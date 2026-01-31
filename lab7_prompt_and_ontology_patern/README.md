# Lab 7: Prompt + Ontology Pattern with SPARQL + Internal API

## 🎯 Learning Objectives

By completing this lab, you will understand:

1. **Ontology**: A formal way to represent knowledge and relationships
   - Think of it as a "smart database" that understands relationships
   - Example: "Ibuprofen TREATS Arthritis" - not just data, but meaningful connections

2. **SPARQL**: Query language for ontologies (like SQL for knowledge graphs)
   - Retrieve structured knowledge to enhance AI responses
   - Make AI answers more accurate and explainable

3. **RAG Pattern**: Retrieval-Augmented Generation
   - RETRIEVE relevant facts from knowledge base
   - AUGMENT the AI prompt with those facts
   - GENERATE accurate, grounded responses

4. **REST API**: Expose your system as a web service
   - Other applications can use your knowledge system
   - Build modular, reusable AI components

## 📁 Project Structure

```
lab7_prompt_and_ontology_pattern/
│
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── setup_guide.md           # Detailed setup instructions
│
├── ontology/
│   ├── healthcare.ttl       # Knowledge base (Turtle format)
│   └── sample_queries.sparql # Example SPARQL queries
│
├── src/
│   ├── __init__.py
│   ├── sparql_query.py      # SPARQL query functions
│   ├── prompt_generator.py  # Dynamic prompt creation
│   └── api_server.py        # FastAPI REST server
│
├── tests/
│   └── test_queries.py      # Test your SPARQL queries
│
└── examples/
    └── demo_workflow.py     # End-to-end example
```

## 🚀 Quick Start

1. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Start the triple store (Fuseki)**

   ```bash
   docker run -d -p 3030:3030 --name fuseki stain/jena-fuseki
   ```

3. **Upload the ontology**
   - Visit http://localhost:3030
   - Create dataset "healthcare"
   - Upload `ontology/healthcare.ttl`

4. **Run the API server**

   ```bash
   uvicorn src.api_server:app --reload
   ```

5. **Test the endpoint**
   ```bash
   curl http://localhost:8000/generate-prompt
   ```
