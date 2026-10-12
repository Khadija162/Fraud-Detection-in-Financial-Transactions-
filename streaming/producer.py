"""Publish a sample of PaySim rows to Kafka-compatible Redpanda."""
import argparse
import json
import os
import pandas as pd
from confluent_kafka import Producer
from fraud.features import FEATURES


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True)
    p.add_argument("--rows", type=int, default=200)
    args = p.parse_args()
    producer = Producer({"bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP", "localhost:9092"), "acks": "all"})
    sent = 0
    for chunk in pd.read_csv(args.csv, usecols=FEATURES, chunksize=min(max(args.rows,1), 10000)):
        for row in chunk.head(max(0,args.rows-sent)).to_dict(orient="records"):
            producer.produce(os.getenv("KAFKA_TOPIC", "fraud.transactions"), value=json.dumps(row, allow_nan=False, default=str))
            sent += 1
        if sent >= args.rows:
            break
    remaining = producer.flush(30)
    if remaining:
        raise RuntimeError(f"{remaining} messages not confirmed delivered")
    print(f"Published {sent} transactions")


if __name__ == "__main__":
    main()
