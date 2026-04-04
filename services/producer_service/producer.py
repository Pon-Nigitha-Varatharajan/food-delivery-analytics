import json
import time
import random
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

food_items = ["pizza", "burger", "biryani", "sandwich"]
locations = ["Coimbatore", "Chennai", "Bangalore"]
restaurants = [1, 2, 3, 4, 5]

print("Starting Kafka Producer...")

while True:
    data = {
        "order_id": random.randint(1000, 9999),
        "user_id": random.randint(1, 100),
        "food_item": random.choice(food_items),
        "restaurant_id": random.choice(restaurants),
        "location": random.choice(locations),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    producer.send("food_orders", value=data)
    print("Sent:", data)

    time.sleep(1)