"""
SPARQL Query Module

This module handles all interactions with the Apache Jena Fuseki triple store.
It provides functions to query the healthcare ontology and retrieve knowledge.

KEY CONCEPTS:
- SPARQL: Query language for RDF/ontologies (like SQL for graphs)
- Triple Store: Database that stores subject-predicate-object triples
- Endpoint: The URL where we send SPARQL queries

LEARNING OBJECTIVES:
1. How to connect to a SPARQL endpoint
2. How to construct SPARQL queries
3. How to process query results
"""

import requests
import json
from typing import List, Dict, Optional
from SPARQLWrapper import SPARQLWrapper, JSON


# ========================================
# CONFIGURATION
# ========================================

# Fuseki endpoint - where our ontology is stored
FUSEKI_ENDPOINT = "http://localhost:3030/healthcare/sparql"

# Namespace prefix for our healthcare ontology
HEALTHCARE_PREFIX = "http://example.org/healthcare#"


# ========================================
# HELPER FUNCTIONS
# ========================================

def extract_local_name(uri: str) -> str:
    """
    Extract the local name from a full URI.
    
    Example:
        Input: "http://example.org/healthcare#Ibuprofen"
        Output: "Ibuprofen"
    
    Args:
        uri: Full URI string
    
    Returns:
        Local name (last part after # or /)
    """
    if '#' in uri:
        return uri.split('#')[-1]
    elif '/' in uri:
        return uri.split('/')[-1]
    return uri


def format_query_results(results: Dict) -> List[Dict[str, str]]:
    """
    Convert raw SPARQL JSON results into a clean list of dictionaries.
    
    Args:
        results: Raw JSON response from SPARQL endpoint
    
    Returns:
        List of dictionaries with clean key-value pairs
    
    Example:
        Input: Complex JSON with URIs
        Output: [{"drug": "Ibuprofen", "mechanism": "COX_Inhibitor"}]
    """
    formatted = []
    
    if 'results' in results and 'bindings' in results['results']:
        for binding in results['results']['bindings']:
            row = {}
            for key, value in binding.items():
                # Extract just the value, removing URI prefixes
                if value['type'] == 'uri':
                    row[key] = extract_local_name(value['value'])
                else:
                    row[key] = value['value']
            formatted.append(row)
    
    return formatted


# ========================================
# QUERY FUNCTIONS
# ========================================

def query_drugs_for_disease(disease_name: str) -> List[Dict[str, str]]:
    """
    Find all drugs that treat a specific disease.
    
    This demonstrates the RAG pattern: we retrieve relevant knowledge
    before generating a response.
    
    Args:
        disease_name: Name of the disease (e.g., "Arthritis")
    
    Returns:
        List of drugs with their mechanisms
        
    Example:
        >>> query_drugs_for_disease("Arthritis")
        [{"drug": "Ibuprofen", "mechanism": "COX_Inhibitor"}]
    """
    
    # SPARQL Query Construction
    # This query says: "Find drugs that treat [disease] and tell me their mechanism"
    query = f"""
    PREFIX ex: <{HEALTHCARE_PREFIX}>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?drug ?drugLabel ?mechanism ?mechanismLabel ?dosage
    WHERE {{
        ?drug ex:treats ex:{disease_name} .
        ?drug rdfs:label ?drugLabel .
        ?drug ex:hasMechanism ?mechanism .
        ?mechanism rdfs:label ?mechanismLabel .
        OPTIONAL {{ ?drug ex:hasDosage ?dosage }}
    }}
    """
    
    try:
        # Send query to Fuseki
        response = requests.post(
            FUSEKI_ENDPOINT,
            data={'query': query},
            headers={'Accept': 'application/sparql-results+json'}
        )
        
        # Check if request was successful
        response.raise_for_status()
        
        # Parse and format results
        results = response.json()
        return format_query_results(results)
    
    except requests.exceptions.RequestException as e:
        print(f"Error querying SPARQL endpoint: {e}")
        return []


def query_disease_symptoms(disease_name: str) -> List[Dict[str, str]]:
    """
    Find all symptoms associated with a disease.
    
    Args:
        disease_name: Name of the disease
    
    Returns:
        List of symptoms
    """
    
    query = f"""
    PREFIX ex: <{HEALTHCARE_PREFIX}>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?symptom ?symptomLabel
    WHERE {{
        ex:{disease_name} ex:hasSymptom ?symptom .
        ?symptom rdfs:label ?symptomLabel .
    }}
    """
    
    try:
        response = requests.post(
            FUSEKI_ENDPOINT,
            data={'query': query},
            headers={'Accept': 'application/sparql-results+json'}
        )
        response.raise_for_status()
        results = response.json()
        return format_query_results(results)
    
    except requests.exceptions.RequestException as e:
        print(f"Error querying symptoms: {e}")
        return []


def query_drug_details(drug_name: str) -> Dict[str, any]:
    """
    Get comprehensive information about a specific drug.
    
    This is useful for creating detailed, informative prompts.
    
    Args:
        drug_name: Name of the drug (e.g., "Ibuprofen")
    
    Returns:
        Dictionary with all drug information
    """
    
    query = f"""
    PREFIX ex: <{HEALTHCARE_PREFIX}>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?disease ?diseaseLabel ?mechanism ?mechanismLabel ?dosage
    WHERE {{
        ex:{drug_name} ex:treats ?disease .
        ex:{drug_name} ex:hasMechanism ?mechanism .
        ex:{drug_name} ex:hasDosage ?dosage .
        ?disease rdfs:label ?diseaseLabel .
        ?mechanism rdfs:label ?mechanismLabel .
    }}
    """
    
    try:
        response = requests.post(
            FUSEKI_ENDPOINT,
            data={'query': query},
            headers={'Accept': 'application/sparql-results+json'}
        )
        response.raise_for_status()
        results = response.json()
        formatted = format_query_results(results)
        
        if formatted:
            # Combine results into a single drug profile
            drug_info = {
                'name': drug_name,
                'treats': list(set([r['diseaseLabel'] for r in formatted])),
                'mechanism': formatted[0]['mechanismLabel'] if formatted else None,
                'dosage': formatted[0].get('dosage', 'Not specified')
            }
            return drug_info
        
        return {}
    
    except requests.exceptions.RequestException as e:
        print(f"Error querying drug details: {e}")
        return {}


def query_all_drugs() -> List[Dict[str, str]]:
    """
    Get a list of all drugs in the ontology.
    
    Returns:
        List of all drugs with basic info
    """
    
    query = f"""
    PREFIX ex: <{HEALTHCARE_PREFIX}>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT DISTINCT ?drug ?drugLabel
    WHERE {{
        ?drug a ex:Drug .
        ?drug rdfs:label ?drugLabel .
    }}
    ORDER BY ?drugLabel
    """
    
    try:
        response = requests.post(
            FUSEKI_ENDPOINT,
            data={'query': query},
            headers={'Accept': 'application/sparql-results+json'}
        )
        response.raise_for_status()
        results = response.json()
        return format_query_results(results)
    
    except requests.exceptions.RequestException as e:
        print(f"Error querying all drugs: {e}")
        return []


def test_connection() -> bool:
    """
    Test if we can connect to the Fuseki endpoint.
    
    Returns:
        True if connection successful, False otherwise
    """
    
    # Simple query to test connectivity
    query = """
    SELECT * WHERE { ?s ?p ?o } LIMIT 1
    """
    
    try:
        response = requests.post(
            FUSEKI_ENDPOINT,
            data={'query': query},
            headers={'Accept': 'application/sparql-results+json'},
            timeout=5
        )
        response.raise_for_status()
        return True
    
    except requests.exceptions.RequestException as e:
        print(f"Connection test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Is Fuseki running? Check: docker ps")
        print("2. Is the dataset created? Visit: http://localhost:3030")
        print("3. Is the ontology uploaded?")
        return False


# ========================================
# MAIN (for testing)
# ========================================

if __name__ == "__main__":
    """
    Run: python src/sparql_query.py
    """
    
    print("=" * 60)
    print("SPARQL Query Module - Test Suite")
    print("=" * 60)
    
    # Test 1: Connection
    print("\n[Test 1] Testing connection to Fuseki...")
    if test_connection():
        print("✅ Connection successful!")
    else:
        print("❌ Connection failed. Please check Fuseki setup.")
        exit(1)
    
    # Test 2: Query drugs for Arthritis
    print("\n[Test 2] Querying drugs for Arthritis...")
    drugs = query_drugs_for_disease("Arthritis")
    if drugs:
        print(f"✅ Found {len(drugs)} drug(s):")
        for drug in drugs:
            print(f"   - {drug.get('drugLabel')}: {drug.get('mechanismLabel')}")
    else:
        print("❌ No results. Check if ontology is uploaded.")
    
    # Test 3: Query disease symptoms
    print("\n[Test 3] Querying symptoms of Diabetes...")
    symptoms = query_disease_symptoms("Diabetes")
    if symptoms:
        print(f"✅ Found {len(symptoms)} symptom(s):")
        for symptom in symptoms:
            print(f"   - {symptom.get('symptomLabel')}")
    else:
        print("❌ No symptoms found.")
    
    # Test 4: Get drug details
    print("\n[Test 4] Getting details for Ibuprofen...")
    details = query_drug_details("Ibuprofen")
    if details:
        print("✅ Drug details:")
        print(f"   Name: {details.get('name')}")
        print(f"   Treats: {', '.join(details.get('treats', []))}")
        print(f"   Mechanism: {details.get('mechanism')}")
        print(f"   Dosage: {details.get('dosage')}")
    else:
        print("❌ No details found.")
    
    # Test 5: List all drugs
    print("\n[Test 5] Listing all drugs in ontology...")
    all_drugs = query_all_drugs()
    if all_drugs:
        print(f"✅ Found {len(all_drugs)} drug(s):")
        for drug in all_drugs:
            print(f"   - {drug.get('drugLabel')}")
    else:
        print("❌ No drugs found.")
    
    print("\n" + "=" * 60)
    print("Tests complete!")
    print("=" * 60)