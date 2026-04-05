from flask import Flask, jsonify
from cassandra.cluster import Cluster
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

print("🔥 API container started")
print("⏳ Waiting for Cassandra to be ready...")

session = None

# 🔥 INFINITE RETRY (NO CRASH)
while True:
    try:
        print("🔄 Trying to connect to Cassandra...")

        cluster = Cluster(["cassandra"], port=9042)
        session = cluster.connect()

        print("✅ Connected to Cassandra!")

        # 🔥 CREATE KEYSPACE
        session.execute("""
        CREATE KEYSPACE IF NOT EXISTS food_keyspace
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
        """)

        # 🔥 USE KEYSPACE
        session.set_keyspace("food_keyspace")

        # 🔥 CREATE TABLES
        session.execute("""
        CREATE TABLE IF NOT EXISTS food_trends (
            food_item TEXT PRIMARY KEY,
            count INT
        );
        """)

        session.execute("""
        CREATE TABLE IF NOT EXISTS restaurant_load (
            restaurant_id INT PRIMARY KEY,
            order_count INT
        );
        """)

        session.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INT PRIMARY KEY,
            food_item TEXT,
            restaurant_id INT,
            location TEXT
        );
        """)

        print("✅ Cassandra ready + tables ensured!")
        break

    except Exception as e:
        print("❌ Cassandra not ready yet, retrying...", e)
        time.sleep(5)


# 🟢 Home API
@app.route("/")
def home():
    return "Food Delivery Analytics API Running 🚀"


# 🟢 Food Trends API
@app.route("/food_trends")
def food_trends():
    try:
        rows = session.execute("SELECT * FROM food_trends;")

        data = [
            {"food_item": r.food_item, "count": r.count}
            for r in rows
        ]

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🟢 Restaurant Load API
@app.route("/restaurant_load")
def restaurant_load():
    try:
        rows = session.execute("SELECT * FROM restaurant_load;")

        data = [
            {"restaurant_id": r.restaurant_id, "order_count": r.order_count}
            for r in rows
        ]

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/insights")
def insights():
    try:
        # 🔹 FOOD DATA
        food_rows = session.execute("SELECT * FROM food_keyspace.food_trends;")
        food_data = [{"food_item": r.food_item, "count": r.count} for r in food_rows]

        # 🔥 HIGH DEMAND FOOD
        top_food = max(food_data, key=lambda x: x["count"])

        # 🔹 RESTAURANT DATA
        res_rows = session.execute("SELECT * FROM food_keyspace.restaurant_load;")
        res_data = [{"restaurant_id": r.restaurant_id, "order_count": r.order_count} for r in res_rows]

        # ⚠ OVERLOADED RESTAURANT
        overloaded = max(res_data, key=lambda x: x["order_count"])

        # 🔹 CITY-WISE DEMAND (ASSUMING you store location)
        city_rows = session.execute("SELECT location, food_item FROM food_keyspace.orders;")

        city_map = {}

        for r in city_rows:
            city = r.location
            food = r.food_item

            if city not in city_map:
                city_map[city] = {}

            city_map[city][food] = city_map[city].get(food, 0) + 1

        # 📍 TOP FOOD PER CITY
        city_insights = []
        for city, foods in city_map.items():
            top = max(foods, key=foods.get)
            city_insights.append({
                "city": city,
                "top_food": top,
                "count": foods[top]
            })

        # 🔮 SIMPLE PREDICTION (TREND GROWTH)
        predicted_food = sorted(food_data, key=lambda x: x["count"], reverse=True)[0]

        return jsonify({
            "high_demand_food": top_food,
            "overloaded_restaurant": overloaded,
            "city_wise_demand": city_insights,
            "prediction": f"{predicted_food['food_item']} will continue trending"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🚀 Start Flask
if __name__ == "__main__":
    print("🚀 Starting Flask server...")
    app.run(host="0.0.0.0", port=5000)