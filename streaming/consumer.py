"""Kafka consumer scoring stream; logs aggregates, not customer PII. Demo implementation."""
import json
import os
import pandas as pd
from confluent_kafka import Consumer, KafkaException
from api.main import load_model
from fraud.features import prepare_features


def main():
    c = Consumer({"bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP", "localhost:9092"), "group.id": "fraud-score-v1", "auto.offset.reset": "earliest", "enable.auto.commit": False})
    c.subscribe([os.getenv("KAFKA_TOPIC", "fraud.transactions")])
    model = load_model()
    print("Scoring stream; Ctrl+C to stop")
    try:
        while True:
            msg = c.poll(1.0)
            if msg is None: continue
            if msg.error(): raise KafkaException(msg.error())
            try:
                values = json.loads(msg.value())
                probability = float(model.predict_proba(prepare_features(pd.DataFrame([values])))[0, 1])
                print(json.dumps({"offset": msg.offset(), "partition": msg.partition(), "fraud_probability": round(probability, 4)}))
            except (ValueError, KeyError, TypeError) as exc:
                print(f"Invalid event at offset {msg.offset()}: {type(exc).__name__}")
            c.commit(msg, asynchronous=False)
    except KeyboardInterrupt:
        pass
    finally:
        c.close()


if __name__ == "__main__": main()
