# Todo — Law as Code (OLL 2026)

## 1. Infrastructure Setup

- [x] `uv init` and project scaffolding
- [x] Add dependencies: dspy, jupyter, httpx, lxml
- [x] Create `src/oll_law_as_code/` package structure
- [x] Write `architecture.md`
- [ ] Configure DSPy LM backend (OpenAI / Anthropic / local)
- [ ] Set up `.env` for API keys

## 2. Fedlex Integration

- [ ] Research Fedlex SPARQL endpoint schema
- [ ] Write SPARQL query for DFTA articles (DBG / LIFD)
- [ ] Write SPARQL query for AHV articles (AHVG / LAVS)
- [ ] Implement `fedlex.py` — fetch and parse article text
- [ ] Cache fetched articles locally in `data/`
- [ ] Handle multilingual text (DE / FR / IT)

## 3. DSPy Pipeline

- [x] Define `LegalToCode` signature
- [x] Implement `LegalTransformer` module (ChainOfThought)
- [ ] Create first few-shot example (simple AHV contribution rule)
- [ ] Create 3–5 additional examples covering different legal patterns
- [ ] Choose target format: Catala vs OpenFisca vs plain Python
- [ ] Set up `BootstrapFewShot` optimizer
- [ ] Define evaluation metric (persona pass rate)
- [ ] Run first training/compilation loop

## 4. Validation Suite (Personas)

- [x] Define 5 Swiss test personas with profiles
- [ ] Compute expected AHV contribution values per persona
- [ ] Compute expected income tax values per persona
- [ ] Implement test runner that executes generated code against personas
- [ ] Add assertion-based pass/fail reporting
- [ ] Integrate persona tests as DSPy metric

## 5. Notebook Prototype

- [ ] Build interactive demo in `notebooks/01_prototype.ipynb`
- [ ] Demo: fetch article → transform → show generated code
- [ ] Demo: run generated code against one persona
- [ ] Visualize pipeline steps and intermediate reasoning

## 6. Stretch Goals

- [ ] Multi-article composition (rules that reference other articles)
- [ ] Temporal versioning (law valid from date X)
- [ ] French/Italian input support
- [ ] Export to standalone Catala `.catala_en` file
- [ ] CI pipeline for automated validation
