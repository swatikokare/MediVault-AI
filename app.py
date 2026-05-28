from __future__ import annotations

import hashlib
import base64
import json
import pickle
import textwrap
from pathlib import Path

import numpy as np
import requests
import streamlit as st
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


APP_DIR = Path(__file__).parent
ASSET_DIR = APP_DIR / "assets"
HERO_IMAGE = ASSET_DIR / "medivault-hero.svg"
DATA_DIR = APP_DIR / "data"
INDEX_PATH = DATA_DIR / "vector_index.pkl"
UPLOAD_DIR = DATA_DIR / "uploads"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_OLLAMA_MODEL = "llama3.2:1b"
ANSWER_MODES = {
    "Patient friendly": "Use plain language. Explain medical terms briefly. Keep the tone calm and practical.",
    "Clinical summary": "Use concise clinical language. Organize details for a healthcare or life-sciences reader.",
    "Study notes": "Use bullet-style study notes with key facts, mechanisms, and source-grounded details.",
}
RED_FLAG_TERMS = [
    "chest pain",
    "difficulty breathing",
    "shortness of breath",
    "stroke",
    "seizure",
    "unconscious",
    "severe bleeding",
    "suicidal",
    "poisoning",
    "overdose",
    "anaphylaxis",
    "blue lips",
    "worst headache",
    "confusion",
    "pregnant",
    "high fever",
]

APP_CSS = """
<style>
    :root {
        --med-bg: #f4f9fb;
        --med-panel: #ffffff;
        --med-panel-soft: #eef8f7;
        --med-line: #cfe3e8;
        --med-text: #12323f;
        --med-muted: #55707b;
        --med-primary: #0f766e;
        --med-primary-dark: #115e59;
        --med-blue: #2563a8;
        --med-alert-bg: #fff7ed;
        --med-alert-line: #ea580c;
        --med-alert-text: #7c2d12;
    }
    .stApp {
        background: var(--med-bg);
        color: var(--med-text);
    }
    .block-container {
        max-width: 1180px;
        padding-top: 1.4rem;
        padding-bottom: 2rem;
    }
    [data-testid="stSidebar"] {
        background: #eaf6f6;
        border-right: 1px solid var(--med-line);
    }
    h1, h2, h3 {
        letter-spacing: 0;
        color: var(--med-text);
    }
    .app-header {
        border: 1px solid var(--med-line);
        border-radius: 8px;
        padding: 22px 24px;
        background: linear-gradient(135deg, #ffffff 0%, #f0fbfa 100%);
        margin-bottom: 18px;
        box-shadow: 0 8px 26px rgba(15, 118, 110, 0.08);
        display: grid;
        grid-template-columns: minmax(0, 1fr) minmax(220px, 360px);
        gap: 18px;
        align-items: center;
    }
    .app-header h1 {
        font-size: 2.35rem;
        line-height: 1.15;
        margin: 0 0 8px 0;
        color: var(--med-text);
    }
    .app-header p {
        margin: 0;
        color: var(--med-muted);
        font-size: 1rem;
    }
    .hero-image {
        width: 100%;
        border-radius: 8px;
        overflow: hidden;
        background: transparent;
    }
    .hero-image img {
        display: block;
        width: 100%;
        height: auto;
    }
    .workflow-panel {
        border: 1px solid var(--med-line);
        border-radius: 8px;
        padding: 16px;
        background: rgba(255, 255, 255, 0.78);
        margin-bottom: 14px;
        box-shadow: 0 6px 18px rgba(15, 118, 110, 0.05);
    }
    .workflow-panel strong {
        color: var(--med-primary-dark);
    }
    @media (max-width: 900px) {
        .app-header {
            grid-template-columns: 1fr;
        }
        .hero-image {
            max-width: 420px;
        }
    }
    .status-strip {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 14px;
    }
    .status-pill {
        border: 1px solid var(--med-line);
        border-radius: 999px;
        padding: 5px 10px;
        color: var(--med-primary-dark);
        background: var(--med-panel-soft);
        font-size: 0.85rem;
        white-space: nowrap;
    }
    .medical-alert {
        border-left: 4px solid var(--med-alert-line);
        background: var(--med-alert-bg);
        color: var(--med-alert-text);
        padding: 12px 14px;
        border-radius: 6px;
        margin: 10px 0 18px 0;
    }
    .section-label {
        color: var(--med-primary-dark);
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
    }
    .source-chip {
        display: inline-block;
        border: 1px solid #b7d9d6;
        border-radius: 999px;
        padding: 4px 9px;
        margin: 0 6px 6px 0;
        background: #edfafa;
        color: var(--med-primary-dark);
        font-size: 0.82rem;
    }
    .stButton > button {
        border-radius: 7px;
        border-color: #9ccfcc;
        color: var(--med-primary-dark);
        background: #ffffff;
        min-height: 2.45rem;
    }
    .stButton > button:hover {
        border-color: var(--med-primary);
        color: #ffffff;
        background: var(--med-primary);
    }
    .stChatMessage {
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.72);
        border: 1px solid rgba(207, 227, 232, 0.7);
    }
    div[data-testid="stMetric"] {
        background: var(--med-panel);
        border: 1px solid var(--med-line);
        border-radius: 8px;
        padding: 12px 14px;
    }
    div[data-testid="stMetricValue"] {
        color: var(--med-primary-dark);
    }
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.72);
        border: 1px dashed #9ccfcc;
        border-radius: 8px;
        padding: 10px;
    }
    .stAlert {
        border-radius: 8px;
    }
</style>
"""


st.set_page_config(page_title="MediVault AI", layout="wide")


def inject_styles() -> None:
    st.markdown(APP_CSS, unsafe_allow_html=True)


def svg_data_uri(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


@st.cache_resource(show_spinner="Loading embedding model...")
def load_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL)


def file_hash(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()[:16]


def read_pdf_text(pdf_path: Path) -> list[dict]:
    reader = PdfReader(str(pdf_path))
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = " ".join(text.split())
        if text:
            pages.append({"page": index, "text": text})
    return pages


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> list[str]:
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be larger than overlap")

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap
    return chunks


def empty_index() -> dict:
    return {"documents": [], "metadatas": [], "embeddings": np.empty((0, 384), dtype=np.float32)}


def load_index() -> dict:
    if not INDEX_PATH.exists():
        return empty_index()
    with INDEX_PATH.open("rb") as file:
        return pickle.load(file)


def save_index(index: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with INDEX_PATH.open("wb") as file:
        pickle.dump(index, file)


def index_pdf(pdf_path: Path, document_id: str) -> int:
    model = load_embedding_model()
    index = load_index()

    if any(metadata["document_id"] == document_id for metadata in index["metadatas"]):
        return 0

    pages = read_pdf_text(pdf_path)
    documents = []
    metadatas = []

    for page in pages:
        for chunk_index, chunk in enumerate(chunk_text(page["text"])):
            documents.append(chunk)
            metadatas.append(
                {
                    "document_id": document_id,
                    "source": pdf_path.name,
                    "page": page["page"],
                    "chunk": chunk_index,
                }
            )

    if not documents:
        return 0

    embeddings = model.encode(documents, normalize_embeddings=True).astype(np.float32)
    index["documents"].extend(documents)
    index["metadatas"].extend(metadatas)
    index["embeddings"] = (
        embeddings
        if index["embeddings"].size == 0
        else np.vstack([index["embeddings"], embeddings])
    )
    save_index(index)
    return len(documents)


def retrieve_context(question: str, top_k: int) -> list[dict]:
    model = load_embedding_model()
    index = load_index()
    if index["embeddings"].size == 0:
        return []

    query_embedding = model.encode([question], normalize_embeddings=True).astype(np.float32)[0]
    scores = index["embeddings"] @ query_embedding
    top_indices = np.argsort(scores)[::-1][:top_k]

    return [
        {
            "text": index["documents"][i],
            "metadata": index["metadatas"][i],
            "score": float(scores[i]),
        }
        for i in top_indices
    ]


def detect_red_flags(question: str) -> list[str]:
    normalized = question.lower()
    return [term for term in RED_FLAG_TERMS if term in normalized]


def source_summary(contexts: list[dict]) -> str:
    seen = []
    for item in contexts:
        metadata = item["metadata"]
        label = f"{metadata['source']}, page {metadata['page']}"
        if label not in seen:
            seen.append(label)
    return "; ".join(seen)


def render_source_chips(contexts: list[dict]) -> None:
    chips = []
    seen = set()
    for item in contexts:
        metadata = item["metadata"]
        label = f"{metadata['source']} - page {metadata['page']}"
        if label in seen:
            continue
        seen.add(label)
        chips.append(f"<span class='source-chip'>{label}</span>")

    if chips:
        st.markdown("".join(chips), unsafe_allow_html=True)


def build_prompt(question: str, contexts: list[dict], answer_mode: str) -> str:
    context_text = "\n\n".join(
        f"Source: {item['metadata']['source']}, page {item['metadata']['page']}\n{item['text']}"
        for item in contexts
    )
    mode_instruction = ANSWER_MODES[answer_mode]
    return f"""You are a careful medical information assistant.
Answer only from the provided context. If the context does not contain the answer, say you do not know.
Do not diagnose the user. Do not replace a clinician. For urgent symptoms, recommend emergency care.
{mode_instruction}

Use this structure:
1. Direct answer
2. Key details from the document
3. When to seek medical care
4. Sources used

Context:
{context_text}

Question:
{question}

Keep the answer grounded in the source pages. Do not invent facts that are not in the context.
"""


def ask_ollama(prompt: str, model_name: str) -> str:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model_name, "prompt": prompt, "stream": False},
        timeout=120,
    )
    response.raise_for_status()
    return response.json().get("response", "").strip()


def format_ollama_error(error: Exception) -> str:
    if isinstance(error, requests.HTTPError) and error.response is not None:
        try:
            payload = error.response.json()
            if payload.get("error"):
                return payload["error"]
        except json.JSONDecodeError:
            text = error.response.text.strip()
            if text:
                return text
    return str(error)


def fallback_answer(contexts: list[dict], error: Exception | None = None) -> str:
    if not contexts:
        return "I could not find relevant context in the indexed documents."

    snippets = []
    for item in contexts[:3]:
        source = item["metadata"]["source"]
        page = item["metadata"]["page"]
        text = textwrap.shorten(item["text"], width=650, placeholder="...")
        snippets.append(f"From {source}, page {page}: {text}")

    reason = ""
    if error is not None:
        reason = f"Ollama generation failed: {format_ollama_error(error)}\n\n"

    return reason + "Here are the most relevant retrieved passages:\n\n" + "\n\n".join(snippets)


def clear_index() -> None:
    if INDEX_PATH.exists():
        INDEX_PATH.unlink()


def save_upload(uploaded_file) -> tuple[Path, str]:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_bytes = uploaded_file.getvalue()
    digest = file_hash(file_bytes)
    clean_name = Path(uploaded_file.name).name
    pdf_path = UPLOAD_DIR / f"{digest}-{clean_name}"
    if not pdf_path.exists():
        pdf_path.write_bytes(file_bytes)
    return pdf_path, digest


def render_index_status() -> None:
    index = load_index()
    chunk_count = len(index["documents"])
    sources = sorted({metadata["source"] for metadata in index["metadatas"]})

    metric_cols = st.sidebar.columns(2)
    metric_cols[0].metric("Chunks", chunk_count)
    metric_cols[1].metric("Docs", len(sources))
    st.sidebar.caption("Embedding model: MiniLM-L6-v2")

    if sources:
        with st.sidebar.expander("Indexed documents"):
            for source in sources:
                st.write(source)


def render_sidebar_guide() -> None:
    st.sidebar.subheader("How To Use")
    st.sidebar.markdown(
        """
        1. Upload a trusted medical PDF.
        2. Wait for the local index to update.
        3. Ask a focused medical question.
        4. Review the cited source pages.
        """
    )


def sidebar() -> tuple[str, int, str]:
    st.sidebar.header("Settings")
    model_name = st.sidebar.text_input("Ollama model", value=DEFAULT_OLLAMA_MODEL)
    answer_mode = st.sidebar.selectbox("Answer style", list(ANSWER_MODES.keys()))
    top_k = st.sidebar.slider("Retrieved chunks", min_value=1, max_value=8, value=4)

    st.sidebar.divider()
    render_sidebar_guide()

    st.sidebar.divider()
    st.sidebar.subheader("Index Status")
    render_index_status()
    if st.sidebar.button("Clear local index", use_container_width=True):
        clear_index()
        st.sidebar.success("Index cleared.")

    st.sidebar.divider()
    st.sidebar.caption("Run Ollama locally for generated answers. Without it, the app shows retrieved passages.")
    return model_name, top_k, answer_mode


def render_header() -> None:
    st.markdown(
        f"""
        <div class="app-header">
            <div>
                <h1>MediVault AI</h1>
                <p>Clinical document intelligence for grounded medical answers, source review, and study support.</p>
            </div>
            {hero_image_html()}
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero_image_html() -> str:
    if not HERO_IMAGE.exists():
        return ""
    return (
        '<div class="hero-image">'
        f'<img src="{svg_data_uri(HERO_IMAGE)}" alt="MediVault AI medical document assistant illustration">'
        "</div>"
    )


def render_medical_notice() -> None:
    st.markdown(
        """
        <div class="medical-alert">
            This assistant is for reference and study. It does not diagnose, prescribe, or replace a qualified clinician.
            For severe or sudden symptoms, seek urgent medical care.
        </div>
        """,
        unsafe_allow_html=True,
    )


def quick_question_buttons() -> str | None:
    st.markdown("<div class='section-label'>Common medical queries</div>", unsafe_allow_html=True)
    cols = st.columns(3)
    prompts = [
        "Summarize the key symptoms mentioned in this document.",
        "What treatments or precautions are described?",
        "When should urgent medical care be considered?",
    ]
    for col, prompt in zip(cols, prompts):
        if col.button(prompt, use_container_width=True):
            return prompt
    return None


def main() -> None:
    inject_styles()
    model_name, top_k, answer_mode = sidebar()

    render_header()
    render_medical_notice()

    st.markdown("<div class='section-label'>Knowledge source</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Medical PDF", type=["pdf"], label_visibility="collapsed")
    if uploaded_file:
        pdf_path, document_id = save_upload(uploaded_file)
        with st.spinner("Indexing document..."):
            added_count = index_pdf(pdf_path, document_id)
        if added_count:
            st.success(f"Indexed {added_count} chunks from {uploaded_file.name}.")
        else:
            st.info("This document is already indexed, or no text could be extracted.")

    st.divider()

    st.markdown("<div class='section-label'>Question workspace</div>", unsafe_allow_html=True)
    quick_question = quick_question_buttons()

    question = st.chat_input("Ask about symptoms, treatment, precautions, diagnosis, or follow-up care")
    question = quick_question or question
    if question:
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            red_flags = detect_red_flags(question)
            if red_flags:
                st.error(
                    "Your question includes urgent-sounding terms: "
                    + ", ".join(red_flags)
                    + ". If this describes a real person, seek urgent medical care."
                )

            contexts = retrieve_context(question, top_k=top_k)
            if not contexts:
                st.warning("No indexed document chunks found. Upload and index a PDF first.")
                return

            st.caption(f"Using sources: {source_summary(contexts)}")
            render_source_chips(contexts)
            prompt = build_prompt(question, contexts, answer_mode)
            try:
                with st.spinner("Generating grounded answer..."):
                    answer = ask_ollama(prompt, model_name)
            except requests.RequestException as error:
                answer = fallback_answer(contexts, error)

            st.write(answer)

            with st.expander("Retrieved sources"):
                for item in contexts:
                    metadata = item["metadata"]
                    st.markdown(
                        f"**{metadata['source']} - page {metadata['page']}** "
                        f"(similarity: {item['score']:.2f})"
                    )
                    st.write(item["text"])


if __name__ == "__main__":
    main()
