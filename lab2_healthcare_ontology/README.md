# Mini Ontology Lab – Healthcare Domain

## Objective

Understand how to represent knowledge intelligently,  
store it in a Graph Database,  
and query it with smart questions.

> Knowledge Representation: no AI, no LLM, no RAG.

---

## Tools Used

- **Protégé**: to design the ontology (classes, properties, individuals)
- **Neo4j**: to store the knowledge graph and query relationships using Cypher

---

## Key Concepts Learned

- Difference between **data** and **knowledge**
- **Ontology ≠ Database**
- **Graph ≠ Table**
- Linking **Ontology → Knowledge Graph**
- Linking **Knowledge Graph → Agents / RAG** (conceptually)

---

## Lab Summary

1. **Create ontology in Protégé**
   - Classes: Patient, Doctor, Disease, Treatment
   - Object Properties: hasDisease, receivesTreatment, treatedBy
   - Data Properties: hasAge, hasName
   - Individuals: Alice (Patient), DrSmith (Doctor), Diabetes (Disease), Insulin (Treatment)

2. **Export ontology**
   - RDF/Turtle format (`healthcare.ttl`)

3. **Load into Neo4j**
   - Install Neosemantics (n10s) plugin
   - Initialize: `CALL n10s.graphconfig.init()`
   - Import RDF: `CALL n10s.rdf.import.fetch("file:///healthcare.ttl", "Turtle")`

4. **Query the knowledge graph using Cypher**
   - Find all patients
   - Find patients and their diseases
   - Find patients treated by a specific doctor
   - Count patients per disease

> **Takeaway:** Ontologies model domain knowledge, RDF represents it, Neo4j stores it as a graph, and Cypher queries relationships efficiently.
