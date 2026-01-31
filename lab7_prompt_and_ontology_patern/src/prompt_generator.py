"""
Prompt Generator Module

This module implements the RAG (Retrieval-Augmented Generation) pattern.
It retrieves knowledge from the ontology and creates enhanced prompts for LLMs.

THE RAG PATTERN:
1. RETRIEVE: Get relevant facts from knowledge base (ontology)
2. AUGMENT: Add those facts to the prompt context
3. GENERATE: LLM generates informed, accurate response

WHY THIS MATTERS:
- Reduces hallucinations (making up facts)
- Grounds AI responses in real knowledge
- Makes responses explainable and trustworthy
"""

from typing import Dict, List, Optional
from src.sparql_query import (
    query_drugs_for_disease,
    query_disease_symptoms,
    query_drug_details,
    query_all_drugs
)


# ========================================
# PROMPT TEMPLATES
# ========================================

# Template for drug treatment explanation
DRUG_TREATMENT_TEMPLATE = """You are a knowledgeable medical assistant. Based on the following verified information from our medical knowledge base:

Drug: {drug_name}
Treats: {diseases}
Mechanism of Action: {mechanism}
Typical Dosage: {dosage}

Please explain in clear, simple terms:
1. How {drug_name} works to treat {primary_disease}
2. Why the {mechanism} mechanism is effective
3. What patients should know about taking this medication

Keep the explanation accessible to non-medical professionals."""


SYMPTOM_ANALYSIS_TEMPLATE = """You are a medical education assistant. Based on our knowledge base:

Disease: {disease_name}
Known Symptoms: {symptoms}

Please explain:
1. Why these symptoms occur with {disease_name}
2. How they relate to the underlying condition
3. When someone should seek medical attention

Use simple, clear language suitable for patient education."""


DRUG_COMPARISON_TEMPLATE = """You are a pharmaceutical education assistant. Based on our knowledge base:

Drug 1: {drug1_name}
- Treats: {drug1_treats}
- Mechanism: {drug1_mechanism}

Drug 2: {drug2_name}
- Treats: {drug2_treats}
- Mechanism: {drug2_mechanism}

Please compare these medications:
1. Similarities in what they treat
2. Differences in how they work
3. Considerations for choosing between them

Provide an objective, educational comparison."""


# ========================================
# PROMPT GENERATION FUNCTIONS
# ========================================

def generate_treatment_prompt(disease_name: str) -> Dict[str, any]:
    """
    Generate an LLM prompt about treating a specific disease.
    
    This demonstrates RAG in action:
    - Queries ontology for relevant drugs
    - Constructs a factual, grounded prompt
    - Returns both prompt and supporting data
    
    Args:
        disease_name: Name of disease (e.g., "Arthritis")
    
    Returns:
        Dictionary with 'prompt', 'context', and 'metadata'
    """
    
    # STEP 1: RETRIEVE - Get knowledge from ontology
    drugs = query_drugs_for_disease(disease_name)
    
    if not drugs:
        return {
            'prompt': None,
            'context': None,
            'metadata': {'error': f'No treatment found for {disease_name}'}
        }
    
    # Use the first drug as primary treatment
    primary_drug = drugs[0]
    
    # STEP 2: AUGMENT - Build context-rich prompt
    prompt = DRUG_TREATMENT_TEMPLATE.format(
        drug_name=primary_drug.get('drugLabel', 'Unknown'),
        diseases=', '.join([d.get('diseaseLabel', '') for d in drugs]),
        mechanism=primary_drug.get('mechanismLabel', 'Unknown mechanism'),
        dosage=primary_drug.get('dosage', 'Consult healthcare provider'),
        primary_disease=disease_name
    )
    
    # STEP 3: Package everything together
    return {
        'prompt': prompt,
        'context': {
            'retrieved_drugs': drugs,
            'primary_drug': primary_drug.get('drugLabel'),
            'mechanism': primary_drug.get('mechanismLabel')
        },
        'metadata': {
            'disease': disease_name,
            'num_treatments': len(drugs),
            'rag_pattern': 'retrieval_augmented_generation'
        }
    }


def generate_symptom_prompt(disease_name: str) -> Dict[str, any]:
    """
    Generate a prompt explaining disease symptoms.
    
    Args:
        disease_name: Name of disease
    
    Returns:
        Dictionary with prompt and context
    """
    
    # RETRIEVE symptoms from ontology
    symptoms = query_disease_symptoms(disease_name)
    
    if not symptoms:
        return {
            'prompt': None,
            'context': None,
            'metadata': {'error': f'No symptoms found for {disease_name}'}
        }
    
    # AUGMENT with structured context
    symptom_list = ', '.join([s.get('symptomLabel', '') for s in symptoms])
    
    prompt = SYMPTOM_ANALYSIS_TEMPLATE.format(
        disease_name=disease_name,
        symptoms=symptom_list
    )
    
    return {
        'prompt': prompt,
        'context': {
            'retrieved_symptoms': symptoms,
            'symptom_count': len(symptoms)
        },
        'metadata': {
            'disease': disease_name,
            'rag_pattern': 'symptom_retrieval'
        }
    }


def generate_drug_comparison_prompt(drug1_name: str, drug2_name: str) -> Dict[str, any]:
    """
    Generate a prompt comparing two drugs.
    
    This shows how RAG can combine multiple knowledge retrievals.
    
    Args:
        drug1_name: First drug name
        drug2_name: Second drug name
    
    Returns:
        Dictionary with comparison prompt
    """
    
    # RETRIEVE details for both drugs
    drug1_info = query_drug_details(drug1_name)
    drug2_info = query_drug_details(drug2_name)
    
    if not drug1_info or not drug2_info:
        return {
            'prompt': None,
            'context': None,
            'metadata': {'error': 'Could not retrieve details for both drugs'}
        }
    
    # AUGMENT with comparative context
    prompt = DRUG_COMPARISON_TEMPLATE.format(
        drug1_name=drug1_name,
        drug1_treats=', '.join(drug1_info.get('treats', [])),
        drug1_mechanism=drug1_info.get('mechanism', 'Unknown'),
        drug2_name=drug2_name,
        drug2_treats=', '.join(drug2_info.get('treats', [])),
        drug2_mechanism=drug2_info.get('mechanism', 'Unknown')
    )
    
    return {
        'prompt': prompt,
        'context': {
            'drug1': drug1_info,
            'drug2': drug2_info
        },
        'metadata': {
            'comparison': f'{drug1_name} vs {drug2_name}',
            'rag_pattern': 'multi_entity_retrieval'
        }
    }


def generate_simple_prompt(user_question: str, disease_name: str) -> str:
    """
    Generate a simple, focused prompt for quick queries.
    
    This is the most basic RAG pattern - retrieve and inject context.
    
    Args:
        user_question: User's original question
        disease_name: Disease to look up
    
    Returns:
        Enhanced prompt string
    """
    
    # RETRIEVE treatment info
    drugs = query_drugs_for_disease(disease_name)
    
    if not drugs:
        return f"I don't have information about treatments for {disease_name} in my knowledge base."
    
    # Build simple context
    drug = drugs[0]
    context = f"{drug.get('drugLabel')} treats {disease_name} by acting as a {drug.get('mechanismLabel')}."
    
    # AUGMENT user question with context
    enhanced_prompt = f"""Based on this medical knowledge: {context}

User question: {user_question}

Please provide an accurate, helpful answer based on the provided knowledge."""
    
    return enhanced_prompt


def generate_discovery_prompt() -> Dict[str, any]:
    """
    Generate a prompt for exploring what's in the knowledge base.
    
    Useful for open-ended queries like "What can you tell me about medications?"
    
    Returns:
        Dictionary with discovery prompt
    """
    
    # RETRIEVE all available drugs
    all_drugs = query_all_drugs()
    
    if not all_drugs:
        return {
            'prompt': 'The knowledge base appears to be empty.',
            'context': None,
            'metadata': {'error': 'No drugs in ontology'}
        }
    
    drug_list = ', '.join([d.get('drugLabel', '') for d in all_drugs])
    
    prompt = f"""You are a medical information assistant with access to a knowledge base containing information about the following medications:

{drug_list}

Available information includes:
- What conditions each medication treats
- How the medications work (mechanism of action)
- Typical dosages

How can I help you learn about these medications?"""
    
    return {
        'prompt': prompt,
        'context': {
            'available_drugs': all_drugs,
            'total_count': len(all_drugs)
        },
        'metadata': {
            'rag_pattern': 'knowledge_discovery'
        }
    }


# ========================================
# MAIN (for testing)
# ========================================

if __name__ == "__main__":
    """
    Test the prompt generation functions.
    
    Run: python src/prompt_generator.py
    """
    
    print("=" * 80)
    print("PROMPT GENERATOR - Test Suite")
    print("=" * 80)
    
    # Test 1: Treatment prompt
    print("\n[Test 1] Generating treatment prompt for Arthritis...")
    result = generate_treatment_prompt("Arthritis")
    if result['prompt']:
        print("✅ Prompt generated successfully!")
        print("\n--- GENERATED PROMPT ---")
        print(result['prompt'])
        print("\n--- CONTEXT USED ---")
        print(f"Primary drug: {result['context']['primary_drug']}")
        print(f"Mechanism: {result['context']['mechanism']}")
    else:
        print("❌ Failed to generate prompt")
    
    # Test 2: Symptom prompt
    print("\n" + "=" * 80)
    print("\n[Test 2] Generating symptom prompt for Diabetes...")
    result = generate_symptom_prompt("Diabetes")
    if result['prompt']:
        print("✅ Prompt generated successfully!")
        print("\n--- GENERATED PROMPT ---")
        print(result['prompt'])
    else:
        print("❌ Failed to generate prompt")
    
    # Test 3: Drug comparison
    print("\n" + "=" * 80)
    print("\n[Test 3] Comparing Ibuprofen and Aspirin...")
    result = generate_drug_comparison_prompt("Ibuprofen", "Aspirin")
    if result['prompt']:
        print("✅ Comparison prompt generated!")
        print("\n--- GENERATED PROMPT ---")
        print(result['prompt'])
    else:
        print("❌ Failed to generate comparison")
    
    # Test 4: Simple prompt
    print("\n" + "=" * 80)
    print("\n[Test 4] Simple prompt for user question...")
    simple = generate_simple_prompt(
        "How does Ibuprofen help with joint pain?",
        "Arthritis"
    )
    print("✅ Simple prompt generated!")
    print("\n--- GENERATED PROMPT ---")
    print(simple)
    
    # Test 5: Discovery prompt
    print("\n" + "=" * 80)
    print("\n[Test 5] Discovery prompt...")
    result = generate_discovery_prompt()
    if result['prompt']:
        print("✅ Discovery prompt generated!")
        print("\n--- GENERATED PROMPT ---")
        print(result['prompt'])
        print(f"\n--- Available drugs: {result['context']['total_count']} ---")
    else:
        print("❌ Failed to generate discovery prompt")
    
    print("\n" + "=" * 80)
    print("All tests complete!")
    print("=" * 80)