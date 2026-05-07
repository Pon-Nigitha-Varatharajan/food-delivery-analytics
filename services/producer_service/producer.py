import json
import time
import random
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

food_items = ["pizza", "burger", "biryani", "sandwich", "sushi", "tacos", "pasta", "ramen", "noodles", "wrap", "salad", "steak", "curry", "donuts", "waffles", "pancakes", "ice cream", "smoothie", "fried rice", "dumplings"]

locations = ["Coimbatore", "Chennai", "Bangalore", "Mumbai", "Delhi", "Pune", "Hyderabad", "Kochi", "Kolkata", "Ahmedabad"]

restaurants = list(range(1, 31))

print("🔥 Starting Kafka Producer with BIAS...")

while True:
    
    # 🔥 BIAS LOGIC (IMPORTANT)
    if random.random() < 0.7:
        restaurant = 5   # 🎯 overload this kitchen
    else:
        restaurant = random.choice(restaurants)

    data = {
        "order_id": random.randint(1000, 9999),
        "user_id": random.randint(1, 100),
        "food_item": random.choice(food_items),
        "restaurant_id": restaurant,
        "location": random.choice(locations),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    producer.send("food_orders", value=data)
    print("Sent:", data)

    time.sleep(0.05)