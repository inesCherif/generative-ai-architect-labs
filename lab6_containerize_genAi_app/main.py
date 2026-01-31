# main.py
from fastapi import FastAPI, Request
import openai
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Read OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Create FastAPI app
app = FastAPI()

@app.post("/generate")
async def generate(request: Request):
    """
    Receive JSON request, call OpenAI API, return generated text
    """
    try:
        # 1. Parse request data
        data = await request.json()
        prompt = data.get("prompt", "Hello, world")
        
        # 2. Log the request
        logger.info(f"Request received, Prompt: {prompt[:50]}...")
        
        # 3. Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        
        # 4. Extract response content
        ai_response = response.choices[0].message["content"]
        
        # 5. Log response
        logger.info(f"Response length: {len(ai_response)} characters")
        
        # 6. Return JSON response
        return {
            "status": "success",
            "response": ai_response,
            "model": "gpt-3.5-turbo",
            "tokens_used": response.usage.total_tokens
        }
        
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "genai-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)