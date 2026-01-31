"""
OBJECTIVE:
Learn how to use Pinecone - a managed vector database with metadata filtering.

CONCEPTS:
- Vector Database: Like FAISS, but in the cloud with extra features
- Metadata Filtering: Search vectors AND filter by categories
- Managed Service: No need to maintain servers or indexes yourself
- Hybrid Search: Combine semantic similarity + exact metadata matches

WHY THIS MATTERS:
FAISS finds similar vectors, but can't filter by metadata.
Pinecone can do: "Find similar documents that are ALSO from US AND Healthcare"

Example: 
  Query: "insurance benefits"
  Filter: region=US AND category=Healthcare
  Result: Only US healthcare docs, ranked by similarity
"""

import json
import numpy as np
import os
from pathlib import Path
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import time

# ============================================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================================
print("\n🔑 Loading API keys...")

load_dotenv()

pinecone_api_key = os.getenv('PINECONE_API_KEY')

if not pinecone_api_key or pinecone_api_key == 'your_pinecone_api_key_here':
    print("WARNING: Pinecone API key not found!")
    print("   Please:")
    print("   1. Copy .env.template to .env")
    print("   2. Add your Pinecone API key to .env")
    print("   3. Get free key from: https://www.pinecone.io/")
    print("\n   Continuing in demo mode (showing concepts without actual upload)...")
    use_pinecone = False
else:
    print("Pinecone API key loaded")
    use_pinecone = True

# ============================================================================
# LOAD DATA
# ============================================================================
print("\n Loading documents and embeddings...")

with open('data/sample_documents.json', 'r', encoding='utf-8') as f:
    documents = json.load(f)

embeddings = np.load('models/embeddings.npy')

print(f"Loaded {len(documents)} documents")
print(f"Loaded {len(embeddings)} embeddings")

# ============================================================================
# CONCEPT: What is Pinecone?
# ============================================================================
print("\n" + "="*60)
print("CONCEPT: Pinecone vs FAISS")
print("="*60)
print("""
FAISS (Local):
✓ Fast vector search
✓ Runs on your machine
✗ No built-in metadata filtering
✗ You manage the index
✗ Limited to one machine's RAM

Pinecone (Cloud):
✓ Fast vector search
✓ Cloud-hosted (managed for you)
✓ Metadata filtering built-in!
✓ Automatically scales
✓ Multi-user access

Example Use Case:
  "Find documents similar to 'health insurance' 
   BUT ONLY from US 
   AND ONLY category Healthcare
   AND ONLY topic Medicare"

This hybrid search (vector + filters) is Pinecone's strength!
""")

# ============================================================================
# SETUP PINECONE
# ============================================================================
if use_pinecone:
    print("\n" + "="*60)
    print("Connecting to Pinecone...")
    print("="*60)
    
    try:
        # Initialize Pinecone
        pc = Pinecone(api_key=pinecone_api_key)
        
        print("✓ Connected to Pinecone")
        
        # Define index name
        index_name = "lab4-hybrid-rag"
        
        # Check if index exists
        existing_indexes = pc.list_indexes()
        index_exists = any(idx['name'] == index_name for idx in existing_indexes)
        
        if index_exists:
            print(f"\n Index '{index_name}' already exists")
            print("   Deleting old index to start fresh...")
            pc.delete_index(index_name)
            time.sleep(1)  # Wait for deletion
        
        # ============================================================================
        # CREATE PINECONE INDEX
        # ============================================================================
        print(f"\n Creating new index: '{index_name}'")
        print("   Configuration:")
        print("   - Dimension: 1536 (OpenAI embedding size)")
        print("   - Metric: cosine (measures angle between vectors)")
        print("   - Spec: Serverless (auto-scaling)")
        print("   - Cloud: AWS us-east-1")
        
        pc.create_index(
            name=index_name,
            dimension=1536,  # Must match embedding dimension
            metric="cosine",  # Cosine similarity (good for normalized vectors)
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        
        print("✓ Index created successfully!")
        
        # Wait for index to be ready
        print("\n⏳ Waiting for index to be ready...")
        time.sleep(5)
        
        # Connect to index
        index = pc.Index(index_name)
        
        print("✓ Connected to index")
        
        # ============================================================================
        # PREPARE DATA FOR UPLOAD
        # ============================================================================
        print("\n" + "="*60)
        print("Preparing data for upload...")
        print("="*60)
        
        print("""
Data format for Pinecone:
{
    'id': 'unique_id',
    'values': [0.1, 0.2, ...],  # embedding vector
    'metadata': {                # filterable fields!
        'category': 'Healthcare',
        'region': 'US',
        'topic': 'Medicare',
        'text': 'actual document text'
    }
}

The metadata is what makes Pinecone powerful!
""")
        
        # Prepare vectors for upload
        vectors_to_upload = []
        
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            vector = {
                'id': doc['id'],
                'values': embedding.tolist(),
                'metadata': {
                    'category': doc['category'],
                    'region': doc['region'],
                    'topic': doc['topic'],
                    'text': doc['text']
                }
            }
            vectors_to_upload.append(vector)
        
        print(f"\n✓ Prepared {len(vectors_to_upload)} vectors for upload")
        
        # ============================================================================
        # UPLOAD TO PINECONE
        # ============================================================================
        print("\n" + "="*60)
        print("Uploading vectors to Pinecone...")
        print("="*60)
        
        # Upload in batches (Pinecone recommends batching)
        batch_size = 100
        
        for i in range(0, len(vectors_to_upload), batch_size):
            batch = vectors_to_upload[i:i+batch_size]
            index.upsert(vectors=batch)
            print(f"  ✓ Uploaded batch {i//batch_size + 1}: {len(batch)} vectors")
        
        print(f"\n✅ Successfully uploaded {len(vectors_to_upload)} vectors!")
        
        # Wait for vectors to be indexed
        print("\n⏳ Waiting for vectors to be indexed...")
        time.sleep(2)
        
        # Get index stats
        stats = index.describe_index_stats()
        print(f"\n📊 Index Statistics:")
        print(f"   Total vectors: {stats['total_vector_count']}")
        print(f"   Dimension: {stats['dimension']}")
        
        # ============================================================================
        # TEST METADATA FILTERING
        # ============================================================================
        print("\n" + "="*60)
        print("TESTING: Metadata Filtering")
        print("="*60)
        
        # Test query
        test_query_text = "health insurance coverage"
        print(f"\n🔍 Query: '{test_query_text}'")
        
        # Use first embedding as dummy query
        query_vector = embeddings[0].tolist()
        
        # Search WITHOUT filters
        print("\n1️⃣  Search WITHOUT filters:")
        print("-" * 60)
        
        results_no_filter = index.query(
            vector=query_vector,
            top_k=3,
            include_metadata=True
        )
        
        for i, match in enumerate(results_no_filter['matches'], 1):
            print(f"{i}. ID: {match['id']}")
            print(f"   Score: {match['score']:.4f}")
            print(f"   Topic: {match['metadata']['topic']}")
            print(f"   Region: {match['metadata']['region']}")
        
        # Search WITH filters
        print("\n2️⃣  Search WITH filters (region=US AND category=Healthcare):")
        print("-" * 60)
        
        results_with_filter = index.query(
            vector=query_vector,
            top_k=3,
            include_metadata=True,
            filter={
                "region": {"$eq": "US"},
                "category": {"$eq": "Healthcare"}
            }
        )
        
        for i, match in enumerate(results_with_filter['matches'], 1):
            print(f"{i}. ID: {match['id']}")
            print(f"   Score: {match['score']:.4f}")
            print(f"   Topic: {match['metadata']['topic']}")
            print(f"   Region: {match['metadata']['region']}")
            print(f"   Text: {match['metadata']['text'][:80]}...")
        
        # Search with different filter
        print("\n3️⃣  Search WITH filter (topic=Medicare):")
        print("-" * 60)
        
        results_topic_filter = index.query(
            vector=query_vector,
            top_k=3,
            include_metadata=True,
            filter={
                "topic": {"$eq": "Medicare"}
            }
        )
        
        for i, match in enumerate(results_topic_filter['matches'], 1):
            print(f"{i}. ID: {match['id']}")
            print(f"   Score: {match['score']:.4f}")
            print(f"   Topic: {match['metadata']['topic']}")
            print(f"   Text: {match['metadata']['text'][:80]}...")
        
        print("\n✅ Pinecone setup and testing complete!")
        
    except Exception as e:
        print(f"\n❌ Error with Pinecone: {e}")
        print("   This might be due to:")
        print("   - Invalid API key")
        print("   - Network issues")
        print("   - Free tier limitations")
        use_pinecone = False

else:
    # ============================================================================
    # DEMO MODE - EXPLAIN CONCEPTS
    # ============================================================================
    print("\n" + "="*60)
    print("DEMO MODE: Understanding Pinecone Concepts")
    print("="*60)
    
    print("\n📚 What would happen with a real Pinecone API key:")
    print("-" * 60)
    print("1. Create cloud-hosted index with 1536 dimensions")
    print("2. Upload vectors with metadata:")
    
    # Show example of what we'd upload
    example_vector = {
        'id': documents[0]['id'],
        'values': '[0.123, -0.456, ...]',  # 1536 numbers
        'metadata': {
            'category': documents[0]['category'],
            'region': documents[0]['region'],
            'topic': documents[0]['topic'],
            'text': documents[0]['text'][:50] + '...'
        }
    }
    
    print("\nExample vector structure:")
    print(json.dumps(example_vector, indent=2))
    
    print("\n3. Query with filters:")
    print("   query(vector=[...], filter={'region': 'US'})")
    print("   → Returns only US documents, ranked by similarity")
    
    print("\n4. Hybrid search combines:")
    print("   ✓ Vector similarity (semantic meaning)")
    print("   ✓ Metadata filters (exact matches)")
    print("   = Best of both worlds!")

