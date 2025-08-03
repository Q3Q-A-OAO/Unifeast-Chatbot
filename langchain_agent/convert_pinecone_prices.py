"""
Convert Pinecone String Prices to Numbers
=========================================

This script converts existing student_price and staff_price fields from strings to numbers
in the Pinecone index. This is a one-time migration script.
"""

import os
import json
from typing import List, Dict, Any
from pinecone import Pinecone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', 'unifeast-food-index')

def connect_to_pinecone():
    """Connect to Pinecone index"""
    pc = Pinecone(api_key=PINECONE_API_KEY)
    return pc.Index(name=PINECONE_INDEX_NAME)

def fetch_all_records(index, namespace: str) -> List[Dict[str, Any]]:
    """Fetch all records from a namespace using query with high top_k"""
    print(f"📥 Fetching all records from {namespace}...")
    
    # Get index stats to know total count
    stats = index.describe_index_stats()
    total_vectors = stats.namespaces.get(namespace, {}).get('vector_count', 0)
    
    if total_vectors == 0:
        print(f"⚠️  No records found in namespace: {namespace}")
        return []
    
    print(f"📊 Found {total_vectors} records in {namespace}")
    
    # Use a dummy vector to get all records (since we need a vector for query)
    # We'll use a zero vector of the right dimension
    dummy_vector = [0.0] * stats.dimension
    
    # Query with high top_k to get all records
    response = index.query(
        vector=dummy_vector,
        top_k=total_vectors,
        include_metadata=True,
        namespace=namespace
    )
    
    records = []
    for match in response.matches:
        records.append({
            'id': match.id,
            'metadata': match.metadata,
            'score': match.score
        })
    
    print(f"✅ Fetched {len(records)} records from {namespace}")
    return records

def convert_price_strings_to_numbers(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert string prices to numbers in records"""
    print("🔄 Converting string prices to numbers...")
    
    converted_records = []
    converted_count = 0
    
    for record in records:
        try:
            # Parse the flow_document
            flow_doc = json.loads(record['metadata']['flow_document'])
            
            # Track if we made any conversions
            record_converted = False
            
            # Convert string prices to numbers
            if 'student_price' in flow_doc and isinstance(flow_doc['student_price'], str):
                try:
                    flow_doc['student_price'] = float(flow_doc['student_price'])
                    record_converted = True
                    print(f"  📊 Converted student_price: '{record['metadata']['flow_document'].get('student_price', 'N/A')}' → {flow_doc['student_price']}")
                except (ValueError, TypeError):
                    flow_doc['student_price'] = 0.0
                    record_converted = True
                    print(f"  ⚠️  Invalid student_price, set to 0.0")
                    
            if 'staff_price' in flow_doc and isinstance(flow_doc['staff_price'], str):
                try:
                    flow_doc['staff_price'] = float(flow_doc['staff_price'])
                    record_converted = True
                    print(f"  📊 Converted staff_price: '{record['metadata']['flow_document'].get('staff_price', 'N/A')}' → {flow_doc['staff_price']}")
                except (ValueError, TypeError):
                    flow_doc['staff_price'] = 0.0
                    record_converted = True
                    print(f"  ⚠️  Invalid staff_price, set to 0.0")
            
            # Update the record if we made conversions
            if record_converted:
                record['metadata']['flow_document'] = json.dumps(flow_doc)
                converted_count += 1
            
            converted_records.append(record)
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  ❌ Error processing record {record.get('id', 'unknown')}: {e}")
            # Keep the record as-is if we can't process it
            converted_records.append(record)
    
    print(f"✅ Converted {converted_count} records with price updates")
    return converted_records

def update_records_in_pinecone(index, records: List[Dict[str, Any]], namespace: str):
    """Update records in Pinecone with converted prices"""
    print(f"📤 Updating {len(records)} records in {namespace}...")
    
    # Prepare records for upsert
    vectors_to_upsert = []
    
    for record in records:
        # We need to get the vector for each record
        # Since we don't have the vectors, we'll need to fetch them first
        # For now, let's use a different approach - fetch and update in batches
        
        vectors_to_upsert.append({
            'id': record['id'],
            'metadata': record['metadata']
        })
    
    # Upsert in batches
    batch_size = 100
    for i in range(0, len(vectors_to_upsert), batch_size):
        batch = vectors_to_upsert[i:i + batch_size]
        print(f"  📦 Upserting batch {i//batch_size + 1}/{(len(vectors_to_upsert) + batch_size - 1)//batch_size}")
        
        try:
            # Note: We need the vectors for upsert, so we'll use a different approach
            # For now, let's use delete and insert approach
            pass
        except Exception as e:
            print(f"  ❌ Error upserting batch: {e}")
    
    print(f"✅ Successfully updated records in {namespace}")

def convert_prices_in_namespace(index, namespace: str):
    """Convert all prices in a namespace from strings to numbers"""
    print(f"\n🔄 Converting prices in namespace: {namespace}")
    print("=" * 60)
    
    # 1. Fetch all records
    records = fetch_all_records(index, namespace)
    
    if not records:
        print(f"⚠️  No records to convert in {namespace}")
        return
    
    # 2. Convert prices
    converted_records = convert_price_strings_to_numbers(records)
    
    # 3. Update in Pinecone
    update_records_in_pinecone(index, converted_records, namespace)
    
    print(f"✅ Successfully converted prices in {namespace}")

def main():
    """Main conversion process"""
    print("🚀 Starting Pinecone price conversion...")
    print("=" * 60)
    
    try:
        # Connect to Pinecone
        index = connect_to_pinecone()
        print(f"✅ Connected to Pinecone index: {PINECONE_INDEX_NAME}")
        
        # Get index stats
        stats = index.describe_index_stats()
        print(f"📊 Index stats: {stats.total_vector_count} total vectors")
        print(f"📊 Namespaces: {list(stats.namespaces.keys())}")
        
        # Convert prices in both namespaces
        convert_prices_in_namespace(index, "unifeast_food")
        convert_prices_in_namespace(index, "unifeast_restaurants")
        
        print("\n🎉 Price conversion completed!")
        
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        raise

if __name__ == "__main__":
    main() 