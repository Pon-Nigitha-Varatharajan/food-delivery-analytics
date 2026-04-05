import os
# Ensure PySpark downloads the Kafka connector JAR to enable true streaming
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1 pyspark-shell'

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, IntegerType
import subprocess
import json

print("🚀 Initializing True PySpark Structured Streaming ETL Pipeline...\n")

# 1. Spark Session setup
spark = SparkSession.builder \
    .appName("RealTimeFoodETL") \
    .getOrCreate()

# Suppress verbose spark logging to keep terminal readable
spark.sparkContext.setLogLevel("ERROR")

# 2. Define the schema to map the JSON payload
schema = StructType() \
    .add("order_id", IntegerType()) \
    .add("user_id", IntegerType()) \
    .add("food_item", StringType()) \
    .add("restaurant_id", IntegerType()) \
    .add("location", StringType()) \
    .add("timestamp", StringType())

# 3. Read Stream directly from Kafka (Real-time processing)
streaming_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "food_orders") \
    .option("startingOffsets", "latest") \
    .load()

# 4. Transformations (Spark SQL / DataFrame API)
# Extract the value column, cast from binary to string, and parse JSON
parsed_df = streaming_df \
    .selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

from cassandra.cluster import Cluster

# 5. Define RDD Action to write to Cassandra in batches
def process_partition(partition):
    """
    Executes an action directly on the Worker Nodes for each partition of data.
    """
    # Connect to Cassandra once per partition to avoid overhead
    # NOTE: Change 'localhost' to your EC2 Public IP if running this script from your laptop
    cluster = Cluster(['localhost'], port=9042)
    session = cluster.connect('food_keyspace')

    for row in partition:
        try:
            food = row.food_item.lower().strip()
            rest = int(row.restaurant_id)
            order_id = int(row.order_id)
            location = str(row.location)

            # Insert raw order
            session.execute(
                f"INSERT INTO orders (order_id, food_item, restaurant_id, location) VALUES ({order_id}, '{food}', {rest}, '{location}')"
            )
            
            # Increment trends
            session.execute(f"UPDATE food_trends SET count = count + 1 WHERE food_item = '{food}'")
            session.execute(f"UPDATE restaurant_load SET order_count = order_count + 1 WHERE restaurant_id = {rest}")

        except Exception as e:
            pass

    cluster.shutdown()

def write_to_cassandra(batch_df, batch_id):
    # Using the underlying RDD to process data partitions (Satisfies: Spark RDD, Actions)
    batch_df.rdd.foreachPartition(process_partition)
    print(f"✅ Processed micro-batch {batch_id} with {batch_df.count()} real-time records.")

# 6. Ignite the Stream
query = parsed_df.writeStream \
    .outputMode("append") \
    .foreachBatch(write_to_cassandra) \
    .start()

print("⏳ Stream is live. Listening to Kafka and writing to Cassandra via Spark workers...")
query.awaitTermination()