from pyspark.sql import SparkSession
import json
import subprocess

# Spark session
spark = SparkSession.builder.appName("Spark SQL Analytics").getOrCreate()

# Kafka consumer
process = subprocess.Popen(
    ["/opt/homebrew/opt/kafka/bin/kafka-console-consumer",
     "--topic", "food_orders",
     "--bootstrap-server", "localhost:9092"],
    stdout=subprocess.PIPE,
    text=True
)

data_list = []

print("Reading data for Spark SQL...\n")

# Collect some data (batch for SQL)
for i in range(20):  # take 20 records
    line = process.stdout.readline()
    if line:
        data = json.loads(line.strip())
        data_list.append((data["food_item"],))

# Create DataFrame
df = spark.createDataFrame(data_list, ["food_item"])

# Create temporary SQL table
df.createOrReplaceTempView("orders")

# 🔹 SQL Query
result = spark.sql("""
    SELECT food_item, COUNT(*) as count
    FROM orders
    GROUP BY food_item
""")

# Show result
result.show()