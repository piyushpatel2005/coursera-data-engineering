import argparse
import json
import logging
import sys
import time

import boto3

logging.basicConfig(
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("consumer.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

parser = argparse.ArgumentParser()
parser.add_argument("--stream", type=str, help="Kinesis data stream name")


class ShardIteratorPair:
    """This class represents a pair consisting of a shard ID and its
    corresponding shard iterator. It's used to store information about shards
    and their iterators.
    """

    def __init__(self, shard_id, iterator):
        self.shard_id = shard_id
        self.iterator = iterator


def fetch_shards_and_iterators(kinesis, stream_name):
    """This function retrieves a list of shard iterators for the specified
    Kinesis stream. It iterates over all shards in the stream, retrieves
    their iterators using "TRIM_HORIZON" as the iterator type (which starts
    reading from the oldest available data in the shard), and stores the shard
    ID and iterator in a list of ShardIteratorPairs. It handles pagination if
    the number of shards exceeds the limit returned by the API.

    Args:
        kinesis (boto3 client): Boto3 client for kinesis resources
        stream_name (str): Kinesis data stream name

    Returns:
        List: Pair of ShardId and corresponding Iterator
    """

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
    """This function continuously polls the shards for data. It iterates
    over the list of shard iterators, fetching records from each shard using
    the respective iterator. For each record retrieved, it logs the order
    data along with the shard ID and sequence number. It updates the shard
    iterator to the next iterator if available.

    Args:
        kinesis (boto3 client): Boto3 client for kinesis resources
        shard_iterators (List): Pair of ShardId and corresponding Iterator
    """
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


def main():
    logging.info("Starting GetRecords Consumer")
    args = parser.parse_args()

    kinesis_stream_name = args.stream

    kinesis = boto3.client("kinesis")

    shard_iterators = fetch_shards_and_iterators(kinesis, kinesis_stream_name)
    poll_shards(kinesis, shard_iterators)


if __name__ == "__main__":
    main()
