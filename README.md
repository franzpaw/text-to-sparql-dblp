# SPARQL DBLP Connection

A Python-based Retrieval-Augmented Generation (RAG) pipeline that translates natural language questions into SPARQL queries for the DBLP Knowledge Graph.


## Installation

### Install uv

```bash
# Install uv using pip (if not already installed)
pip install uv
```

### Setup Project

1. Clone the repository and navigate to the project directory

2. Create and activate a virtual environment:
   ```bash
   uv venv
   .venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   uv pip install -e .
   ```

4. Set up environment variables:
   ```bash
   # Copy the example environment file
   copy .env.example .env
   # Edit .env and add your OpenAI API key
   ```

5. Run the project:
   ```bash
   python main.py
   ```
