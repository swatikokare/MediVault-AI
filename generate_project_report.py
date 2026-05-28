from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


APP_DIR = Path(__file__).parent
OUTPUT_PATH = APP_DIR / "MediVault_AI_Project_Report.pdf"
SCREENSHOTS = [
    Path(r"C:\Users\swath\OneDrive\Pictures\Screenshots\Screenshot 2026-05-28 192141.png"),
    Path(r"C:\Users\swath\OneDrive\Pictures\Screenshots\Screenshot 2026-05-28 190718.png"),
    Path(r"C:\Users\swath\OneDrive\Pictures\Screenshots\Screenshot 2026-05-28 190757.png"),
]


def make_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="TitleCenter",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=24,
            leading=30,
            textColor=colors.HexColor("#12323f"),
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SubtitleCenter",
            parent=styles["BodyText"],
            alignment=TA_CENTER,
            fontSize=11,
            leading=16,
            textColor=colors.HexColor("#55707b"),
            spaceAfter=18,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Section",
            parent=styles["Heading2"],
            fontSize=15,
            leading=19,
            textColor=colors.HexColor("#0f766e"),
            spaceBefore=12,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Small",
            parent=styles["BodyText"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#55707b"),
        )
    )
    return styles


def bullet_list(items: list[str], styles):
    return ListFlowable(
        [ListItem(Paragraph(item, styles["BodyText"]), leftIndent=12) for item in items],
        bulletType="bullet",
        leftIndent=18,
        bulletFontSize=7,
    )


def numbered_list(items: list[str], styles):
    return ListFlowable(
        [ListItem(Paragraph(item, styles["BodyText"]), leftIndent=14) for item in items],
        bulletType="1",
        start="1",
        leftIndent=18,
    )


def screenshot(path: Path, caption: str, styles):
    available_width = 7.0 * inch
    img = Image(str(path))
    aspect = img.imageHeight / float(img.imageWidth)
    img.drawWidth = available_width
    img.drawHeight = available_width * aspect
    if img.drawHeight > 4.65 * inch:
        img.drawHeight = 4.65 * inch
        img.drawWidth = img.drawHeight / aspect

    return KeepTogether(
        [
            img,
            Spacer(1, 6),
            Paragraph(caption, styles["Small"]),
            Spacer(1, 12),
        ]
    )


def architecture_table(styles):
    data = [
        ["Layer", "Implementation Used"],
        ["Frontend", "Streamlit web interface"],
        ["Document Input", "PDF upload and text extraction using pypdf"],
        ["Chunking", "Character-based chunks with overlap"],
        ["Embeddings", "sentence-transformers/all-MiniLM-L6-v2"],
        ["Vector Search", "Local NumPy cosine-similarity index"],
        ["LLM Generation", "Ollama local model, default llama3.2:1b"],
        ["Storage", "Local pickle vector index and uploaded PDFs"],
    ]
    table = Table(data, colWidths=[1.7 * inch, 4.9 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cfe3e8")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f4f9fb")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return table


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#cfe3e8"))
    canvas.line(doc.leftMargin, 0.55 * inch, A4[0] - doc.rightMargin, 0.55 * inch)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#55707b"))
    canvas.drawString(doc.leftMargin, 0.35 * inch, "MediVault AI Project Report")
    canvas.drawRightString(A4[0] - doc.rightMargin, 0.35 * inch, f"Page {doc.page}")
    canvas.restoreState()


def build_report() -> None:
    styles = make_styles()
    doc = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=A4,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
        title="MediVault AI Project Report",
    )

    story = []
    story.append(Paragraph("MediVault AI", styles["TitleCenter"]))
    story.append(
        Paragraph(
            "A Local Retrieval-Augmented Generation Assistant for Medical Document Question Answering",
            styles["SubtitleCenter"],
        )
    )
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Project Type:</b> AI-powered medical document assistant", styles["BodyText"]))
    story.append(Paragraph("<b>Technology Stack:</b> Python, Streamlit, Sentence Transformers, NumPy, Ollama, pypdf", styles["BodyText"]))

    story.append(Paragraph("1. Project Overview", styles["Section"]))
    story.append(
        Paragraph(
            "MediVault AI is a local Retrieval-Augmented Generation application designed to answer questions from uploaded medical PDF documents. "
            "The system extracts text from trusted documents, converts the text into searchable embeddings, retrieves relevant passages for a user question, "
            "and generates an answer grounded in the retrieved source pages.",
            styles["BodyText"],
        )
    )
    story.append(
        Paragraph(
            "The project was developed as a lightweight alternative to large cloud-based document assistants. Instead of storing medical content on an external "
            "server, the application keeps uploaded PDFs, extracted chunks, embeddings, and the vector index on the local machine. This design makes the tool "
            "suitable for demonstrations, student projects, and small-scale learning scenarios where simplicity and transparency are important.",
            styles["BodyText"],
        )
    )

    story.append(Paragraph("2. Problem Statement", styles["Section"]))
    story.append(
        Paragraph(
            "Medical references can be lengthy and difficult to search manually. Students and healthcare learners often need quick, source-backed summaries "
            "from trusted material. MediVault AI addresses this by allowing users to upload a PDF and ask focused questions while keeping the retrieved source "
            "passages visible for verification.",
            styles["BodyText"],
        )
    )
    story.append(
        Paragraph(
            "A normal chatbot may answer from its general training data, which can lead to unsupported or outdated responses. In a medical context, this is risky "
            "because users need to know where an answer came from. The main problem solved by this project is therefore not only answer generation, but grounded "
            "answer generation: the response should be based on the document that the user uploaded and should expose the retrieved evidence.",
            styles["BodyText"],
        )
    )

    story.append(Paragraph("3. Objectives", styles["Section"]))
    story.append(
        bullet_list(
            [
                "Build a simple local RAG chatbot for medical PDF question answering.",
                "Keep document indexing and embedding storage local on the user's machine.",
                "Provide answer styles such as patient-friendly, clinical summary, and study notes.",
                "Display source pages and similarity scores to support transparency.",
                "Add medical safety framing and red-flag warnings for urgent symptoms.",
                "Use a local Ollama model for generated answers.",
            ],
            styles,
        )
    )

    story.append(Paragraph("4. System Architecture", styles["Section"]))
    story.append(architecture_table(styles))
    story.append(
        Paragraph(
            "The system follows a modular architecture. The Streamlit interface handles user interaction, file upload, settings, and result display. The document "
            "processing layer reads PDF pages and prepares text chunks. The embedding layer converts chunks into numerical vectors, while the retrieval layer "
            "performs similarity search between the question vector and stored document vectors. Finally, the generation layer sends the retrieved context to "
            "Ollama so that the answer can be produced with document-specific grounding.",
            styles["BodyText"],
        )
    )

    story.append(Paragraph("5. Why Retrieval-Augmented Generation Is Used", styles["Section"]))
    story.append(
        Paragraph(
            "Retrieval-Augmented Generation, or RAG, combines information retrieval with language generation. In this project, retrieval is used to find the most "
            "relevant passages from the uploaded medical PDF before the language model writes the answer. This improves the usefulness of the chatbot because "
            "the model does not have to rely only on memory. Instead, it receives a focused context containing the document passages that are most related to "
            "the user's question.",
            styles["BodyText"],
        )
    )
    story.append(
        Paragraph(
            "RAG is especially useful for medical document question answering because medical content must be traceable. The app shows the source pages and "
            "retrieved chunks so that the user can inspect whether the answer is actually supported by the uploaded document.",
            styles["BodyText"],
        )
    )

    story.append(Paragraph("6. RAG Workflow", styles["Section"]))
    story.append(
        numbered_list(
            [
                "The user uploads a medical PDF through the Streamlit interface.",
                "The app extracts text from each PDF page using pypdf.",
                "Extracted text is split into overlapping chunks.",
                "Each chunk is embedded using all-MiniLM-L6-v2 from Sentence Transformers.",
                "Embeddings and metadata are stored in a local NumPy-based vector index.",
                "For a question, the app embeds the query and retrieves the most similar chunks.",
                "The retrieved context is inserted into a prompt and sent to the local Ollama LLM.",
                "The answer and retrieved source passages are shown to the user.",
            ],
            styles,
        )
    )
    story.append(
        Paragraph(
            "The chunking step is important because language models and embedding models work better with manageable text segments. If the entire PDF were sent "
            "at once, it would be inefficient and may exceed model limits. By storing smaller overlapping chunks, the retriever can return only the parts of the "
            "document that are relevant to a specific question.",
            styles["BodyText"],
        )
    )

    story.append(Paragraph("7. Implementation Details", styles["Section"]))
    story.append(
        bullet_list(
            [
                "<b>PDF handling:</b> The app uses pypdf to extract text from uploaded PDF pages.",
                "<b>Chunking:</b> Extracted page text is divided into chunks with overlap to preserve context across boundaries.",
                "<b>Embeddings:</b> Sentence Transformers creates a 384-dimensional vector for each chunk using all-MiniLM-L6-v2.",
                "<b>Vector index:</b> The vectors, source filename, page number, and chunk metadata are saved locally in vector_index.pkl.",
                "<b>Similarity search:</b> The app computes cosine similarity through normalized dot products using NumPy.",
                "<b>LLM prompt:</b> Retrieved chunks are inserted into a safety-aware prompt before being sent to Ollama.",
                "<b>Fallback behavior:</b> If Ollama is unavailable, the app still shows the most relevant retrieved passages.",
            ],
            styles,
        )
    )

    story.append(Paragraph("8. Prompt Design", styles["Section"]))
    story.append(
        Paragraph(
            "The prompt instructs the model to answer only from the provided context. It also tells the model not to diagnose the user or replace a clinician. "
            "The prompt asks for a structured answer with a direct answer, key details, when to seek medical care, and sources used. This structure makes the "
            "output easier to read and encourages the model to remain tied to the retrieved evidence.",
            styles["BodyText"],
        )
    )
    story.append(
        Paragraph(
            "The app also provides answer styles. Patient-friendly mode uses simpler language, clinical summary mode uses concise professional wording, and "
            "study notes mode presents information in a revision-friendly format. These styles make the same RAG system useful for different audiences.",
            styles["BodyText"],
        )
    )

    story.append(Paragraph("9. Medical Safety Considerations", styles["Section"]))
    story.append(
        Paragraph(
            "Because this project works with medical information, the interface includes visible safety framing. The app states that it is for reference and "
            "study only and does not diagnose, prescribe, or replace a qualified clinician. It also detects urgent-sounding terms such as chest pain, seizure, "
            "overdose, severe bleeding, and difficulty breathing. When such terms appear, the user receives an urgent-care warning.",
            styles["BodyText"],
        )
    )
    story.append(
        Paragraph(
            "This safety design does not make the system a medical device. Its purpose is to reduce misuse and remind users that medical decisions should be "
            "made with qualified professionals, especially in emergency situations.",
            styles["BodyText"],
        )
    )

    story.append(Paragraph("10. User Interface Design", styles["Section"]))
    story.append(
        Paragraph(
            "The user interface was designed to feel medical, calm, and easy to scan. A teal and light-blue palette was used because these colors are commonly "
            "associated with healthcare, cleanliness, and trust. The sidebar contains controls and index status, while the main area focuses on document upload, "
            "quick question buttons, chat interaction, and source review.",
            styles["BodyText"],
        )
    )
    story.append(
        Paragraph(
            "The app displays source chips above the answer so the user immediately knows which pages were used. Retrieved passages are kept inside an expandable "
            "section, allowing the user to verify evidence without overwhelming the main answer area.",
            styles["BodyText"],
        )
    )

    story.append(Paragraph("11. Key Features", styles["Section"]))
    story.append(
        bullet_list(
            [
                "Local PDF upload and indexing.",
                "Local vector search without requiring Chroma, FAISS, or Microsoft C++ Build Tools.",
                "Ollama integration with llama3.2:1b for machines with limited memory.",
                "Sidebar controls for model name, answer style, retrieval count, index status, and clearing embeddings.",
                "Medical-friendly UI with teal clinical colors, source chips, and quick question buttons.",
                "Safety notice and red-flag detection for urgent medical terms.",
            ],
            styles,
        )
    )

    story.append(PageBreak())
    story.append(Paragraph("12. User Interface Screenshots", styles["Section"]))
    if SCREENSHOTS[0].exists():
        story.append(
            screenshot(
                SCREENSHOTS[0],
                "Figure 1: MediVault AI landing screen showing the sidebar controls, safety notice, PDF upload area, and quick medical question buttons.",
                styles,
            )
        )
    if SCREENSHOTS[1].exists():
        story.append(
            screenshot(
                SCREENSHOTS[1],
                "Figure 2: MediVault AI answering a hypertension-related question using the uploaded sample medical reference PDF.",
                styles,
            )
        )
    if SCREENSHOTS[2].exists():
        story.append(
            screenshot(
                SCREENSHOTS[2],
                "Figure 3: Retrieved source passages with page references and similarity scores for answer verification.",
                styles,
            )
        )

    story.append(Paragraph("13. Testing With Sample Document", styles["Section"]))
    story.append(
        Paragraph(
            "A synthetic sample medical reference document was created for testing. It includes sections on migraine, appendicitis, type 2 diabetes, asthma, "
            "hypertension, and medication safety. The sample document is educational and not intended as actual clinical guidance.",
            styles["BodyText"],
        )
    )
    story.append(
        bullet_list(
            [
                "Sample file: sample_medical_reference.pdf",
                "Example question: What are the symptoms of hypertension?",
                "Expected behavior: Retrieve the hypertension section and answer with source-backed details.",
                "Observed behavior: The app displayed cited source pages and retrieved passages for review.",
            ],
            styles,
        )
    )
    story.append(
        Paragraph(
            "During testing, the application successfully indexed the sample PDF and displayed eight chunks for one uploaded document. A query about hypertension "
            "retrieved source passages from the hypertension section and showed page references with similarity scores. This confirmed that the retrieval layer "
            "was functioning and that the UI provided enough evidence for manual verification.",
            styles["BodyText"],
        )
    )

    story.append(Paragraph("14. Local Setup And Execution", styles["Section"]))
    story.append(
        numbered_list(
            [
                "Create and activate a Python virtual environment.",
                "Install dependencies from requirements.txt.",
                "Install Ollama and pull the smaller local model llama3.2:1b.",
                "Run the app using streamlit run app.py.",
                "Upload a medical PDF and wait for indexing to complete.",
                "Ask a question and review the answer with retrieved sources.",
            ],
            styles,
        )
    )
    story.append(
        Paragraph(
            "The smaller llama3.2:1b model was selected because it is more practical on laptops with limited available memory. Larger models can improve answer "
            "quality but require more RAM or GPU resources.",
            styles["BodyText"],
        )
    )

    story.append(Paragraph("15. Limitations", styles["Section"]))
    story.append(
        bullet_list(
            [
                "The app is an educational assistant and must not be used for diagnosis or treatment decisions.",
                "Answer quality depends on the uploaded document quality and PDF text extraction quality.",
                "Small local models may produce less fluent or less complete answers than larger models.",
                "The current vector index clears all embeddings at once rather than deleting one document at a time.",
                "Scanned image-only PDFs require OCR, which is not included in the current version.",
            ],
            styles,
        )
    )

    story.append(Paragraph("16. Future Scope", styles["Section"]))
    story.append(
        bullet_list(
            [
                "Add OCR support for scanned PDFs.",
                "Add per-document delete and document selection.",
                "Improve answer evaluation using groundedness and relevance scoring.",
                "Add citations inline beside each answer sentence.",
                "Add user authentication for multi-user deployments.",
                "Add better medical entity extraction for symptoms, medicines, and conditions.",
            ],
            styles,
        )
    )

    story.append(Paragraph("17. Conclusion", styles["Section"]))
    story.append(
        Paragraph(
            "MediVault AI demonstrates a practical local RAG workflow for medical document question answering. It combines document ingestion, embedding-based "
            "retrieval, local LLM generation, source transparency, and medical safety framing in a user-friendly Streamlit application. The project is suitable "
            "as a foundation for academic exploration of retrieval-augmented generation in healthcare information systems.",
            styles["BodyText"],
        )
    )

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT_PATH)


if __name__ == "__main__":
    build_report()
