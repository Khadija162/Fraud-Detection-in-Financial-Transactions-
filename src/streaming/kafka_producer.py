"""Optional adapter: replay approved offline CSV events into Kafka."""
import argparse
import json
from pathlib import Path
import pandas as pd


def replay(path: Path, broker: str, topic: str, limit: int):
    from confluent_kafka import Producer
    producer = Producer({"bootstrap.servers": broker, "acks": "all"})
    df = pd.read_csv(path, nrows=limit)
    for idx, row in df.iterrows():
        payload = {"event_id": str(idx), "amount": float(row["Amount"]),
                   "event_time": float(row["Time"])}
        producer.produce(topic, key=str(idx), value=json.dumps(payload))
        producer.poll(0)
    remaining = producer.flush(30)
    if remaining:
        raise RuntimeError(f"{remaining} undelivered events")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--path", default="data/raw/creditcard.csv")
    p.add_argument("--broker", default="localhost:9092")
    p.add_argument("--topic", default="fraud.transactions")
    p.add_argument("--limit", type=int, default=1000)
    args = p.parse_args()
    replay(Path(args.path), args.broker, args.topic, args.limit)
