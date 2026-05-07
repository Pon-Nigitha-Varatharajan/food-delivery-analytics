from pyspark.sql import SparkSession
import json
import subprocess

# 🔥 Spark setup (for syllabus requirement)
spark = SparkSession.builder.appName("ETL Pipeline").getOrCreate()
sc = spark.sparkContext

# 🔥 In-memory aggregations
food_counts = {}
restaurant_counts = {}
city_food_counts = {}   # 🔥 NEW (city + food)

# 🔥 Kafka consumer (Docker Kafka)
process = subprocess.Popen(
    [
        "docker", "exec", "kafka", "kafka-console-consumer",
        "--topic", "food_orders",
        "--bootstrap-server", "localhost:9092"
    ],
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
        location = data.get("location", "unknown").strip()

        if not food:
            continue

        # =========================
        # 🔥 TRANSFORM (CORE LOGIC)
        # =========================

        # 1️⃣ Food count
        food_counts[food] = food_counts.get(food, 0) + 1

        # 2️⃣ Restaurant load
        restaurant_counts[restaurant] = restaurant_counts.get(restaurant, 0) + 1

        # 3️⃣ City-wise food demand 🔥 NEW
        city_key = (location, food)
        city_food_counts[city_key] = city_food_counts.get(city_key, 0) + 1

        # =========================
        # 🔥 LOAD (CASSANDRA)
        # =========================

        food_count = food_counts[food]
        rest_count = restaurant_counts[restaurant]
        city_count = city_food_counts[city_key]

        # 🔹 Queries (NO semicolon ❗)
        query1 = f"""
        INSERT INTO food_keyspace.food_trends (food_item, count)
        VALUES ('{food}', {food_count})
        """

        query2 = f"""
        INSERT INTO food_keyspace.restaurant_load (restaurant_id, order_count)
        VALUES ({restaurant}, {rest_count})
        """

        query3 = f"""
        INSERT INTO food_keyspace.orders (order_id, food_item, restaurant_id, location)
        VALUES ({order_id}, '{food}', {restaurant}, '{location}')
        """

        # 🔥 NEW TABLE → city demand
        query4 = f"""
        INSERT INTO food_keyspace.city_demand (location, food_item, count)
        VALUES ('{location}', '{food}', {city_count})
        """

        # 🔥 Execute all queries
        queries = [query1, query2, query3, query4]

        for i, q in enumerate(queries, start=1):
            res = subprocess.run(
                ["docker", "exec", "cassandra", "cqlsh", "-e", q],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if res.stderr:
                print(f"❌ Query {i} Error:", res.stderr)

        # =========================
        # 🔥 DEBUG LOG
        # =========================
        print(
            f"✅ Food: ({food}, {food_count}) | "
            f"Restaurant: ({restaurant}, {rest_count}) | "
            f"City: ({location}, {city_count})"
        )

    except Exception as e:
        print("❌ Error:", e)