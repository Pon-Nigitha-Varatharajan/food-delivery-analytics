from pyspark.sql import SparkSession
import json
import subprocess

# 🔥 Spark setup
spark = SparkSession.builder.appName("ETL Pipeline").getOrCreate()
sc = spark.sparkContext

# 🔥 In-memory aggregation
food_counts = {}
restaurant_counts = {}

# 🔥 Kafka consumer
process = subprocess.Popen(
    ["/opt/homebrew/opt/kafka/bin/kafka-console-consumer",
     "--topic", "food_orders",
     "--bootstrap-server", "localhost:9092",
     "--from-beginning"],
    stdout=subprocess.PIPE,
    text=True
)

print("🚀 Starting ETL Pipeline...\n")

for line in process.stdout:
    try:
        data = json.loads(line.strip())

        # 🔹 Validate data
        if not data.get("food_item") or not data.get("restaurant_id"):
            continue

        # 🔹 Extract fields
        food = data["food_item"].lower().strip()
        restaurant = int(data["restaurant_id"])
        order_id = int(data.get("order_id", 0))
        location = data.get("location", "unknown")

        # 🔹 Filter valid items
        valid_items = ["pizza", "burger", "biryani", "sandwich"]
        if food not in valid_items:
            continue

        # 🔥 UPDATE COUNTS
        food_counts[food] = food_counts.get(food, 0) + 1
        restaurant_counts[restaurant] = restaurant_counts.get(restaurant, 0) + 1

        food_count = food_counts[food]
        rest_count = restaurant_counts[restaurant]

        # 🔹 Cassandra Queries

        # 1️⃣ Food Trends
        query1 = f"INSERT INTO food_keyspace.food_trends (food_item, count) VALUES ('{food}', {food_count})"

        # 2️⃣ Restaurant Load
        query2 = f"INSERT INTO food_keyspace.restaurant_load (restaurant_id, order_count) VALUES ({restaurant}, {rest_count})"

        # 3️⃣ Raw Orders (🔥 NEW - IMPORTANT)
        query3 = f"INSERT INTO food_keyspace.orders (order_id, food_item, restaurant_id, location) VALUES ({order_id}, '{food}', {restaurant}, '{location}')"

        # 🔥 Execute queries
        res1 = subprocess.run(
            ["docker", "exec", "cassandra", "cqlsh", "-e", query1],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        res2 = subprocess.run(
            ["docker", "exec", "cassandra", "cqlsh", "-e", query2],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        res3 = subprocess.run(
            ["docker", "exec", "cassandra", "cqlsh", "-e", query3],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # 🔹 Error handling
        if res1.stderr:
            print("❌ Food Insert Error:", res1.stderr)

        if res2.stderr:
            print("❌ Restaurant Insert Error:", res2.stderr)

        if res3.stderr:
            print("❌ Orders Insert Error:", res3.stderr)

        # 🔹 Debug output
        print(f"✅ Updated → Food: ({food}, {food_count}), Restaurant: ({restaurant}, {rest_count}), Location: {location}")

    except Exception as e:
        print("❌ Error:", e)