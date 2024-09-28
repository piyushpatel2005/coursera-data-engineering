import json
import logging
import sys
import time
import boto3
from botocore.config import Config

logging.basicConfig(
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("consumer.log"),
        logging.StreamHandler(sys.stdout),
    ],
)


my_config = Config(
    region_name = 'us-east-1',
    signature_version = 'v4',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)

class ShardIteratorPair:
    def __init__(self, shard_id, iterator):
        self.shard_id = shard_id
        self.iterator = iterator


def fetch_shards_and_iterators(kinesis, stream_name):
    shard_iterators = []
    response_shards = kinesis.list_shards(StreamName=stream_name)
    while response_shards["Shards"]:
        for shard in response_shards["Shards"]:
            shard_id = shard["ShardId"]
            itr_response = kinesis.get_shard_iterator(
                StreamName=stream_name,
                ShardId=shard_id,
                ShardIteratorType="TRIM_HORIZON",
            )
            shard_itr = ShardIteratorPair(
                shard_id, itr_response["ShardIterator"]
            )
            shard_iterators.append(shard_itr)

        if "NextToken" in response_shards:
            response_shards = kinesis.list_shards(
                StreamName=stream_name, NextToken=response_shards["NextToken"]
            )
        else:
            break

    return shard_iterators


def poll_shards(kinesis, shard_iterators):
    while True:
        for shard_itr in shard_iterators:
            try:
                records_response = kinesis.get_records(
                    ShardIterator=shard_itr.iterator, Limit=200
                )
                for record in records_response["Records"]:
                    order = json.loads(record["Data"].decode("utf-8"))
                    logging.info(
                        f"Read Order {order} from Shard {shard_itr.shard_id} at position {record['SequenceNumber']}"
                    )

                if records_response["NextShardIterator"]:
                    shard_itr.iterator = records_response["NextShardIterator"]
            except Exception as e:
                logging.error(
                    {"message": "Failed fetching records", "error": str(e)}
                )

        time.sleep(1)


def main(args):
    logging.info("Starting GetRecords Consumer")

    if len(args) < 2:
        print("Usage: python consumer.py <kinesis_stream_name>")
        sys.exit(1)

    kinesis_stream_name = args[1]
    kinesis = boto3.client("kinesis", config=my_config)

    shard_iterators = fetch_shards_and_iterators(kinesis, kinesis_stream_name)
    poll_shards(kinesis, shard_iterators)


if __name__ == "__main__":
    main(sys.argv)
