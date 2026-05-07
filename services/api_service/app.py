from flask import Flask, jsonify
from cassandra.cluster import Cluster
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

print("🔥 API container started")
print("⏳ Waiting for Cassandra to be ready...")

session = None

# 🔥 RETRY CONNECTION
while True:
    try:
        print("🔄 Connecting to Cassandra...")

        cluster = Cluster(["cassandra"], port=9042)
        session = cluster.connect()

        print("✅ Connected!")

        # 🔹 Create keyspace
        session.execute("""
        CREATE KEYSPACE IF NOT EXISTS food_keyspace
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
        """)

        session.set_keyspace("food_keyspace")

        # 🔹 Tables
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

        # 🔥 NEW TABLE
        session.execute("""
        CREATE TABLE IF NOT EXISTS city_demand (
            location TEXT,
            food_item TEXT,
            count INT,
            PRIMARY KEY (location, food_item)
        );
        """)

        print("✅ Tables ready!")
        break

    except Exception as e:
        print("❌ Retry Cassandra...", e)
        time.sleep(5)


# 🟢 HOME
@app.route("/")
def home():
    return "🚀 Food Delivery Analytics API Running"


# 🟢 FOOD TRENDS
@app.route("/food_trends")
def food_trends():
    try:
        rows = session.execute("SELECT * FROM food_trends;")

        return jsonify([
            {"food_item": r.food_item, "count": r.count}
            for r in rows
        ])

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🟢 RESTAURANT LOAD
@app.route("/restaurant_load")
def restaurant_load():
    try:
        rows = session.execute("SELECT * FROM restaurant_load;")

        return jsonify([
            {"restaurant_id": r.restaurant_id, "order_count": r.order_count}
            for r in rows
        ])

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🟢 CITY DEMAND
@app.route("/city_demand")
def city_demand():
    try:
        rows = session.execute("SELECT * FROM city_demand;")

        return jsonify([
            {
                "city": r.location,
                "food_item": r.food_item,
                "count": r.count
            }
            for r in rows
        ])

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🟢 INSIGHTS (🔥 CORE INTELLIGENCE + AGENTIC AI)
@app.route("/insights")
def insights():
    try:
        # 🔹 FOOD DATA
        food_rows = list(session.execute("SELECT * FROM food_trends;"))

        # 🔹 RESTAURANT DATA
        res_rows = list(session.execute("SELECT * FROM restaurant_load;"))

        # 🔹 CITY DATA
        city_rows = list(session.execute("SELECT * FROM city_demand;"))

        # ❗ Safety checks
        if not food_rows or not res_rows:
            return jsonify({
                "high_demand_food": None,
                "overloaded_restaurant": None,
                "city_wise_demand": [],
                "prediction": "No data yet",
                "load_balancing": None
            })

        # 🔥 HIGH DEMAND FOOD
        top_food = max(food_rows, key=lambda x: x.count)

        # 🔥 OVERLOADED RESTAURANT
        top_rest = max(res_rows, key=lambda x: x.order_count)

        # 🤖 LOAD BALANCING AGENT (NEW)
        res_data = [
            {"restaurant_id": r.restaurant_id, "order_count": r.order_count}
            for r in res_rows
        ]

        sorted_restaurants = sorted(res_data, key=lambda x: x["order_count"], reverse=True)

        overloaded = sorted_restaurants[0]
        underloaded = sorted(res_data, key=lambda x: x["order_count"])[0]

        threshold = 50
        load_balance_action = None

        if overloaded["order_count"] > threshold:
            load_balance_action = {
                "from": overloaded["restaurant_id"],
                "to": underloaded["restaurant_id"],
                "message": f"Redirect orders from Kitchen-{overloaded['restaurant_id']} to Kitchen-{underloaded['restaurant_id']}"
            }

        # 🔥 CITY-WISE ANALYTICS
        city_map = {}

        for row in city_rows:
            city = row.location

            if city not in city_map:
                city_map[city] = []

            city_map[city].append(row)

        city_result = []
        for city, items in city_map.items():
            top_item = max(items, key=lambda x: x.count)

            city_result.append({
                "city": city,
                "top_food": top_item.food_item,
                "count": top_item.count
            })

        # 🔮 PREDICTION
        prediction = f"{top_food.food_item} will continue trending 🔥"

        return jsonify({
            "high_demand_food": {
                "food_item": top_food.food_item,
                "count": top_food.count
            },
            "overloaded_restaurant": {
                "restaurant_id": top_rest.restaurant_id,
                "order_count": top_rest.order_count
            },
            "city_wise_demand": city_result,
            "prediction": prediction,
            "load_balancing": load_balance_action   # 👈 NEW AGENT OUTPUT
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🚀 RUN SERVER
if __name__ == "__main__":
    print("🚀 Starting Flask API...")
    app.run(host="0.0.0.0", port=5000)