from pyspark.sql import SparkSession
from kafka import KafkaConsumer
from cassandra.cluster import Cluster
import json

# 🔥 Spark setup
spark = SparkSession.builder.appName("ETL Pipeline").getOrCreate()
print("🚀 Initializing ETL Pipeline...\n")

# Connect natively to AWS Cassandra (Bypasses PySpark Worker Connection Bugs)
print("⏳ Connecting to AWS Cassandra...")
cluster = Cluster(['56.228.7.202'], port=9042)
session = cluster.connect('food_keyspace')
print("✅ Connected to Cassandra!")

# Initialize Local Kafka Consumer
print("⏳ Connecting to Local Kafka...")
consumer = KafkaConsumer(
    'food_orders',
    bootstrap_servers=['localhost:9092'],
    api_version=(3, 4, 0),
    auto_offset_reset='latest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)
print("✅ Connected! Listening for real-time orders...\n")

# Local Aggregation State
food_counts = {}
restaurant_counts = {}

for message in consumer:
    data = message.value
    
    # Extract fields
    food = data.get("food_item", "unknown").lower().strip()
    restaurant = int(data.get("restaurant_id", 0))
    order_id = int(data.get("order_id", 0))
    location = data.get("location", "unknown")

    # Increment aggregations
    food_counts[food] = food_counts.get(food, 0) + 1
    restaurant_counts[restaurant] = restaurant_counts.get(restaurant, 0) + 1

    try:
        # Stream into Cassandra
        session.execute(
            "INSERT INTO food_trends (food_item, count) VALUES (%s, %s)",
            (food, food_counts[food])
        )
        session.execute(
            "INSERT INTO restaurant_load (restaurant_id, order_count) VALUES (%s, %s)",
            (restaurant, restaurant_counts[restaurant])
        )
        session.execute(
            "INSERT INTO orders (order_id, food_item, restaurant_id, location) VALUES (%s, %s, %s, %s)",
            (order_id, food, restaurant, location)
        )
        
        print(f"📦 Successfully Processed -> Order {order_id} | {food.capitalize()} in {location}")
        
    except Exception as e:
        print("❌ Error Syncing to DB:", e)