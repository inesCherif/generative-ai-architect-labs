"""
End-to-End Demo Workflow

This script demonstrates the complete RAG pipeline:
1. Query the ontology (SPARQL)
2. Generate enhanced prompts
3. Show how this would integrate with an LLM

Run this to see the entire system in action!

Usage:
    python examples/demo_workflow.py
"""

import sys
import os

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sparql_query import (
    query_drugs_for_disease,
    query_disease_symptoms,
    test_connection
)
from src.prompt_generator import (
    generate_treatment_prompt,
    generate_symptom_prompt,
    generate_drug_comparison_prompt
)


def print_section(title):
    """Helper function to print section headers"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80 + "\n")


def demo_basic_retrieval():
    """
    Demo 1: Basic Knowledge Retrieval
    
    Shows how to query the ontology for facts.
    """
    print_section("DEMO 1: Basic Knowledge Retrieval")
    
    print("Question: What drugs treat Arthritis?")
    print("\n[Querying ontology with SPARQL...]")
    
    drugs = query_drugs_for_disease("Arthritis")
    
    if drugs:
        print(f"\n✅ Found {len(drugs)} treatment(s):\n")
        for drug in drugs:
            print(f"  Drug: {drug.get('drugLabel')}")
            print(f"  Mechanism: {drug.get('mechanismLabel')}")
            print(f"  Dosage: {drug.get('dosage', 'Not specified')}")
            print()
    else:
        print("❌ No treatments found")
    
    input("\nPress Enter to continue...")


def demo_rag_prompt_generation():
    """
    Demo 2: RAG Prompt Generation
    
    Shows how retrieval enhances AI prompts.
    """
    print_section("DEMO 2: RAG Prompt Generation")
    
    print("User Question: 'How can I treat Arthritis?'")
    print("\n[Step 1] Retrieving knowledge from ontology...")
    
    result = generate_treatment_prompt("Arthritis")
    
    if result['prompt']:
        print("\n[Step 2] Knowledge retrieved:")
        print(f"  - Primary drug: {result['context']['primary_drug']}")
        print(f"  - Mechanism: {result['context']['mechanism']}")
        
        print("\n[Step 3] Generated Enhanced Prompt:")
        print("-" * 80)
        print(result['prompt'])
        print("-" * 80)
        
        print("\n💡 This prompt would now be sent to an LLM (like GPT-4 or Claude)")
        print("   The LLM's response will be grounded in real medical knowledge!")
    else:
        print("❌ Failed to generate prompt")
    
    input("\nPress Enter to continue...")


def demo_symptom_analysis():
    """
    Demo 3: Symptom Analysis
    
    Shows multi-entity retrieval.
    """
    print_section("DEMO 3: Symptom Analysis")
    
    print("Question: What are the symptoms of Diabetes?")
    print("\n[Retrieving symptoms from ontology...]")
    
    symptoms = query_disease_symptoms("Diabetes")
    
    if symptoms:
        print(f"\n✅ Found {len(symptoms)} symptom(s):")
        for symptom in symptoms:
            print(f"  - {symptom.get('symptomLabel')}")
        
        print("\n[Generating educational prompt...]")
        result = generate_symptom_prompt("Diabetes")
        
        print("\n" + "-" * 80)
        print(result['prompt'])
        print("-" * 80)
    else:
        print("❌ No symptoms found")
    
    input("\nPress Enter to continue...")


def demo_drug_comparison():
    """
    Demo 4: Drug Comparison
    
    Shows complex RAG pattern combining multiple retrievals.
    """
    print_section("DEMO 4: Drug Comparison")
    
    print("Question: How do Ibuprofen and Aspirin compare?")
    print("\n[Retrieving details for both drugs...]")
    
    result = generate_drug_comparison_prompt("Ibuprofen", "Aspirin")
    
    if result['prompt']:
        print("\n✅ Retrieved information for both drugs")
        print("\n[Generated Comparison Prompt:]")
        print("-" * 80)
        print(result['prompt'])
        print("-" * 80)
        
        print("\n📊 Context used:")
        print(f"  Drug 1: {result['context']['drug1']['name']}")
        print(f"    Treats: {', '.join(result['context']['drug1']['treats'])}")
        print(f"  Drug 2: {result['context']['drug2']['name']}")
        print(f"    Treats: {', '.join(result['context']['drug2']['treats'])}")
    else:
        print("❌ Failed to generate comparison")
    
    input("\nPress Enter to continue...")


def demo_without_rag_vs_with_rag():
    """
    Demo 5: With vs Without RAG
    
    Shows the value of RAG by comparing approaches.
    """
    print_section("DEMO 5: The Value of RAG")
    
    print("User Question: 'How does Ibuprofen work for arthritis?'\n")
    
    print("❌ WITHOUT RAG (LLM alone):")
    print("-" * 80)
    print("""The LLM would generate a response based only on training data:
- Might be generic or outdated
- Could include hallucinations
- Not grounded in your specific knowledge base
- No source attribution""")
    print("-" * 80)
    
    print("\n✅ WITH RAG (Our System):")
    print("-" * 80)
    
    result = generate_treatment_prompt("Arthritis")
    print(f"""1. First, retrieve facts from knowledge base:
   - Drug: {result['context']['primary_drug']}
   - Mechanism: {result['context']['mechanism']}

2. Then, create enhanced prompt with facts:
   (See prompt above in Demo 2)

3. LLM generates response using YOUR knowledge:
   - Accurate and specific
   - Grounded in your ontology
   - Traceable to source
   - Up-to-date with your data""")
    print("-" * 80)
    
    input("\nPress Enter to continue...")


def demo_complete_workflow():
    """
    Demo 6: Complete RAG Workflow
    
    Shows the entire pipeline from user query to AI response.
    """
    print_section("DEMO 6: Complete RAG Workflow")
    
    user_query = "I have joint pain. What medication might help?"
    
    print(f"User Query: '{user_query}'")
    print("\n📋 RAG PIPELINE:")
    print("-" * 80)
    
    print("\n[Step 1] Understand Intent")
    print("  → Identified: User wants treatment for joint pain")
    print("  → Related disease: Arthritis (commonly causes joint pain)")
    
    print("\n[Step 2] RETRIEVE - Query Knowledge Base")
    print("  → Querying ontology with SPARQL...")
    
    drugs = query_drugs_for_disease("Arthritis")
    
    if drugs:
        print(f"  ✅ Retrieved {len(drugs)} relevant treatment(s)")
        for drug in drugs:
            print(f"     - {drug.get('drugLabel')}: {drug.get('mechanismLabel')}")
    
    print("\n[Step 3] AUGMENT - Enhance Prompt")
    print("  → Creating context-rich prompt...")
    
    result = generate_treatment_prompt("Arthritis")
    
    print("  ✅ Prompt enhanced with:")
    print(f"     - Drug information: {result['context']['primary_drug']}")
    print(f"     - Mechanism: {result['context']['mechanism']}")
    print(f"     - Number of retrieved facts: {result['metadata']['num_treatments']}")
    
    print("\n[Step 4] GENERATE - Send to LLM")
    print("  → Enhanced prompt ready for LLM")
    print("  → LLM generates informed response")
    
    print("\n[Step 5] Return Response")
    print("  → User receives accurate, grounded answer")
    
    print("\n" + "-" * 80)
    print("\n💡 KEY BENEFITS OF RAG:")
    print("  ✅ Reduces hallucinations")
    print("  ✅ Grounds responses in real knowledge")
    print("  ✅ Makes AI explainable and trustworthy")
    print("  ✅ Easy to update knowledge without retraining")
    
    input("\nPress Enter to finish...")


def main():
    """
    Run the complete demo workflow.
    """
    print("\n" + "=" * 80)
    print(" HEALTHCARE RAG SYSTEM - Complete Demo")
    print("=" * 80)
    print("\nThis demo will show you:")
    print("  1. How to retrieve knowledge from an ontology")
    print("  2. How to generate RAG-enhanced prompts")
    print("  3. Why RAG makes AI more accurate and trustworthy")
    print("\n" + "=" * 80)
    
    # Check connection first
    print("\n[Pre-flight Check] Testing Fuseki connection...")
    if not test_connection():
        print("\n❌ ERROR: Cannot connect to Fuseki!")
        print("\nTroubleshooting:")
        print("  1. Is Fuseki running? Check: docker ps")
        print("  2. Is it accessible? Visit: http://localhost:3030")
        print("  3. Is the ontology uploaded?")
        print("\nPlease fix the connection and try again.")
        return
    
    print("✅ Fuseki connection OK!")
    
    input("\nPress Enter to start the demo...")
    
    # Run all demos
    try:
        demo_basic_retrieval()
        demo_rag_prompt_generation()
        demo_symptom_analysis()
        demo_drug_comparison()
        demo_without_rag_vs_with_rag()
        demo_complete_workflow()
        
        print_section("Demo Complete!")
        print("🎉 You've successfully completed the RAG demo!")
        print("\nNext steps:")
        print("  1. Try running the API server: uvicorn src.api_server:app --reload")
        print("  2. Test endpoints: http://localhost:8000/docs")
        print("  3. Modify the ontology to add your own knowledge")
        print("  4. Integrate with a real LLM (OpenAI, Claude, etc.)")
        print("\n" + "=" * 80 + "\n")
    
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Thanks for watching!")
    except Exception as e:
        print(f"\n\n❌ Error during demo: {e}")
        print("Please check that Fuseki is running and the ontology is loaded.")


if __name__ == "__main__":
    main()