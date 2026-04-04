#!/bin/bash

echo "🚀 Starting Full System..."
source venv/bin/activate
# Start Docker services
echo "📦 Starting Docker (Kafka + Cassandra + API)..."
cd docker
docker-compose up -d --build

echo "⏳ Waiting for services to initialize..."
sleep 30

# Start Producer
echo "📡 Starting Producer..."
cd ../services/producer_service
python3 producer.py &

# Start ETL
echo "⚙️ Starting ETL Pipeline..."
cd ../streaming_service
python3 etl.py &

echo "✅ System is running!"
echo "🌐 API: http://localhost:5001"
echo "📊 Frontend: http://localhost:8000"