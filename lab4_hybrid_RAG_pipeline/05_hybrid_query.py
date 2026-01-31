"""
OBJECTIVE:
Combine FAISS + RDF Graph + Pinecone to build a complete hybrid RAG system.

CONCEPTS:
- Hybrid Retrieval: Use multiple methods to find the best context
- Context Assembly: Combine results from different sources
- Prompt Engineering: Structure context for LLM
- RAG Pipeline: Complete flow from query to answer

WHY THIS MATTERS:
Different retrieval methods have different strengths:
- FAISS: Fast local semantic search
- RDF Graph: Structured relationship queries
- Pinecone: Cloud semantic search + metadata filters

Combining them gives better, more accurate answers!
"""

import json
import numpy as np
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import faiss
from rdflib import Graph
from pinecone import Pinecone

print("="*70)
print(" " * 15 + "🎯 HYBRID RAG PIPELINE 🎯")
print("="*70)
print("Combining:")
print("  🔵 FAISS (Local Vector Search)")
print("  🟢 RDF Graph (Structured Knowledge)")
print("  🟣 Pinecone (Cloud Vector + Metadata)")
print("="*70)

# ============================================================================
# SETUP
# ============================================================================
print("\n Loading resources...")

# Load environment variables
load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
pinecone_api_key = os.getenv('PINECONE_API_KEY')

use_openai = openai_api_key and openai_api_key != 'your_openai_api_key_here'
use_pinecone = pinecone_api_key and pinecone_api_key != 'your_pinecone_api_key_here'

if use_openai:
    client = OpenAI(api_key=openai_api_key)
    print("OpenAI client initialized")
else:
    print("OpenAI API not available - using demo mode")

if use_pinecone:
    try:
        pc = Pinecone(api_key=pinecone_api_key)
        pinecone_index = pc.Index("lab4-hybrid-rag")
        print("Pinecone index connected")
    except:
        use_pinecone = False
        print("Pinecone not available - using FAISS and RDF only")
else:
    print("Pinecone not configured - using FAISS and RDF only")

# Load documents
with open('data/sample_documents.json', 'r', encoding='utf-8') as f:
    documents = json.load(f)
print(f"Loaded {len(documents)} documents")

# Load FAISS index
faiss_index = faiss.read_index('models/faiss_index.bin')
embeddings = np.load('models/embeddings.npy')
print(f"Loaded FAISS index with {faiss_index.ntotal} vectors")

# Load RDF graph
rdf_graph = Graph()
rdf_graph.parse('data/knowledge.ttl', format='turtle')
print(f"Loaded RDF graph with {len(rdf_graph)} triples")

# ============================================================================
# CONCEPT: The Hybrid RAG Pipeline
# ============================================================================
print("\n" + "="*70)
print("CONCEPT: How Hybrid RAG Works")
print("="*70)
print("""
Traditional RAG:
  User Query → Vector Search → Top K docs → LLM → Answer

Hybrid RAG (Our Approach):
  User Query → ┬→ FAISS Search (semantic)
               ├→ RDF Query (structured)  
               └→ Pinecone Search (semantic + filters)
               ↓
          Combine All Results
               ↓
          Deduplicate & Rank
               ↓
          Assemble Context
               ↓
          LLM with Rich Context
               ↓
          Better Answer!

WHY? Different sources catch different relevant info:
- FAISS might find similar phrasing
- RDF might find exact category matches
- Pinecone might filter to specific regions

Combining them = more comprehensive context!
""")

# ============================================================================
# DEFINE HELPER FUNCTIONS
# ============================================================================

def get_embedding(text, use_api=True):
    """Get embedding for a text query"""
    if use_api and use_openai:
        try:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return np.array(response.data[0].embedding).astype('float32')
        except Exception as e:
            print(f"  ⚠️  Error getting embedding: {e}")
            return embeddings[0]  # fallback
    else:
        # Use first document embedding as dummy
        return embeddings[0]

def search_faiss(query_embedding, k=3):
    """Search FAISS index for similar vectors"""
    query_vector = query_embedding.reshape(1, -1)
    distances, indices = faiss_index.search(query_vector, k)
    
    results = []
    for idx, distance in zip(indices[0], distances[0]):
        results.append({
            'source': 'FAISS',
            'doc_id': documents[idx]['id'],
            'distance': float(distance),
            'document': documents[idx]
        })
    return results

def search_rdf(category=None, region=None, topic=None):
    """Query RDF graph with filters"""
    
    # Build SPARQL query dynamically
    filters = []
    if category:
        filters.append(f'?doc ex:hasCategory "{category}"')
    if region:
        filters.append(f'?doc ex:hasRegion "{region}"')
    if topic:
        filters.append(f'?doc ex:hasTopic "{topic}"')
    
    filter_clause = " ;\n         ".join(filters) if filters else "?doc ex:hasText ?text"
    
    query = f"""
    PREFIX ex: <http://example.org/healthcare/>
    
    SELECT ?doc ?text ?category ?region ?topic
    WHERE {{
        {filter_clause} ;
             ex:hasText ?text ;
             ex:hasCategory ?category ;
             ex:hasRegion ?region ;
             ex:hasTopic ?topic .
    }}
    LIMIT 3
    """
    
    results = []
    try:
        query_results = rdf_graph.query(query)
        for row in query_results:
            # Find matching document
            doc_uri = str(row['doc'])
            doc_id = doc_uri.split('/')[-1]
            
            matching_doc = next((d for d in documents if d['id'] == doc_id), None)
            if matching_doc:
                results.append({
                    'source': 'RDF',
                    'doc_id': doc_id,
                    'document': matching_doc
                })
    except Exception as e:
        print(f"  ⚠️  RDF query error: {e}")
    
    return results

def search_pinecone(query_embedding, filters=None, k=3):
    """Search Pinecone with optional metadata filters"""
    if not use_pinecone:
        return []
    
    try:
        query_results = pinecone_index.query(
            vector=query_embedding.tolist(),
            top_k=k,
            include_metadata=True,
            filter=filters
        )
        
        results = []
        for match in query_results['matches']:
            results.append({
                'source': 'Pinecone',
                'doc_id': match['id'],
                'score': match['score'],
                'document': {
                    'id': match['id'],
                    'text': match['metadata']['text'],
                    'category': match['metadata']['category'],
                    'region': match['metadata']['region'],
                    'topic': match['metadata']['topic']
                }
            })
        return results
    except Exception as e:
        print(f"  ⚠️  Pinecone search error: {e}")
        return []

def deduplicate_results(all_results):
    """Remove duplicate documents, keeping highest priority source"""
    seen_docs = {}
    source_priority = {'Pinecone': 3, 'FAISS': 2, 'RDF': 1}
    
    for result in all_results:
        doc_id = result['doc_id']
        if doc_id not in seen_docs:
            seen_docs[doc_id] = result
        else:
            # Keep result from higher priority source
            current_priority = source_priority.get(seen_docs[doc_id]['source'], 0)
            new_priority = source_priority.get(result['source'], 0)
            if new_priority > current_priority:
                seen_docs[doc_id] = result
    
    return list(seen_docs.values())

def assemble_context(results):
    """Create context string from results"""
    context_parts = []
    
    for i, result in enumerate(results, 1):
        doc = result['document']
        source = result['source']
        
        context_parts.append(
            f"[Document {i} - Source: {source}]\n"
            f"Topic: {doc['topic']}\n"
            f"Region: {doc['region']}\n"
            f"Text: {doc['text']}\n"
        )
    
    return "\n".join(context_parts)

# ============================================================================
# INTERACTIVE QUERY SYSTEM
# ============================================================================

def run_hybrid_query(query_text, category=None, region=None, topic=None):
    """
    Run a complete hybrid RAG query
    
    Args:
        query_text: The user's question
        category: Optional category filter
        region: Optional region filter  
        topic: Optional topic filter
    """
    
    print("\n" + "="*70)
    print(f"🔍 QUERY: {query_text}")
    print("="*70)
    
    if category or region or topic:
        print("\n📋 Filters:")
        if category:
            print(f"   Category: {category}")
        if region:
            print(f"   Region: {region}")
        if topic:
            print(f"   Topic: {topic}")
    
    # Step 1: Get query embedding
    print("\n1️⃣  Getting query embedding...")
    query_embedding = get_embedding(query_text, use_api=use_openai)
    print("   ✓ Embedding created")
    
    # Step 2: Search FAISS
    print("\n2️⃣  Searching FAISS (local vector search)...")
    faiss_results = search_faiss(query_embedding, k=3)
    print(f"   ✓ Found {len(faiss_results)} results from FAISS")
    for r in faiss_results:
        print(f"      - {r['doc_id']}: {r['document']['topic']} (distance: {r['distance']:.2f})")
    
    # Step 3: Query RDF Graph
    print("\n3️⃣  Querying RDF Graph (structured knowledge)...")
    rdf_results = search_rdf(category=category, region=region, topic=topic)
    print(f"   ✓ Found {len(rdf_results)} results from RDF")
    for r in rdf_results:
        print(f"      - {r['doc_id']}: {r['document']['topic']}")
    
    # Step 4: Search Pinecone (if available)
    print("\n4️⃣  Searching Pinecone (cloud vector + metadata)...")
    pinecone_filters = {}
    if category:
        pinecone_filters['category'] = {'$eq': category}
    if region:
        pinecone_filters['region'] = {'$eq': region}
    if topic:
        pinecone_filters['topic'] = {'$eq': topic}
    
    pinecone_results = search_pinecone(
        query_embedding, 
        filters=pinecone_filters if pinecone_filters else None,
        k=3
    )
    print(f"   ✓ Found {len(pinecone_results)} results from Pinecone")
    for r in pinecone_results:
        print(f"      - {r['doc_id']}: {r['document']['topic']} (score: {r.get('score', 0):.4f})")
    
    # Step 5: Combine and deduplicate
    print("\n5️⃣  Combining and deduplicating results...")
    all_results = faiss_results + rdf_results + pinecone_results
    unique_results = deduplicate_results(all_results)
    print(f"   ✓ Combined {len(all_results)} results → {len(unique_results)} unique documents")
    
    # Step 6: Assemble context
    print("\n6️⃣  Assembling context for LLM...")
    context = assemble_context(unique_results[:5])  # Use top 5 unique results
    print(f"   ✓ Context assembled ({len(context)} characters)")
    
    # Step 7: Generate answer with LLM
    print("\n7️⃣  Generating answer with GPT-4...")
    
    prompt = f"""You are a helpful assistant answering questions about healthcare policies.

Use the following context to answer the question. If the context doesn't contain 
enough information, say so.

CONTEXT:
{context}

QUESTION: {query_text}

ANSWER:"""
    
    if use_openai:
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant specializing in healthcare policy information."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            
        except Exception as e:
            print(f"   ⚠️  Error calling OpenAI: {e}")
            answer = "[Demo Mode] In a real system, GPT-4 would generate an answer based on the retrieved context."
    else:
        answer = "[Demo Mode] In a real system, GPT-4 would generate an answer based on the retrieved context."
    
    # Display results
    print("\n" + "="*70)
    print("📊 RESULTS")
    print("="*70)
    
    print(f"\n📚 Retrieved {len(unique_results)} unique documents:")
    for i, result in enumerate(unique_results, 1):
        doc = result['document']
        print(f"\n{i}. [{result['source']}] {doc['id']}")
        print(f"   Topic: {doc['topic']} | Region: {doc['region']}")
        print(f"   Text: {doc['text'][:100]}...")
    
    print("\n" + "="*70)
    print("💡 ANSWER")
    print("="*70)
    print(f"\n{answer}\n")
    
    print("="*70)
    print("✅ Hybrid RAG Query Complete!")
    print("="*70)
    
    return {
        'query': query_text,
        'results': unique_results,
        'context': context,
        'answer': answer
    }

# ============================================================================
# RUN EXAMPLE QUERIES
# ============================================================================

print("\n" + "🎓 RUNNING EXAMPLE QUERIES...\n")

# Example 1: General question
print("\n" + "▶" * 35)
print("EXAMPLE 1: General Healthcare Question")
print("▶" * 35)

result1 = run_hybrid_query(
    query_text="What are the healthcare benefits available in the US?",
    category="Healthcare",
    region="US"
)

# Example 2: Specific topic
print("\n" + "▶" * 35)
print("EXAMPLE 2: Specific Topic Question")
print("▶" * 35)

result2 = run_hybrid_query(
    query_text="Tell me about Medicare coverage",
    topic="Medicare"
)

# Example 3: No filters
print("\n" + "▶" * 35)
print("EXAMPLE 3: Open-ended Question (No Filters)")
print("▶" * 35)

result3 = run_hybrid_query(
    query_text="What preventive care services are covered by insurance?"
)

# ============================================================================
# WHAT WE LEARNED
# ============================================================================
print("\n" + "="*70)
print("🎓 WHAT WE LEARNED IN THIS LAB")
print("="*70)
print("""
✅ CONCEPTS MASTERED:

1. RAG (Retrieval-Augmented Generation)
   - Retrieve relevant context before generating answers
   - Better than pure LLM (no hallucinations from missing context)

2. Vector Embeddings
   - Convert text to numerical vectors
   - Similar meanings = similar vectors
   - Enable semantic search

3. FAISS (Vector Search)
   - Fast local similarity search
   - Great for finding semantically similar content

4. RDF Graphs (Structured Knowledge)
   - Triple-based knowledge representation
   - SPARQL queries for exact metadata matches
   - Perfect for structured data

5. Pinecone (Managed Vector DB)
   - Cloud-hosted vector search
   - Metadata filtering built-in
   - Combines semantic + structured search

6. Hybrid RAG Pipeline
   - Use multiple retrieval methods
   - Deduplicate and rank results
   - Assemble rich context for LLM
   - Generate accurate, grounded answers

✅ SKILLS DEVELOPED:
   - Loading and preprocessing data
   - Creating embeddings with OpenAI
   - Building and querying RDF graphs
   - Using FAISS for vector search
   - Setting up cloud vector databases
   - Combining multiple retrieval sources
   - Prompt engineering for RAG
   - End-to-end pipeline development

✅ TECHNOLOGIES USED:
   - Python
   - OpenAI API (embeddings + GPT-4)
   - FAISS (vector similarity)
   - RDFLib (knowledge graphs)
   - Pinecone (vector database)
   - NumPy (numerical computing)
""")

