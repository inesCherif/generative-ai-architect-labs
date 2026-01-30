# RDF Knowledge Graph Lab

**Goal:** Convert `products.csv` to RDF, upload to online triple store, query with SPARQL.

**Dataset:** 100 products, columns: Index, Name, Description, Brand, Category, Price, Currency, Stock, EAN, Color, Size, Availability, Internal ID.

**Steps:**

1. **Prepare CSV** - ensure clean, consistent data.
2. **Convert to RDF** - use RDFLib in Python → `products.ttl`.
3. **Upload RDF** - GraphDB Free online repository `enterpriseKG`.
4. **SPARQL queries** - retrieve products, categories, prices.

**Outcome:**

- CSV → RDF → Knowledge Graph
- SPARQL queries executed successfully

**Tools:** Python, RDFLib, GraphDB, SPARQL
