# oll_2026_law_as_code
Law as code

Source : 
https://staging.openjustice.ai
https://www.lexfind.ch/fe/de/search

## Swiss Law as Code – Automated Semantic Transformation of Fiscal & Social Norms

## Organization:

## Event: Open Legal Lab (OLL) 2026 – Magglingen, Switzerland

### The Challenge: Bridging the "Translation Gap"

Swiss federalism and direct democracy create a unique challenge: legal norms like the Federal Act on Direct Federal Tax (DFTA) and Social Security (AHV) are updated frequently by popular vote, yet their digital implementation in administrative systems remains a slow, manual, and error-prone process.

This challenge asks: Can we use Large Language Models (LLMs) to automatically transform natural language Swiss law into verifiable, machine-executable code?

We are moving from "linear text" to "executable logic," turning the law itself into a shared digital infrastructure for a modern, transparent state.

### Objectives & Mission

Our goal for the OLL 2026 is to build a functional Proof-of-Concept (PoC) pipeline that:

* Fetches structured legal text from the Fedlex API using ELI identifiers.
* Transforms articles into formal programming languages like Catala (for high-assurance logic) or OpenFisca (for fiscal microsimulation).
* Validates the code to ensure arithmetic and logical correctness.

### The Technical Approach: Declarative AI & RAG

To solve the problem of "brittle" LLM outputs, we will pioneer a cutting-edge technical stack:

* DSPy (Declarative Self-improving Python): Instead of manual prompt engineering, we will write Python code that programs the LLM, using "Optimizers" to systematically refine the transformation logic.
* Grounded RAG with NotebookLM: We will provide the model with a "second brain" by attaching specifications for Catala/OpenFisca via Google NotebookLM or Gemini Notebooks. This ensures the LLM stays grounded in formal syntax and avoids hallucinations.
* Interactive Prototyping: The entire pipeline will be hosted in Jupyter Notebooks, allowing for real-time "Lawyer-in-the-Loop" validation of the generated code.

### Impact: Why Join Us?

By succeeding, we provide a blueprint for "Digital-Ready Legislation." Imagine a future where Swiss laws are published simultaneously as human-readable text and as an official logic "kernel" that powers all administrative software.
We are looking for:

* Legal Domain Experts: To help "Rulemap" the legal logic and verify legal fidelity.
* Python Developers: To build the DSPy pipeline and integrate formal language execution.
* Innovation Advocates: To help present the vision of an algorithmic, transparent rule of law.

Resource Suite needed: Fedlex SPARQL access, Catala/OpenFisca language specs, and a curated test dataset for validation.

## Let’s code the law. Join us at OLL 2026 to build the unified reasoning infrastructure for the Swiss digital state.

**Examples of legal texts to digest:**

**Federal Personnel Act (FPA)**

* [172.220.1 Bundespersonalgesetz vom 24. März 2000 (BPG)](https://www.fedlex.admin.ch/eli/cc/2001/123/de#art_17_a)
* [172.220.111.3 Bundespersonalverordnung vom 3. Juli 2001 (BPV)](https://www.fedlex.admin.ch/eli/cc/2001/319/de#art_64)
* [172.220.111.31 Verordnung des EFD vom 6. Dezember 2001 zur Bundespersonalverordnung (VBPV)](https://www.fedlex.admin.ch/eli/cc/2001/485/de#art_28https:/)
