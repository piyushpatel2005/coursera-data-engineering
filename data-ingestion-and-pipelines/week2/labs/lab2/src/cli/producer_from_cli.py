"""
Producer app writing single session records at a time to a Kinesis Data Stream using
the PutRecord API of the Python SDK.

The globally unique session ID of each record is used as the partition key which ensures
session records will be equally distributed across the shard of the stream.
"""
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
        logging.FileHandler("producer.log"),
        logging.StreamHandler(sys.stdout),
    ],
)


parser = argparse.ArgumentParser(
    description="Parse JSON object from command line"
)
parser.add_argument("--stream", type=str, help="Kinesis data stream name")
parser.add_argument("--json_string", type=str, help="JSON object as a string")


def main():
    logging.info("Starting PutRecord Producer")
    args = parser.parse_args()

    kinesis_stream_name = args.stream
    data_record = json.loads(args.json_string)

    kinesis = boto3.client("kinesis")

    try:
        # execute single PutRecord request
        response = kinesis.put_record(
            StreamName=kinesis_stream_name,
            Data=json.dumps(data_record).encode("utf-8"),
            PartitionKey=data_record["session_id"],
        )
        logging.info(
            f"Produced record {response['SequenceNumber']} to Shard {response['ShardId']}"
        )
    except Exception as e:
        logging.error(
            {
                "message": "Error producing record",
                "error": str(e),
                "record": data_record,
            }
        )


if __name__ == "__main__":
    main()
