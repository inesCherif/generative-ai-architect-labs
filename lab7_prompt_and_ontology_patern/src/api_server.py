"""
FastAPI REST API Server

This module exposes our RAG system as a REST API that other applications can use.

WHAT IS A REST API?
- A way for applications to talk to each other over HTTP
- Uses URLs (endpoints) to access different functions
- Returns data in JSON format

WHY BUILD AN API?
- Makes your RAG system reusable
- Other apps (chatbots, websites, mobile apps) can use it
- Separates knowledge retrieval from presentation

ENDPOINTS WE'LL CREATE:
- GET /health - Check if API is running
- GET /drugs - List all available drugs
- GET /treatment/{disease} - Get treatment info for a disease
- GET /symptoms/{disease} - Get symptoms of a disease
- GET /compare/{drug1}/{drug2} - Compare two drugs
- POST /generate-prompt - Generate custom prompts
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

# Import our custom modules
from src.sparql_query import (
    query_drugs_for_disease,
    query_disease_symptoms,
    query_drug_details,
    query_all_drugs,
    test_connection
)
from src.prompt_generator import (
    generate_treatment_prompt,
    generate_symptom_prompt,
    generate_drug_comparison_prompt,
    generate_simple_prompt,
    generate_discovery_prompt
)


# ========================================
# FASTAPI APP INITIALIZATION
# ========================================

app = FastAPI(
    title="Healthcare RAG API",
    description="Retrieval-Augmented Generation API for Healthcare Knowledge",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc"  # ReDoc UI at /redoc
)

# Enable CORS (allows requests from web browsers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================================
# REQUEST/RESPONSE MODELS
# ========================================

class PromptRequest(BaseModel):
    """
    Model for custom prompt generation requests.
    
    This defines what data the client must send when requesting a prompt.
    """
    user_question: str
    disease_name: Optional[str] = None
    drug_name: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "user_question": "How does Ibuprofen help with pain?",
                "disease_name": "Arthritis"
            }
        }


class PromptResponse(BaseModel):
    """
    Model for prompt generation responses.
    
    This defines what data the API will return.
    """
    prompt: Optional[str]
    context: Optional[dict]
    metadata: dict


# ========================================
# API ENDPOINTS
# ========================================

@app.get("/")
async def root():
    """
    Root endpoint - API welcome message.
    
    Try it: http://localhost:8000/
    """
    return {
        "message": "Healthcare RAG API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "drugs": "/drugs",
            "treatment": "/treatment/{disease}",
            "symptoms": "/symptoms/{disease}",
            "compare": "/compare/{drug1}/{drug2}",
            "generate": "/generate-prompt"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Verifies that:
    1. API server is running
    2. Fuseki connection is working
    3. Ontology is accessible
    
    Try it: http://localhost:8000/health
    """
    # Test connection to Fuseki
    fuseki_ok = test_connection()
    
    # Test ontology query
    drugs = query_all_drugs()
    ontology_ok = len(drugs) > 0
    
    status = "healthy" if (fuseki_ok and ontology_ok) else "degraded"
    
    return {
        "status": status,
        "fuseki_connection": "OK" if fuseki_ok else "FAILED",
        "ontology_loaded": "OK" if ontology_ok else "FAILED",
        "drug_count": len(drugs) if drugs else 0
    }


@app.get("/drugs")
async def get_all_drugs():
    """
    List all drugs in the knowledge base.
    
    Returns:
        List of drugs with basic information
    
    Try it: http://localhost:8000/drugs
    """
    drugs = query_all_drugs()
    
    if not drugs:
        raise HTTPException(
            status_code=404,
            detail="No drugs found in knowledge base. Check if ontology is loaded."
        )
    
    return {
        "total": len(drugs),
        "drugs": drugs
    }


@app.get("/treatment/{disease}")
async def get_treatment_info(disease: str):
    """
    Get treatment information for a specific disease.
    
    This endpoint demonstrates RAG:
    - Retrieves treatment knowledge from ontology
    - Generates an AI-ready prompt
    - Returns both for transparency
    
    Args:
        disease: Name of the disease (e.g., "Arthritis")
    
    Try it: http://localhost:8000/treatment/Arthritis
    """
    result = generate_treatment_prompt(disease)
    
    if not result['prompt']:
        raise HTTPException(
            status_code=404,
            detail=f"No treatment information found for {disease}"
        )
    
    return result


@app.get("/symptoms/{disease}")
async def get_symptom_info(disease: str):
    """
    Get symptom information for a disease.
    
    Args:
        disease: Name of the disease
    
    Try it: http://localhost:8000/symptoms/Diabetes
    """
    result = generate_symptom_prompt(disease)
    
    if not result['prompt']:
        raise HTTPException(
            status_code=404,
            detail=f"No symptom information found for {disease}"
        )
    
    return result


@app.get("/compare/{drug1}/{drug2}")
async def compare_drugs(drug1: str, drug2: str):
    """
    Compare two drugs.
    
    Args:
        drug1: First drug name
        drug2: Second drug name
    
    Try it: http://localhost:8000/compare/Ibuprofen/Aspirin
    """
    result = generate_drug_comparison_prompt(drug1, drug2)
    
    if not result['prompt']:
        raise HTTPException(
            status_code=404,
            detail=f"Could not compare {drug1} and {drug2}. Check if both exist in knowledge base."
        )
    
    return result


@app.get("/drug/{drug_name}")
async def get_drug_details(drug_name: str):
    """
    Get detailed information about a specific drug.
    
    Args:
        drug_name: Name of the drug
    
    Try it: http://localhost:8000/drug/Ibuprofen
    """
    details = query_drug_details(drug_name)
    
    if not details:
        raise HTTPException(
            status_code=404,
            detail=f"Drug '{drug_name}' not found in knowledge base"
        )
    
    return details


@app.post("/generate-prompt")
async def generate_custom_prompt(request: PromptRequest):
    """
    Generate a custom prompt based on user question.
    
    This is the most flexible endpoint - accepts any question
    and generates an appropriate RAG-enhanced prompt.
    
    Request body:
        {
            "user_question": "How does Ibuprofen work?",
            "disease_name": "Arthritis"  (optional)
        }
    
    Try it: Send POST request to http://localhost:8000/generate-prompt
    """
    if request.disease_name:
        # If disease specified, use treatment prompt
        prompt = generate_simple_prompt(
            request.user_question,
            request.disease_name
        )
        
        return {
            "prompt": prompt,
            "context": {
                "question": request.user_question,
                "disease": request.disease_name
            },
            "metadata": {
                "rag_pattern": "simple_retrieval"
            }
        }
    
    else:
        # No specific disease - return discovery prompt
        result = generate_discovery_prompt()
        return result


@app.get("/discover")
async def discover_knowledge():
    """
    Discover what's available in the knowledge base.
    
    Useful for exploratory queries or showing capabilities.
    
    Try it: http://localhost:8000/discover
    """
    result = generate_discovery_prompt()
    return result


@app.get("/query-raw")
async def raw_query(
    disease: Optional[str] = Query(None, description="Disease name"),
    drug: Optional[str] = Query(None, description="Drug name")
):
    """
    Raw query endpoint for direct ontology access.
    
    Query parameters:
        ?disease=Arthritis - Get drugs for disease
        ?drug=Ibuprofen - Get drug details
    
    Try it: http://localhost:8000/query-raw?disease=Arthritis
    """
    if disease:
        drugs = query_drugs_for_disease(disease)
        return {"query_type": "disease", "disease": disease, "results": drugs}
    
    elif drug:
        details = query_drug_details(drug)
        return {"query_type": "drug", "drug": drug, "results": details}
    
    else:
        raise HTTPException(
            status_code=400,
            detail="Please specify either 'disease' or 'drug' parameter"
        )


# ========================================
# STARTUP/SHUTDOWN EVENTS
# ========================================

@app.on_event("startup")
async def startup_event():
    """
    Runs when the API starts.
    
    Good place to:
    - Test connections
    - Load resources
    - Initialize services
    """
    print("=" * 60)
    print("🚀 Healthcare RAG API Starting...")
    print("=" * 60)
    
    # Test Fuseki connection
    if test_connection():
        print("✅ Fuseki connection: OK")
        
        # Check if ontology is loaded
        drugs = query_all_drugs()
        if drugs:
            print(f"✅ Ontology loaded: {len(drugs)} drugs found")
        else:
            print("⚠️  Warning: Ontology appears empty")
    else:
        print("❌ Fuseki connection: FAILED")
        print("   Make sure Fuseki is running: docker ps")
    
    print("=" * 60)
    print("📚 API Documentation: http://localhost:8000/docs")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Runs when the API shuts down.
    
    Good place to:
    - Close connections
    - Save state
    - Cleanup resources
    """
    print("\n👋 Healthcare RAG API shutting down...")


# ========================================
# MAIN - Run the server
# ========================================

if __name__ == "__main__":
    """
    Run the FastAPI server.
    
    Usage:
        python src/api_server.py
    
    Or use uvicorn directly:
        uvicorn src.api_server:app --reload
    """
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",  # Listen on all network interfaces
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )