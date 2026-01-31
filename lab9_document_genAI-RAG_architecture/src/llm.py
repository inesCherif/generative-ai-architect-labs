"""
LLM Module (Language Model Integration)

This module handles:
- Communicating with OpenAI's GPT models
- Formatting prompts with retrieved context
- Generating responses

The LLM is the "brain" that reads the documents and generates answers!
"""

from openai import OpenAI
from typing import List
from document_loader import Document


class LLM:
    """
    Wrapper for OpenAI's language models
    """
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", 
                 temperature: float = 0.7, max_tokens: int = 500):
        """
        Initialize the LLM
        
        Args:
            api_key: OpenAI API key
            model: Model name (gpt-3.5-turbo, gpt-4, etc.)
            temperature: Creativity (0 = deterministic, 1 = creative)
            max_tokens: Maximum length of response
        """
        if not api_key:
            raise ValueError("OpenAI API key is required!")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        print(f"🤖 Initialized LLM: {model}")
        print(f"   Temperature: {temperature}")
        print(f"   Max tokens: {max_tokens}\n")
    
    def generate_response(self, query: str, context_documents: List[Document]) -> str:
        """
        Generate a response using the query and retrieved documents
        
        This is where RAG happens! We give the LLM:
        1. The user's question
        2. Relevant documents we found
        3. Instructions to answer based on those documents
        
        Args:
            query: The user's question
            context_documents: List of relevant documents
        
        Returns:
            The generated answer
        """
        # Build the context from documents
        context = self._build_context(context_documents)
        
        # Create the prompt
        prompt = self._create_prompt(query, context)
        
        print(f"🤔 Generating response for: '{query}'")
        print(f"   Using {len(context_documents)} documents as context...")
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant. Answer questions based on the provided context. If the context doesn't contain enough information, say so."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract the answer
            answer = response.choices[0].message.content
            
            print(f"✅ Response generated ({len(answer)} characters)\n")
            return answer
            
        except Exception as e:
            error_msg = f"Error generating response: {e}"
            print(f"❌ {error_msg}\n")
            return error_msg
    
    def _build_context(self, documents: List[Document]) -> str:
        """
        Build context string from retrieved documents
        
        Args:
            documents: List of Document objects
        
        Returns:
            Formatted context string
        """
        if not documents:
            return "No relevant documents found."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get('source', 'Unknown')
            content = doc.content.strip()
            
            context_parts.append(f"Document {i} (Source: {source}):\n{content}")
        
        return "\n\n".join(context_parts)
    
    def _create_prompt(self, query: str, context: str) -> str:
        """
        Create the final prompt for the LLM
        
        This combines the context and query in a way that encourages
        the LLM to use the documents to answer.
        
        Args:
            query: User's question
            context: Retrieved document context
        
        Returns:
            Formatted prompt
        """
        prompt = f"""Context Information:
{context}

Question: {query}

Instructions:
- Answer the question based on the context provided above
- If the context contains relevant information, use it in your answer
- If the context doesn't fully answer the question, say so
- Be concise and clear
- Cite which document(s) you used if relevant

Answer:"""
        
        return prompt


def test_llm(api_key: str):
    """
    Test the LLM module (requires valid API key)
    
    Args:
        api_key: OpenAI API key
    """
    if not api_key or api_key == "your-api-key-here":
        print("⚠️  Skipping LLM test - no API key provided")
        return
    
    print("\n🧪 Testing LLM Module\n")
    
    # Initialize LLM
    llm = LLM(api_key=api_key, temperature=0.5)
    
    # Create sample documents
    docs = [
        Document(
            content="RAG stands for Retrieval-Augmented Generation. It's a technique that combines document retrieval with language models to provide more accurate, grounded responses.",
            metadata={"source": "rag_intro.txt"}
        ),
        Document(
            content="Vector databases store embeddings and enable similarity search. They're essential for RAG systems to find relevant documents quickly.",
            metadata={"source": "vector_db.txt"}
        )
    ]
    
    # Test query
    query = "What is RAG and why is it useful?"
    
    # Generate response
    response = llm.generate_response(query, docs)
    
    print("="*60)
    print("QUESTION:", query)
    print("="*60)
    print("ANSWER:", response)
    print("="*60)


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    test_llm(api_key)