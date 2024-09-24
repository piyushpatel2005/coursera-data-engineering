import argparse
import datetime
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
parser.add_argument(
    "--source_stream", type=str, help="Kinesis data stream name"
)
parser.add_argument(
    "--dest_streams",
    type=str,
    help="JSON Object as string with only two keys: 'USA' and 'International'.",
)


def serialize_datetime(json_obj):
    if isinstance(json_obj, datetime.datetime):
        return json_obj.isoformat()
    raise TypeError("Type not serializable")


class ShardIteratorPair:
    def __init__(self, shard_id, iterator):
        self.shard_id = shard_id
        self.iterator = iterator


def fetch_shards_and_iterators(kinesis, source_stream_name):
    shard_iterators = []
    response_shards = kinesis.list_shards(StreamName=source_stream_name)
    while response_shards["Shards"]:
        for shard in response_shards["Shards"]:
            shard_id = shard["ShardId"]
            itr_response = kinesis.get_shard_iterator(
                StreamName=source_stream_name,
                ShardId=shard_id,
                ShardIteratorType="TRIM_HORIZON",
            )
            shard_itr = ShardIteratorPair(
                shard_id, itr_response["ShardIterator"]
            )
            shard_iterators.append(shard_itr)

        if "NextToken" in response_shards:
            response_shards = kinesis.list_shards(
                StreamName=source_stream_name,
                NextToken=response_shards["NextToken"],
            )
        else:
            break

    return shard_iterators


def transform_stream():
    pass


def poll_shards(kinesis, shard_iterators, kinesis_dest_stream_names):
    while True:
        for shard_itr in shard_iterators:
            try:
                records_response = kinesis.get_records(
                    ShardIterator=shard_itr.iterator, Limit=200
                )
                for record in records_response["Records"]:
                    user_session = json.loads(record["Data"].decode("utf-8"))
                    logging.info(
                        f"Read User Session {user_session} from Shard {shard_itr.shard_id} at position {record['SequenceNumber']}"
                    )

                    ### START CODE HERE ### 
                    # Performing small transformation and putting record into a new kinesis data stream
                    try:
                        # Instructions are in the step 2.2.3.
                        None[
                            "None"
                        ] = None.None.now()

                        # Instructions are in the step 2.2.4.
                        None = None
                        None = None

                        for product in user_session["browse_history"]:
                            # Instructions are in the step 2.2.5.
                            None += None(
                                None["None"]
                            )

                            # Instructions are in the step 2.2.6.
                            if None["None"] == True:
                                None += None(
                                    None["None"]
                                ) 

                        # Instructions are in the step 2.2.7.
                        None[
                            "None"
                        ] = None
                        None[
                            "None"
                        ] = None

                        None["None"] = len(
                            None["None"]
                        )
                        
                        # execute single PutRecord request
                        response = kinesis.put_record(
                            StreamName=kinesis_dest_stream_names["USA"]

                            # Instructions are in the step 2.2.8.
                            if None["None"] == "USA"
                            else None[
                                "International"
                            ],
                    ### END CODE HERE ###
                            Data=json.dumps(
                                user_session, default=serialize_datetime
                            ).encode("utf-8"),
                            PartitionKey=user_session["session_id"],
                        )
                        logging.info(f"Processed User Session {user_session}")
                        logging.info(
                            f"Produced record {response['SequenceNumber']} to Shard {response['ShardId']}\n\n"
                        )
                    
                    
                    except Exception as e:
                        logging.error(
                            {
                                "message": "Error producing record",
                                "error": str(e),
                                "record": user_session,
                            }
                        )

                if records_response["NextShardIterator"]:
                    shard_itr.iterator = records_response["NextShardIterator"]
            except Exception as e:
                logging.error(
                    {"message": "Failed fetching records", "error": str(e)}
                )

        # Adding small delay just to visualization purposes
        time.sleep(2)


def main():
    logging.info("Starting GetRecords Consumer")
    args = parser.parse_args()

    kinesis_source_stream_name = args.source_stream
    kinesis_dest_stream_names = json.loads(args.dest_streams)

    kinesis = boto3.client("kinesis")

    shard_iterators = fetch_shards_and_iterators(
        kinesis, kinesis_source_stream_name
    )
    poll_shards(kinesis, shard_iterators, kinesis_dest_stream_names)


if __name__ == "__main__":
    main()
