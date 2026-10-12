"""Optional distributed Gold aggregation for Spark users."""
from pyspark.sql import SparkSession, functions as F

def main():
    spark = SparkSession.builder.appName("FraudGoldAnalytics").getOrCreate()
    try:
        df = spark.read.parquet("data/silver/transactions.parquet")
        daily = df.withColumn("day_index", (F.col("Time") / 86400).cast("int"))
        result = daily.groupBy("day_index").agg(
            F.count("*").alias("transactions"),
            F.sum("Class").alias("frauds"),
            F.sum("Amount").alias("total_amount")
        )
        result.write.mode("overwrite").parquet("data/gold/spark_daily")
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
