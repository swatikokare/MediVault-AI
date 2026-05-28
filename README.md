# MediVault AI

MediVault AI is a Streamlit-based medical document intelligence app for extracting grounded, source-backed answers from trusted PDF clinical references.

The app builds a local semantic search index using Sentence Transformers and NumPy, then retrieves relevant document chunks to answer user questions. It can optionally call a local Ollama model for answer generation, but it still provides useful retrieval output when Ollama is not available.

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Requirements](#requirements)
- [Setup](#setup)
- [Run](#run)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Optional: Local Ollama](#optional-local-ollama)
- [Troubleshooting](#troubleshooting)
- [Notes](#notes)

## Features

- Upload medical PDF documents for local indexing.
- Extract text, chunk long pages, and store embeddings locally.
- Search indexed content using semantic retrieval.
- Choose answer style: Patient friendly, Clinical summary, or Study notes.
- Display source citations with page numbers and similarity scores.
- Warn when questions include urgent medical red-flag terms.
- Clear or inspect the local vector index from the sidebar.
- Fallback retrieval output if Ollama generation fails.

## How It Works

1. The app extracts text from uploaded PDF pages using `pypdf`.
2. Text is split into overlapping chunks for better retrieval coverage.
3. Sentence embeddings are generated with `sentence-transformers/all-MiniLM-L6-v2`.
4. The local index is stored as `data/vector_index.pkl` and persists across sessions.
5. User questions are embedded and matched against indexed chunks.
6. Retrieved chunks are shown as sources, and the app attempts to generate a grounded answer via Ollama.
7. If Ollama is unavailable, the app returns the top retrieved passages instead.

## Requirements

- Python 3.11+ (recommended)
- `streamlit`
- `sentence-transformers`
- `huggingface_hub`
- `pypdf`
- `requests`
- `numpy`
- `reportlab`

All required packages are listed in `requirements.txt`.

## Setup

```powershell
cd medical_rag_chatbot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```powershell
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal. Upload a medical PDF, wait for indexing, and ask your question in the chat input.

## Usage

1. Upload a trusted medical PDF using the file uploader.
2. The app will save the file under `data/uploads` and index it.
3. Use the sidebar to select an Ollama model and answer style.
4. Enter a question or choose one of the quick query buttons.
5. Review the answer and the retrieved source pages in the chat view.

## Project Structure

- `app.py` - Main Streamlit application.
- `requirements.txt` - Python dependency list.
- `README.md` - Project documentation.
- `assets/` - UI illustration and design assets.
- `data/` - Local storage for uploads and the vector index.
- `create_sample_pdf.py` - Utility script to generate sample PDFs.
- `create_clinical_case_pdf.py` - Utility script to generate a clinical case PDF.
- `generate_project_report.py` - Generates a project report PDF.
- `sample_clinical_case_report.md` / `.pdf` - Example medical reference content.
- `sample_medical_reference.md` / `.pdf` - Example source document.

## Optional: Local Ollama

For generated answers, install Ollama and pull a compatible model:

```powershell
ollama pull llama3.2:1b
```

Leave the default model field as `llama3.2:1b`, or enter another local Ollama model name.

If Ollama is not running, the app will still function by showing the most relevant retrieved passages.

## Troubleshooting

- If the app cannot load the embedding model, verify you have internet access for the first run.
- If PDF text extraction returns no content, try a different PDF source or ensure the file is not scanned as an image.
- If Ollama generation fails, check that `http://localhost:11434` is reachable and the chosen model is installed.
- To reset the local index, use the "Clear local index" button in the sidebar.

## Notes

- Uploaded documents and embeddings are stored locally in `data/uploads` and `data/vector_index.pkl`.
- This app is intended for educational and reference use only, not medical diagnosis or professional advice.
- For severe, sudden, or urgent symptoms, seek immediate medical care.

## UI
<img width="1919" height="1199" alt="Screenshot 2026-05-28 192126" src="https://github.com/user-attachments/assets/09b6a6cc-177d-49d9-8479-1eab3335e289" />
<img width="1919" height="1199" alt="Screenshot 2026-05-28 190718" src="https://github.com/user-attachments/assets/1c7d39d6-4bfd-43c4-8965-ccd1200d18eb" />


