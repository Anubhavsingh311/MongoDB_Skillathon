# 01 — Database Fundamentals

## What is a Database?

A **database** is an organized collection of structured or unstructured information stored on a machine or in the cloud. The key differentiator from a flat file (e.g., a spreadsheet) is the inclusion of a **Database Management System (DBMS)**.

### DBMS Responsibilities
- Handles user requests and data protocols
- Performs **CRUD** operations: **C**reate, **R**etrieve, **U**pdate, **D**elete
- Manages hardware, users, and permissions
- Maintains security and data integrity
- Handles backups and recovery

---

## SQL vs. NoSQL

| | SQL | NoSQL |
|---|---|---|
| Full name | Structured Query Language | Not Only SQL |
| Also called | Relational | Non-relational |
| Created | 1970s | Later, for modern use cases |
| Data structure | Tables (rows + columns) | Varies (documents, key-value, graph, column) |
| Schema | Rigid, enforced | Flexible, optional |

---

## Types of NoSQL Databases

### Key-Value
- Pairs a unique key with a collection of values
- Keys can be text or binary
- No complex queries; lookup is direct via key
- Great for large datasets; weak on complex relationships

### Document
- Data stored in a single document within a collection
- Uses markup (e.g., JSON/BSON) to identify fields and values
- Handles **polymorphic data** (inconsistent structure across records)
- Maps closely to objects in OOP — less translation needed in app code

### Column
- Stores records by column instead of row
- Same data type per column → better compression → faster reads
- Ideal for analytical workloads on a small subset of columns

### Graph
- Stores data as **nodes** (entities) and **edges** (relationships)
- Best for relationship-heavy use cases (e.g., social networks)
- More efficient traversal of connected data than SQL joins
- Usually run alongside a primary database, not as a standalone solution

---

## Schemas and Data Modeling

- **Schema** — the rules governing how data is stored (field types, value constraints, character limits)
- **Data model** — the conceptual organization of data and relationships between entities (often visualized as a diagram)

> Think of the **data model** as the blueprint and the **schema** as the building code enforcing it.

### SQL vs. NoSQL Schema Flexibility
- SQL: Adding a new field requires updating every existing row — costly and complex
- NoSQL: No fixed table structure; add fields only where needed, leave others untouched

---

## Types of Data

| Type | Description | Examples |
|---|---|---|
| **Structured** | Highly organized, predictable format | SQL tables, CSVs |
| **Semi-structured** | Organized but not strictly formatted | JSON, XML |
| **Unstructured** | No organization or categorization | Videos, images, audio, raw text |

> Unstructured data makes up the majority of data in existence. It is commonly used to train and provide context to AI models.

---

## Key Takeaways

- A database is more than a file — it includes a DBMS that manages access, integrity, and operations.
- SQL = tabular, relational; NoSQL = flexible, varied structure.
- Schemas define rules; data models define organization.
- Not all data is the same — structured, semi-structured, and unstructured each have different storage and access requirements.
