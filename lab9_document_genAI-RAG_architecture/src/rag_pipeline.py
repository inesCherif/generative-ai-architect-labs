"""
RAG Pipeline - The Complete System!

This is where everything comes together:
1. Load documents
2. Create embeddings
3. Store in vector database
4. Answer questions using retrieval + LLM

This is the "main controller" of your RAG system.
"""

from pathlib import Path
from typing import List, Optional
import time

from config import Config
from document_loader import DocumentLoader, Document
from embeddings import EmbeddingModel
from vector_store import VectorStore
from llm import LLM


class RAGPipeline:
    """
    Complete RAG (Retrieval-Augmented Generation) Pipeline
    
    This orchestrates all components to create an intelligent Q&A system.
    """
    
    def __init__(self, config: Config = None):
        """
        Initialize the RAG pipeline
        
        Args:
            config: Configuration object (uses default if not provided)
        """
        self.config = config or Config
        
        print("\n" + "="*60)
        print("🚀 INITIALIZING RAG PIPELINE")
        print("="*60 + "\n")
        
        # Initialize components
        self.document_loader = DocumentLoader(self.config.DATA_DIR)
        self.embedding_model = EmbeddingModel(self.config.EMBEDDING_MODEL)
        self.vector_store: Optional[VectorStore] = None
        self.llm: Optional[LLM] = None
        
        # Initialize LLM if API key is available
        if self.config.OPENAI_API_KEY:
            self.llm = LLM(
                api_key=self.config.OPENAI_API_KEY,
                model=self.config.LLM_MODEL,
                temperature=self.config.LLM_TEMPERATURE,
                max_tokens=self.config.LLM_MAX_TOKENS
            )
        else:
            print("⚠️  LLM not initialized - OpenAI API key not found")
            print("   You can still build the vector database!\n")
    
    def build_index(self, force_rebuild: bool = False):
        """
        Build the vector database from documents
        
        Steps:
        1. Load documents from data folder
        2. Split into chunks
        3. Create embeddings
        4. Store in FAISS vector database
        5. Save to disk
        
        Args:
            force_rebuild: If True, rebuild even if index exists
        """
        print("\n" + "="*60)
        print("🔨 BUILDING VECTOR DATABASE")
        print("="*60 + "\n")
        
        # Check if index already exists
        if not force_rebuild and self.config.VECTOR_DB_PATH.exists():
            print(f"📂 Vector database already exists at {self.config.VECTOR_DB_PATH}")
            user_input = input("   Rebuild? (y/n): ").strip().lower()
            if user_input != 'y':
                print("   Loading existing database...\n")
                self.load_index()
                return
        
        start_time = time.time()
        
        # Step 1: Load documents
        print("Step 1/4: Loading documents...")
        documents = self.document_loader.load_documents()
        
        if not documents:
            print("❌ No documents found! Add .txt files to the data folder.")
            return
        
        # Step 2: Split into chunks
        print("Step 2/4: Splitting documents into chunks...")
        chunks = self.document_loader.split_documents(
            documents,
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP
        )
        
        # Step 3: Create embeddings
        print("Step 3/4: Creating embeddings...")
        chunk_texts = [chunk.content for chunk in chunks]
        embeddings = self.embedding_model.embed_documents(chunk_texts)
        
        # Step 4: Build vector store
        print("Step 4/4: Building vector store...")
        self.vector_store = VectorStore(dimension=self.embedding_model.dimension)
        self.vector_store.add_documents(chunks, embeddings)
        
        # Save to disk
        print("💾 Saving vector database...")
        self.vector_store.save(self.config.VECTOR_DB_PATH)
        
        elapsed = time.time() - start_time
        print(f"\n✅ Index built successfully in {elapsed:.2f} seconds!")
        print("="*60 + "\n")
    
    def load_index(self):
        """
        Load an existing vector database from disk
        """
        if not self.config.VECTOR_DB_PATH.exists():
            print(f"❌ Vector database not found at {self.config.VECTOR_DB_PATH}")
            print("   Run build_index() first!")
            return False
        
        print("📂 Loading vector database...")
        self.vector_store = VectorStore.load(
            self.config.VECTOR_DB_PATH,
            dimension=self.embedding_model.dimension
        )
        print("✅ Vector database loaded!\n")
        return True
    
    def query(self, question: str, top_k: int = None) -> dict:
        """
        Answer a question using RAG
        
        Steps:
        1. Convert question to embedding
        2. Search vector database for similar documents
        3. Pass documents + question to LLM
        4. Return answer
        
        Args:
            question: The user's question
            top_k: Number of documents to retrieve (uses config default if not specified)
        
        Returns:
            Dictionary with answer, sources, and metadata
        """
        if self.vector_store is None:
            return {
                "error": "Vector store not loaded. Run build_index() or load_index() first!"
            }
        
        if self.llm is None:
            return {
                "error": "LLM not initialized. Add OPENAI_API_KEY to .env file!"
            }
        
        top_k = top_k or self.config.TOP_K_RESULTS
        
        print("\n" + "="*60)
        print(f"❓ QUESTION: {question}")
        print("="*60 + "\n")
        
        start_time = time.time()
        
        # Step 1: Embed the question
        print("🔄 Step 1/3: Creating question embedding...")
        question_embedding = self.embedding_model.embed_text(question)
        
        # Step 2: Search for relevant documents
        print(f"🔍 Step 2/3: Searching for top {top_k} relevant documents...")
        results = self.vector_store.search(question_embedding, top_k=top_k)
        
        print(f"\n📚 Retrieved {len(results)} documents:")
        for i, (doc, score) in enumerate(results, 1):
            source = doc.metadata.get('source', 'Unknown')
            print(f"   {i}. {source} (similarity: {score:.4f})")
            print(f"      Preview: {doc.content[:80]}...")
        print()
        
        # Step 3: Generate answer using LLM
        print("🤖 Step 3/3: Generating answer with LLM...")
        documents = [doc for doc, score in results]
        answer = self.llm.generate_response(question, documents)
        
        elapsed = time.time() - start_time
        
        print("="*60)
        print("💡 ANSWER:")
        print("="*60)
        print(answer)
        print("="*60)
        print(f"⏱️  Completed in {elapsed:.2f} seconds\n")
        
        # Return structured result
        return {
            "question": question,
            "answer": answer,
            "sources": [
                {
                    "content": doc.content,
                    "metadata": doc.metadata,
                    "similarity": score
                }
                for doc, score in results
            ],
            "time_taken": elapsed
        }
    
    def interactive_mode(self):
        """
        Interactive Q&A mode
        
        Allows you to ask multiple questions in a conversation-like interface
        """
        if self.vector_store is None:
            print("❌ Please build or load the index first!")
            return
        
        if self.llm is None:
            print("❌ LLM not available. Add OPENAI_API_KEY to .env file!")
            return
        
        print("\n" + "="*60)
        print("💬 INTERACTIVE RAG MODE")
        print("="*60)
        print("Ask questions about your documents!")
        print("Type 'quit' or 'exit' to stop")
        print("="*60 + "\n")
        
        while True:
            try:
                # Get user input
                question = input("You: ").strip()
                
                if not question:
                    continue
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!\n")
                    break
                
                # Answer the question
                self.query(question)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")


def main():
    """
    Main function to demonstrate the RAG pipeline
    """
    # Validate configuration
    config = Config
    config.print_config()
    
    if not config.validate():
        print("\n⚠️  Please fix configuration issues before continuing.")
        return
    
    # Initialize pipeline
    pipeline = RAGPipeline(config)
    
    # Build or load index
    print("\n" + "="*60)
    print("Choose an option:")
    print("1. Build new vector database")
    print("2. Load existing vector database")
    print("3. Build and then start interactive Q&A")
    print("="*60)
    
    choice = input("\nYour choice (1-3): ").strip()
    
    if choice == '1':
        pipeline.build_index(force_rebuild=True)
    elif choice == '2':
        pipeline.load_index()
    elif choice == '3':
        pipeline.build_index()
        pipeline.interactive_mode()
    else:
        print("Invalid choice!")
        return
    
    # If not in interactive mode, ask if user wants to start it
    if choice in ['1', '2']:
        start_interactive = input("\nStart interactive Q&A mode? (y/n): ").strip().lower()
        if start_interactive == 'y':
            pipeline.interactive_mode()


if __name__ == "__main__":
    main()