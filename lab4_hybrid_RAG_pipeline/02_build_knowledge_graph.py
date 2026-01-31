"""
OBJECTIVE:
Learn how to create a structured knowledge graph using RDF (Resource Description Framework).

CONCEPTS:
- RDF (Resource Description Framework): A way to represent information as triples
- Triple: Subject-Predicate-Object (e.g., "Document1" "hasCategory" "Healthcare")
- SPARQL: Query language for RDF graphs (like SQL for databases)
- Knowledge Graph: Network of interconnected facts

WHY THIS MATTERS:
While vector search finds similar text, graphs find STRUCTURED relationships.
Example: "Find all US healthcare documents about Medicare" - this uses
exact metadata, not semantic similarity.
"""

import json
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace, RDF

# ============================================================================
# LOAD OUR SAMPLE DOCUMENTS
# ============================================================================
print("\nLoading documents from Step 1...")

with open('data/sample_documents.json', 'r', encoding='utf-8') as f:
    documents = json.load(f)

print(f"Loaded {len(documents)} documents")

# ============================================================================
# CONCEPT: RDF Basics
# ============================================================================
print("\n" + "="*60)
print("CONCEPT: What is RDF?")
print("="*60)
print("""
RDF represents knowledge as TRIPLES (Subject-Predicate-Object):

Example Triple:
  Subject:   doc_001
  Predicate: hasCategory  
  Object:    Healthcare

This reads as: "doc_001 has category Healthcare"

Multiple triples create a GRAPH of relationships:
  doc_001 → hasCategory → Healthcare
  doc_001 → hasRegion → US
  doc_001 → hasTopic → Insurance
  
This is more structured than just text!
""")

# ============================================================================
# CREATE RDF GRAPH
# ============================================================================
print("="*60)
print("Building the Knowledge Graph...")
print("="*60)

g = Graph()

EX = Namespace("http://example.org/healthcare/")

g.bind("ex", EX) # bind the namespace with a prefix (makes output readable)

# ============================================================================
# ADD TRIPLES TO GRAPH
# ============================================================================
print("\n Adding documents as RDF triples...")

for doc in documents:
    doc_id = doc['id']
    
    # Create a URI for this document
    # URI = Unique Resource Identifier (like a unique ID)
    doc_uri = EX[doc_id]
    
    # Triple 1: Document Type
    # States: "This resource is a Document"
    g.add((doc_uri, RDF.type, EX.Document))
    
    # Triple 2: Category
    # States: "This document has category X"
    g.add((doc_uri, EX.hasCategory, Literal(doc['category'])))
    
    # Triple 3: Region
    # States: "This document is about region Y"
    g.add((doc_uri, EX.hasRegion, Literal(doc['region'])))
    
    # Triple 4: Topic
    # States: "This document's topic is Z"
    g.add((doc_uri, EX.hasTopic, Literal(doc['topic'])))
    
    # Triple 5: Text Content
    # States: "This document contains text..."
    g.add((doc_uri, EX.hasText, Literal(doc['text'])))
    
    print(f"  ✓ Added {doc_id}: {doc['topic']} ({doc['region']})")

# ============================================================================
# GRAPH STATISTICS
# ============================================================================
print("\n" + "="*60)
print("GRAPH STATISTICS")
print("="*60)
print(f"Total triples: {len(g)}")
print(f"Documents: {len(documents)}")
print(f"Triples per document: {len(g) // len(documents)}")

# ============================================================================
# SAVE GRAPH TO FILE
# ============================================================================
output_file = Path("data/knowledge.ttl")
g.serialize(destination=str(output_file), format="turtle")

print(f"\n💾 Graph saved to: {output_file}")
print(f"   Format: Turtle (TTL) - a human-readable RDF format")
print(f"   File size: {output_file.stat().st_size:,} bytes")

# ============================================================================
# DEMONSTRATE SPARQL QUERIES
# ============================================================================
print("\n" + "="*60)
print("CONCEPT: Querying with SPARQL")
print("="*60)
print("""
SPARQL is like SQL for graphs. It finds patterns in triples.

Query Structure:
  SELECT ?variable
  WHERE {
    ?doc hasCategory "Healthcare" .
    ?doc hasRegion "US" .
  }

This finds documents that match BOTH conditions.
""")

# Example Query 1: Find all US Healthcare documents
print("\n📊 Example Query 1: Find US Healthcare Documents")
print("-" * 60)

query1 = """
PREFIX ex: <http://example.org/healthcare/>

SELECT ?doc ?topic ?text
WHERE {
    ?doc ex:hasCategory "Healthcare" ;
         ex:hasRegion "US" ;
         ex:hasTopic ?topic ;
         ex:hasText ?text .
}
LIMIT 3
"""

results1 = g.query(query1)
print(f"Found {len(results1)} documents:")
for i, row in enumerate(results1, 1):
    topic = row['topic']
    text_preview = str(row['text'])[:80]
    print(f"  {i}. Topic: {topic}")
    print(f"     Text: {text_preview}...")

# Example Query 2: Find documents by specific topic
print("\n📊 Example Query 2: Find Medicare Documents")
print("-" * 60)

query2 = """
PREFIX ex: <http://example.org/healthcare/>

SELECT ?doc ?region ?text
WHERE {
    ?doc ex:hasTopic "Medicare" ;
         ex:hasRegion ?region ;
         ex:hasText ?text .
}
"""

results2 = g.query(query2)
print(f"Found {len(results2)} document(s) about Medicare:")
for row in results2:
    print(f"  Region: {row['region']}")
    print(f"  Text: {str(row['text'])[:100]}...")

# Example Query 3: Count documents by region
print("\n📊 Example Query 3: Count Documents by Region")
print("-" * 60)

query3 = """
PREFIX ex: <http://example.org/healthcare/>

SELECT ?region (COUNT(?doc) as ?count)
WHERE {
    ?doc ex:hasRegion ?region .
}
GROUP BY ?region
"""

results3 = g.query(query3)
for row in results3:
    print(f"  {row['region']}: {row['count']} documents")

