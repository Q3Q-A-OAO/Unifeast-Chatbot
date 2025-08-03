import os
from dotenv import load_dotenv
from pinecone import Pinecone
from openai import OpenAI

from tqdm.auto import tqdm  # for progress bar
import json

# Load environment variables
load_dotenv()

# Get credentials from .env
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_REGION = os.getenv('PINECONE_REGION')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', 'unifeast-inference')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Set up OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def get_embedding(text):
    """Get embedding from OpenAI"""
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

print("🔄 OpenAI embedding model ready!")

print(f"�� Testing connection to Pinecone index: {PINECONE_INDEX_NAME}")
print(f"Region: {PINECONE_REGION}")

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# Get index info - using official SDK pattern
index = pc.Index(name=PINECONE_INDEX_NAME)

# Get index stats
stats = index.describe_index_stats()

print("✅ Connection successful!")
print(f"Index name: {PINECONE_INDEX_NAME}")
print(f"Dimension: {stats.dimension}")
print(f"Metric: {stats.metric}")
print(f"Total vectors: {stats.total_vector_count}")
print(f"Namespaces: {list(stats.namespaces.keys())}")

# 🚀 ADD YOUR TESTS HERE
print("\n🔍 Ready for your custom tests...")

# Test: Search across both namespaces using official SDK pattern
print("\n" + "="*60)
print("🔍 TEST: SEARCHING ACROSS BOTH NAMESPACES")
print("="*60)

xq = get_embedding("I'm looking for something cold to drink.")

# Query food namespace
print("🍕 Searching food namespace...")
food_results = index.query(
    vector=xq,  # xq is already a list, no need for .tolist()
    top_k=10,
    include_metadata=True,
    filter={
        "_ab_stream": {"$eq": "unifeast_food"},  # Filter to only food items
        "student_price": {"$lte": 3.0},  # This should work now!
    },
    namespace="__default__"  # You can also use namespaces if configured
)

print(f"Found {len(food_results.matches)} food items (under £3):")
print("-" * 40)

for i, match in enumerate(food_results.matches, 1):
    # No more JSON parsing needed - fields are top-level!
    metadata = match.metadata
    
    print(f"🎯 FOOD RESULT #{i}")
    print(f"📊 Semantic Score: {match.score:.4f}")
    print(f"🆔 Pinecone ID: {match.id}")
    print(f"🍕 Dish Name: {metadata.get('dish_name', 'N/A')}")
    print(f"💰 Student Price: £{metadata.get('student_price', 'N/A')}")
    print(f"🏷️  Cuisine Type: {metadata.get('cuisine_type', 'N/A')}")
    print(f"📝 Description: {metadata.get('description', 'N/A')}")
    print(f"🥘 Ingredients: {metadata.get('ingredients', 'N/A')}")
    print(f"⚠️  Allergens: {metadata.get('other_allergens', 'N/A')}")
    print(f"✅ Available: {metadata.get('available', 'N/A')}")
    print("-" * 40)

# # Query restaurant namespace
# print("\n🏪 Searching restaurant namespace...")
# restaurant_results = index.query(
#     vector=xq,  # xq is already a list, no need for .tolist()
#     top_k=3,
#     include_metadata=True,
#     namespace="unifeast_restaurants"
# )

# print(f"Found {len(restaurant_results.matches)} restaurants:")
# print("-" * 40)

# for i, match in enumerate(restaurant_results.matches, 1):
#     flow_doc = json.loads(match.metadata['flow_document'])
    
#     print(f"🎯 RESTAURANT RESULT #{i}")
#     print(f"📊 Semantic Score: {match.score:.4f}")
#     print(f"🆔 Pinecone ID: {match.id}")
#     print(f"🏪 Restaurant Name: {flow_doc.get('restaurant_name', 'N/A')}")
#     print(f"📍 Location: {flow_doc.get('location', 'N/A')}")
#     print(f"📝 Description: {flow_doc.get('description', 'N/A')}")
#     print(f"🏷️  Cuisine Type: {flow_doc.get('cuisine_type', 'N/A')}")
#     print(f"🕒 Opening Hours: {flow_doc.get('opening_hours', 'N/A')}")
#     print(f"📞 Contact: {flow_doc.get('contact', 'N/A')}")
#     print(f"✅ Available: {flow_doc.get('available', 'N/A')}")
#     print("-" * 40)

# print("\n✅ Both namespace searches completed!")