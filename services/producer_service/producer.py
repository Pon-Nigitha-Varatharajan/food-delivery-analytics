import json
import time
import random
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    api_version=(3, 4, 0)
)

food_items = ["pizza", "burger", "biryani", "sandwich", "sushi", "tacos", "pasta", "ramen", "noodles", "wrap", "salad", "steak", "curry", "donuts", "waffles", "pancakes", "ice cream", "smoothie", "fried rice", "dumplings"]
locations = ["Coimbatore", "Chennai", "Bangalore", "Mumbai", "Delhi", "Pune", "Hyderabad", "Kochi", "Kolkata", "Ahmedabad"]
restaurants = list(range(1, 31))  # 30 restaurants

print("Starting Kafka Producer...")

while True:
    # 💥 AGENTIC AI CHAOS TRIGGER: Intentionally overload Kitchen-5 (70% probability)
    if random.random() < 0.7:
        target_kitchen = 5
    else:
        target_kitchen = random.choice(restaurants)

    data = {
        "order_id": random.randint(1000, 9999),
        "user_id": random.randint(1, 100),
        "food_item": random.choice(food_items),
        "restaurant_id": target_kitchen,
        "location": random.choice(locations),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    producer.send("food_orders", value=data)
    print("Sent:", data)

    time.sleep(0.05)