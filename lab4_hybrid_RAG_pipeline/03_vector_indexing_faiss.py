"""
OBJECTIVE:
Learn how to convert text into vectors (embeddings) and search them using FAISS.

CONCEPTS:
- Embeddings: Converting text into numerical vectors (lists of numbers)
- Vector similarity: Measuring how "close" two pieces of text are in meaning
- FAISS: Fast library for searching similar vectors
- Semantic search: Finding similar meanings, not just exact words

WHY THIS MATTERS:
"What are healthcare benefits?" should match documents about:
- "Health insurance advantages"
- "Medical coverage perks"
- "Healthcare plan features"

Vector search finds SEMANTIC similarity, not just keyword matches!
"""

import json
import numpy as np
from pathlib import Path
import os
from dotenv import load_dotenv
from openai import OpenAI
import faiss

print("="*60)
print("STEP 3: Vector Indexing with FAISS")
print("="*60)

# ============================================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================================

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')

if not openai_api_key or openai_api_key == 'your_openai_api_key_here':
    use_real_api = False
else:
    print("OpenAI API key loaded")
    use_real_api = True
    client = OpenAI(api_key=openai_api_key)

# ============================================================================
# LOAD DOCUMENTS
# ============================================================================
print("\n📖 Loading documents from Step 1...")

with open('data/sample_documents.json', 'r', encoding='utf-8') as f:
    documents = json.load(f)

texts = [doc['text'] for doc in documents]
print(f"✓ Loaded {len(texts)} documents")

# ============================================================================
# CONCEPT: What are Embeddings?
# ============================================================================
print("\n" + "="*60)
print("CONCEPT: What are Embeddings?")
print("="*60)
print("""
Embeddings convert text into vectors (lists of numbers):

Text: "Healthcare benefits in the US"
      ↓ (OpenAI embedding model)
Vector: [0.123, -0.456, 0.789, ..., 0.234]  (1536 numbers!)

WHY? Because computers can measure distance between vectors:

  "healthcare benefits" → [0.1, 0.5, ...]
  "medical advantages"  → [0.12, 0.48, ...]  ← Very similar!
  "car insurance"       → [0.8, -0.3, ...]   ← Very different!

Similar meanings = similar vectors = small distance
Different meanings = different vectors = large distance
""")

# ============================================================================
# CREATE EMBEDDINGS
# ============================================================================
print("="*60)
print("Creating Embeddings...")
print("="*60)

embeddings = []

if use_real_api:
    print("\n🌐 Using OpenAI API to create embeddings...")
    print(f"   Model: text-embedding-3-small")
    print(f"   Embedding dimension: 1536")
    print(f"   Processing {len(texts)} documents...")
    
    try:
        for i, text in enumerate(texts, 1):
            # Call OpenAI API to get embedding
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            
            # Extract the embedding vector
            embedding = response.data[0].embedding
            embeddings.append(embedding)
            
            print(f"  ✓ Document {i}/{len(texts)}: {documents[i-1]['topic']}")
        
        print(f"\nCreated {len(embeddings)} embeddings successfully!")
        
    except Exception as e:
        print(f"\nError calling OpenAI API: {e}")
        print("   Creating dummy embeddings for learning purposes...")
        use_real_api = False

if not use_real_api:
    print("\n🔧 Creating dummy embeddings for learning...")
    print("   (These are random vectors, not real semantic embeddings)")
    
    # Create random embeddings (1536 dimensions like OpenAI)
    np.random.seed(42)  # For reproducibility
    embeddings = np.random.randn(len(texts), 1536).tolist()
    
    print(f"Created {len(embeddings)} dummy embeddings")

# Convert to numpy array
embeddings_array = np.array(embeddings).astype('float32')

print(f"\n📊 Embedding Statistics:")
print(f"   Shape: {embeddings_array.shape}")
print(f"   (That's {embeddings_array.shape[0]} documents × {embeddings_array.shape[1]} dimensions)")
print(f"   Memory: {embeddings_array.nbytes / 1024:.2f} KB")

# ============================================================================
# CONCEPT: What is FAISS?
# ============================================================================
print("\n" + "="*60)
print("CONCEPT: What is FAISS?")
print("="*60)
print("""
FAISS = Facebook AI Similarity Search

It's a library that makes searching millions of vectors FAST.

Think of it like:
- Traditional search: Check every document one by one
- FAISS: Use clever math to find nearest neighbors instantly

IndexFlatL2 = "Flat index using L2 distance"
- Flat: Brute force, checks all vectors (simple but accurate)
- L2: Euclidean distance (straight-line distance in vector space)

For millions of vectors, there are faster index types, but this
is perfect for learning!
""")

# ============================================================================
# BUILD FAISS INDEX
# ============================================================================
print("="*60)
print("Building FAISS Index...")
print("="*60)

# Get embedding dimension (1536 for OpenAI embeddings)
dimension = embeddings_array.shape[1]

# Create FAISS index
# IndexFlatL2 = exact search using L2 (Euclidean) distance
index = faiss.IndexFlatL2(dimension)

print(f"\n🏗️  Created FAISS index:")
print(f"   Type: IndexFlatL2 (exact search)")
print(f"   Dimension: {dimension}")
print(f"   Is trained: {index.is_trained}")

# Add embeddings to index
index.add(embeddings_array)

print(f"\nAdded {index.ntotal} vectors to index")

# ============================================================================
# SAVE INDEX AND EMBEDDINGS
# ============================================================================
print("\nSaving FAISS index and embeddings...")

models_dir = Path("models")
models_dir.mkdir(exist_ok=True)

# Save FAISS index
index_file = models_dir / "faiss_index.bin"
faiss.write_index(index, str(index_file))
print(f"✓ FAISS index saved to: {index_file}")

# Save embeddings array (we'll need this later)
embeddings_file = models_dir / "embeddings.npy"
np.save(str(embeddings_file), embeddings_array)
print(f"✓ Embeddings saved to: {embeddings_file}")

# ============================================================================
# TEST THE INDEX - SEARCH EXAMPLE
# ============================================================================
print("\n" + "="*60)
print("TESTING: Semantic Search with FAISS")
print("="*60)

# Create a test query
test_query = "What are healthcare benefits in the US?"
print(f"\n🔍 Query: '{test_query}'")

# Get query embedding
if use_real_api:
    try:
        query_response = client.embeddings.create(
            model="text-embedding-3-small",
            input=test_query
        )
        query_embedding = np.array([query_response.data[0].embedding]).astype('float32')
    except:
        query_embedding = np.random.randn(1, dimension).astype('float32')
else:
    # Use first document embedding as dummy query
    query_embedding = embeddings_array[0:1]

# Search for top 3 most similar documents
k = 3  # number of results
distances, indices = index.search(query_embedding, k)

print(f"\n📊 Top {k} most similar documents:")
print("-" * 60)

for i, (idx, distance) in enumerate(zip(indices[0], distances[0]), 1):
    doc = documents[idx]
    print(f"\n{i}. Document: {doc['id']}")
    print(f"   Topic: {doc['topic']}")
    print(f"   Region: {doc['region']}")
    print(f"   Distance: {distance:.4f} (lower = more similar)")
    print(f"   Text: {doc['text'][:100]}...")

# ============================================================================
# EXPLAIN THE RESULTS
# ============================================================================
print("\n" + "="*60)
print("UNDERSTANDING THE RESULTS")
print("="*60)
print("""
FAISS found the documents with the SMALLEST distance to our query.

Distance Interpretation:
- 0.0 = Identical vectors
- Small distance (0-10) = Very similar meaning
- Large distance (>50) = Very different meaning

The top results should be about healthcare benefits, insurance,
coverage, etc. - things semantically related to the query!
""")

