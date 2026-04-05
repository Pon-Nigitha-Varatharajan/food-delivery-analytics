from pyspark.sql import SparkSession
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.clustering import KMeans
import json
import subprocess

print("🚀 Starting PySpark Machine Learning Job (K-Means Clustering)...\n")

# 1. Spark session
spark = SparkSession.builder.appName("ML Model - Market Segmentation").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

# 2. Consume Data from Kafka for training
process = subprocess.Popen(
    ["docker", "exec", "kafka", "kafka-console-consumer",
     "--topic", "food_orders",
     "--bootstrap-server", "localhost:9092", "--max-messages", "150"],
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True
)

data_list = []
print("⏳ Collecting 150 real-time records to train the model...")

while len(data_list) < 150:
    line = process.stdout.readline()
    if line:
        try:
            data = json.loads(line.strip())
            data_list.append((data["food_item"], data["location"], int(data["restaurant_id"])))
        except:
            pass

# 3. Create DataFrame (Spark SQL usage)
df = spark.createDataFrame(data_list, ["food_item", "location", "restaurant_id"])

# 4. Data Mapping & Integration (ML Feature Engineering)
# Convert Categorical Strings to Numeric Indices
food_indexer = StringIndexer(inputCol="food_item", outputCol="food_index")
df = food_indexer.fit(df).transform(df)

loc_indexer = StringIndexer(inputCol="location", outputCol="loc_index")
df = loc_indexer.fit(df).transform(df)

# Assemble feature vector
assembler = VectorAssembler(inputCols=["food_index", "loc_index", "restaurant_id"], outputCol="features")
feature_df = assembler.transform(df)

# 5. Apply PySpark ML Clustering (KMeans)
print("\n🧠 Training K-Means Cluster Model for Targeted Geographic Marketing...")
kmeans = KMeans(k=3, seed=42) # Creating 3 market segments
model = kmeans.fit(feature_df)

# 6. Make Predictions & Verify
predictions = model.transform(feature_df)
print("\n📊 Segmented Predictions Result (Sample):")
predictions.select("food_item", "location", "prediction").show(10, truncate=False)

print("\n✅ Successfully integrated PySpark ML Libraries. Model training complete.")