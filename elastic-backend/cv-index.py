import pandas as pd
from elasticsearch import Elasticsearch, helpers
import json

CSV_FILE = "cv-valid-dev.csv"
INDEX_NAME = "cv-transcriptions"

# Connect to Elasticsearch
es = Elasticsearch("http://localhost:9200")

# Read CSV file
df = pd.read_csv(CSV_FILE)

# Replace NaN values with an empty string to avoid invalid tokens
df = df.fillna("")

# Delete existing index to ensure the new mapping is used
if es.indices.exists(index=INDEX_NAME):
    print(f"Deleting existing index: {INDEX_NAME}")
    es.indices.delete(index=INDEX_NAME)

# Create index with the desired mapping (age is a keyword for categorical data)
print(f"Creating index: {INDEX_NAME}")
es.indices.create(index=INDEX_NAME, body={
    "settings": {"number_of_shards": 1, "number_of_replicas": 0},
    "mappings": {
        "properties": {
            "generated_text": {"type": "text"},
            "duration": {"type": "keyword"},
            "age": {"type": "keyword"},
            "gender": {"type": "keyword"},
            "accent": {"type": "keyword"}
        }
    }
})

def generate_actions(df):
    for i, row in df.iterrows():
        doc = row.to_dict()
        yield {
            "_index": INDEX_NAME,
            "_id": i,  # use row index as id for clarity
            "_source": doc
        }

print("Starting bulk indexing...")
success, failed = helpers.bulk(es, generate_actions(df), raise_on_error=False)

if failed:
    print("Indexing encountered errors:")
    for err in failed:
        print(json.dumps(err, indent=2))
else:
    print("Indexing complete.")
