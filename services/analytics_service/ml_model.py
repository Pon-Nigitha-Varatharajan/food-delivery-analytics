from pyspark.sql import SparkSession
import json
import subprocess

# Spark session
spark = SparkSession.builder.appName("ML Model - Trend Prediction").getOrCreate()

# Kafka consumer
process = subprocess.Popen(
    ["docker", "exec", "kafka", "kafka-console-consumer",
     "--topic", "food_orders",
     "--bootstrap-server", "localhost:9092"],
    stdout=subprocess.PIPE,
    text=True
)

data_list = []

print("Collecting data for ML model...\n")

# Collect data
for i in range(30):
    line = process.stdout.readline()
    if line:
        data = json.loads(line.strip())
        data_list.append((data["food_item"],))

# Create DataFrame
df = spark.createDataFrame(data_list, ["food_item"])

# 🔹 ML Logic (trend detection)
trend_df = df.groupBy("food_item").count()

# Sort by highest demand
top_items = trend_df.orderBy("count", ascending=False)

print("\n🔥 Top Trending Food Items:\n")

top_items.show()