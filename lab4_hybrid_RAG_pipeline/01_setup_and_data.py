"""
OBJECTIVE:
Learn how to load and prepare sample documents for our RAG pipeline.
-> create a small knowledge base (dataset) of healthcare policy documents with text and metadata.        

CONCEPTS:
- Document loading: Getting text data from various sources
- Data preprocessing: Cleaning and structuring data
- Sample dataset: using healthcare policy documents as example

WHY THIS MATTERS:
RAG needs a knowledge base. This step creates sample documents about healthcare policies that our system will search through and use to answer questions (vector search, graph ,filters).
"""

import json
import os
from pathlib import Path

print("="*60)
print("STEP 1: Loading Sample Data")
print("="*60)

# ============================================================================
# CONCEPT: Sample Healthcare Documents
# ============================================================================
# In a real system, you'd load from a database, files, or APIs.
# For learning, we'll create sample healthcare policy documents.

sample_documents = [
    {
        "id": "doc_001",
        "text": "The Affordable Care Act (ACA) provides health insurance coverage to millions of Americans. It includes provisions for preventive care, mental health services, and prescription drug coverage. The ACA operates through state and federal health insurance marketplaces.",
        "category": "Healthcare",
        "region": "US",
        "topic": "Insurance Coverage"
    },
    {
        "id": "doc_002",
        "text": "Medicare is a federal health insurance program primarily for people 65 and older. It has four parts: Part A covers hospital stays, Part B covers doctor visits, Part C is Medicare Advantage, and Part D covers prescription drugs. Eligibility typically begins at age 65.",
        "category": "Healthcare",
        "region": "US",
        "topic": "Medicare"
    },
    {
        "id": "doc_003",
        "text": "Medicaid provides health coverage to low-income individuals and families. It is a joint federal and state program, meaning coverage can vary by state. Medicaid covers essential health benefits including emergency services, pregnancy care, and mental health treatment.",
        "category": "Healthcare",
        "region": "US",
        "topic": "Medicaid"
    },
    {
        "id": "doc_004",
        "text": "Health Savings Accounts (HSAs) allow individuals to save money tax-free for medical expenses. To qualify for an HSA, you must be enrolled in a high-deductible health plan. HSA funds can be used for qualified medical expenses including doctor visits, prescriptions, and dental care.",
        "category": "Healthcare",
        "region": "US",
        "topic": "Savings Accounts"
    },
    {
        "id": "doc_005",
        "text": "Preventive care services under most health insurance plans are covered at no cost. These include annual checkups, immunizations, cancer screenings, and wellness visits. The goal is to detect health issues early when they are most treatable.",
        "category": "Healthcare",
        "region": "US",
        "topic": "Preventive Care"
    },
    {
        "id": "doc_006",
        "text": "Mental health parity laws require insurance companies to cover mental health services at the same level as physical health services. This includes therapy, counseling, and psychiatric care. Coverage cannot have higher copays or more restrictive limits for mental health treatment.",
        "category": "Healthcare",
        "region": "US",
        "topic": "Mental Health"
    },
    {
        "id": "doc_007",
        "text": "Prescription drug coverage varies by insurance plan. Most plans use a formulary - a list of covered medications. Generic drugs typically have lower copays than brand-name drugs. Some plans require prior authorization for certain medications.",
        "category": "Healthcare",
        "region": "US",
        "topic": "Prescriptions"
    },
    {
        "id": "doc_008",
        "text": "The UK National Health Service (NHS) provides healthcare to all UK residents free at the point of use. It is funded through taxation. The NHS covers GP visits, hospital treatment, mental health services, and prescriptions with a standard charge in England.",
        "category": "Healthcare",
        "region": "UK",
        "topic": "NHS"
    },
    {
        "id": "doc_009",
        "text": "COBRA allows you to continue your employer health insurance after leaving a job. You pay the full premium plus an administrative fee. COBRA coverage typically lasts 18 months. This provides a bridge while you find new coverage.",
        "category": "Healthcare",
        "region": "US",
        "topic": "COBRA"
    },
    {
        "id": "doc_010",
        "text": "Telehealth services have expanded significantly, allowing patients to consult doctors remotely via video or phone. Many insurance plans now cover telehealth visits. This improves access to care, especially in rural areas or for those with mobility issues.",
        "category": "Healthcare",
        "region": "US",
        "topic": "Telehealth"
    }
]

print(f"\nCreated {len(sample_documents)} sample documents about healthcare") # docs number
print("\nSample document preview:")
print(f"ID: {sample_documents[0]['id']}")
print(f"Category: {sample_documents[0]['category']}")
print(f"Region: {sample_documents[0]['region']}")
print(f"Topic: {sample_documents[0]['topic']}")
print(f"Text: {sample_documents[0]['text'][:100]}...")

# ============================================================================
# SAVE DATA TO FILE so other scripts can use it
# ============================================================================

data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

output_file = data_dir / "sample_documents.json"

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(sample_documents, f, indent=2, ensure_ascii=False)

print(f"\n Data saved to: {output_file}")
print(f"   File size: {output_file.stat().st_size:,} bytes")

# ============================================================================
# DISPLAY STATISTICS
# ============================================================================
print("\n" + "="*60)
print("DATA STATISTICS")
print("="*60)

categories = set(doc['category'] for doc in sample_documents)
regions = set(doc['region'] for doc in sample_documents)
topics = set(doc['topic'] for doc in sample_documents)

print(f"Total documents: {len(sample_documents)}")
print(f"Categories: {', '.join(categories)}")
print(f"Regions: {', '.join(regions)}")
print(f"Topics: {len(topics)} different topics")
print(f"Average text length: {sum(len(doc['text']) for doc in sample_documents) // len(sample_documents)} characters")
