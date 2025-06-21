# CrewAI Citation Audit Pipeline

## Summary
The **CrewAI Citation Audit Pipeline** is designed to audit citation consistency in academic articles. It processes a PDF file, extracts citation tokens, samples a subset, fetches metadata (titles and abstracts) for the citations, computes semantic similarity between sentences and abstracts, logs mismatches, and calculates a quality score band (green/amber/red).

---

## Workflow
1. **Extract citation tokens**: Parses the PDF to identify citation tokens and their associated sentences.
2. **Sample tokens**: Selects 5% of the tokens for auditing.
3. **Fetch metadata**: Retrieves titles and abstracts for the sampled tokens using CrossRef and PubMed APIs.
4. **Compute similarity**: Calculates semantic similarity between the citation sentence and the abstract using OpenAI embeddings.
5. **Log mismatches**: Records mismatches (low similarity scores) in a CSV file for manual review.
6. **Calculate error percentage**: Computes the percentage of mismatches in the sample.
7. **Map quality score**: Maps the error percentage to a quality score and assigns a band (green/amber/red).

---

## Agents
Agents are modular components that perform specific tasks in the pipeline. Here are the agents and their roles:

### 1. **PaperFetcherAgent**
- **Role**: Fetches metadata (title and abstract) for citation tokens using CrossRef and PubMed APIs.
- **Tools**: SQLite database for caching results, HTTP requests for API calls.
- **Key Methods**:
  - `_query_crossref`: Fetches metadata from CrossRef.
  - `_query_pubmed`: Fetches metadata from PubMed.
  - `_lookup_cache`: Checks if metadata is cached locally.
  - `_save_cache`: Saves metadata to the cache.

### 2. **SemanticComparerAgent**
- **Role**: Computes semantic similarity between sentences and abstracts using OpenAI embeddings.
- **Tools**: OpenAI API for embeddings, NumPy for cosine similarity calculations.
- **Key Methods**:
  - `_embed`: Generates embeddings for text.
  - `run`: Computes cosine similarity between sentence and abstract embeddings.

### 3. **MismatchLoggerAgent**
- **Role**: Logs mismatches (low similarity scores) to a CSV file for manual auditing.
- **Tools**: CSV file handling.
- **Key Methods**:
  - `run`: Appends mismatches to the CSV file.

### 4. **ErrorCalculatorAgent**
- **Role**: Calculates the error percentage based on mismatches and sample size.
- **Tools**: Simple arithmetic.
- **Key Methods**:
  - `run`: Computes error percentage.

### 5. **ScoreMapperAgent**
- **Role**: Maps error percentage to a quality score and assigns a band (green/amber/red).
- **Tools**: Threshold-based mapping.
- **Key Methods**:
  - `run`: Maps error percentage to quality score and band.

---

## Tasks
Tasks are abstractions that invoke agents to perform specific operations. Here are the tasks and their roles:

### 1. **FetchPapersTask**
- **Role**: Fetches metadata for citation tokens using the `PaperFetcherAgent`.
- **Expected Output**: List of dictionaries containing token, title, and abstract.

### 2. **CompareSemanticTask**
- **Role**: Computes semantic similarity between sentences and abstracts using the `SemanticComparerAgent`.
- **Expected Output**: List of similarity scores.

### 3. **LogMismatchTask**
- **Role**: Logs mismatches to a CSV file using the `MismatchLoggerAgent`.
- **Expected Output**: Same list of records for downstream stats.

### 4. **ComputeErrorTask**
- **Role**: Computes error percentage using the `ErrorCalculatorAgent`.
- **Expected Output**: Float error percentage.

### 5. **MapScoreTask**
- **Role**: Maps error percentage to quality score and band using the `ScoreMapperAgent`.
- **Expected Output**: Dictionary with quality score and band.

---

## Crew
The **CitationAuditCrew** orchestrates the end-to-end pipeline by combining agents and tasks. It performs the following steps:
1. Samples 5% of citation tokens.
2. Fetches metadata for sampled tokens.
3. Computes semantic similarity between sentences and abstracts.
4. Flags mismatches based on similarity thresholds.
5. Logs mismatches to a CSV file.
6. Calculates error percentage.
7. Maps error percentage to quality score and band.

---

## Tools
The pipeline uses the following tools:
1. **SQLite Database**: Caches metadata fetched by the `PaperFetcherAgent`.
2. **CSV File**: Logs mismatches for manual auditing.
3. **OpenAI API**: Generates embeddings for semantic similarity calculations.
4. **CrossRef and PubMed APIs**: Fetches metadata for citation tokens.
5. **PDFMiner**: Extracts text from PDF files.

---

## Output
1. **CSV File**: Logs mismatches in `output/mismatches.csv`.
2. **Quality Score Band**: Prints the overall quality score and band (green/amber/red) to the console.
