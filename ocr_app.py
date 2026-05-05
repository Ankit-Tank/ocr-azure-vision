import streamlit as st
import time
import json
import os
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="AI OCR Scanner",
    page_icon="🔍",
    layout="wide"
)

# ─────────────────────────────────────────
# CUSTOM UI STYLING
# ─────────────────────────────────────────
st.markdown("""
<style>

/* Main background */
.stApp {
    background: linear-gradient(135deg, #0f172a, #111827);
    color: white;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Main title */
.main-title {
    font-size: 3.5rem;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(to right, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-top: 10px;
    margin-bottom: 10px;
}

/* Subtitle */
.sub-text {
    text-align: center;
    color: #cbd5e1;
    font-size: 1.2rem;
    margin-bottom: 2rem;
}

/* Glassmorphism Card */
.glass {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    padding: 25px;
    border-radius: 20px;
    backdrop-filter: blur(14px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    margin-bottom: 25px;
}

/* Buttons */
.stButton>button {
    width: 100%;
    border-radius: 12px;
    height: 3rem;
    border: none;
    font-size: 1rem;
    font-weight: 700;
    background: linear-gradient(to right, #3b82f6, #8b5cf6);
    color: white;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: scale(1.03);
    box-shadow: 0 0 20px rgba(99,102,241,0.5);
}

/* Upload box */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.06);
    border-radius: 20px;
    padding: 20px;
    border: 2px dashed #6366f1;
}

/* Text area */
.stTextArea textarea {
    background-color: #111827 !important;
    color: white !important;
    border-radius: 15px !important;
    border: 1px solid #374151 !important;
}

/* Metrics */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.1);
    padding: 20px;
    border-radius: 18px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0f172a;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 15px;
    overflow: hidden;
}

/* Success box */
.stSuccess {
    border-radius: 15px;
}

/* Info box */
.stInfo {
    border-radius: 15px;
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
st.markdown(
    """
    <div class="main-title">🔍 AI OCR Scanner</div>
    <div class="sub-text">
        Upload images and extract text instantly using Azure AI Vision
    </div>
    """,
    unsafe_allow_html=True
)

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ OCR Settings")

    show_words = st.checkbox("Show word-level detail", value=False)
    show_bbox = st.checkbox("Show bounding boxes", value=False)

    st.markdown("---")

    st.markdown("""
    ### 🚀 Features
    ✅ Fast OCR  
    ✅ AI Text Extraction  
    ✅ JSON Download  
    ✅ TXT Download  
    ✅ Confidence Analysis  
    """)

# ─────────────────────────────────────────
# SECURE CREDENTIALS
# ─────────────────────────────────────────
endpoint = st.secrets["AZURE_ENDPOINT"]
api_key = st.secrets["AZURE_API_KEY"]

# ─────────────────────────────────────────
# OCR FUNCTION
# ─────────────────────────────────────────
def run_ocr(image_bytes, endpoint, api_key):
    client = ComputerVisionClient(
        endpoint,
        CognitiveServicesCredentials(api_key)
    )

    import io

    response = client.read_in_stream(
        io.BytesIO(image_bytes),
        raw=True
    )

    operation_id = response.headers["Operation-Location"].split("/")[-1]

    for _ in range(30):
        result = client.get_read_result(operation_id)

        if result.status not in [
            OperationStatusCodes.running,
            OperationStatusCodes.not_started
        ]:
            break

        time.sleep(1)

    if result.status != OperationStatusCodes.succeeded:
        raise RuntimeError(f"OCR failed: {result.status}")

    return result

# ─────────────────────────────────────────
# FILE UPLOAD
# ─────────────────────────────────────────
st.markdown('<div class="glass">', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "📤 Upload Image",
    type=["png", "jpg", "jpeg", "bmp", "tiff", "gif"]
)

st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────
# OCR PROCESS
# ─────────────────────────────────────────
if uploaded_file:

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.image(
            uploaded_file,
            caption="📷 Uploaded Image",
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass">', unsafe_allow_html=True)

        st.markdown(f"### 📄 File Details")
        st.markdown(f"**Filename:** `{uploaded_file.name}`")
        st.markdown(f"**Size:** `{uploaded_file.size / 1024:.2f} KB`")
        st.markdown(f"**Type:** `{uploaded_file.type}`")

        st.markdown("<br>", unsafe_allow_html=True)

        run_btn = st.button(
            "🚀 Run OCR",
            type="primary",
            use_container_width=True
        )

        st.markdown('</div>', unsafe_allow_html=True)

    if run_btn:

        with st.spinner("🔍 AI is extracting text..."):

            try:
                image_bytes = uploaded_file.read()

                result = run_ocr(
                    image_bytes,
                    endpoint,
                    api_key
                )

                # ─────────────────────────────────────────
                # PROCESS OCR RESULTS
                # ─────────────────────────────────────────
                all_lines = []
                all_words = []
                json_data = []

                for page in result.analyze_result.read_results:
                    for line in page.lines:

                        all_lines.append(line.text)

                        for word in line.words:
                            all_words.append(word)

                        json_data.append({
                            "line": line.text,
                            "words": [
                                {
                                    "word": w.text,
                                    "confidence": round(w.confidence, 4),
                                    "bounding_box": w.bounding_box
                                }
                                for w in line.words
                            ]
                        })

                avg_conf = (
                    sum(w.confidence for w in all_words) / len(all_words)
                    if all_words else 0
                )

                low_conf = [
                    w for w in all_words
                    if w.confidence < 0.7
                ]

                st.balloons()

                st.success("✅ OCR Completed Successfully!")

                # ─────────────────────────────────────────
                # METRICS
                # ─────────────────────────────────────────
                st.markdown("## 📊 OCR Analytics")

                m1, m2, m3 = st.columns(3)

                m1.metric("Lines Extracted", len(all_lines))
                m2.metric("Words Detected", len(all_words))
                m3.metric("Avg Confidence", f"{avg_conf:.1%}")

                # ─────────────────────────────────────────
                # LOW CONFIDENCE WARNING
                # ─────────────────────────────────────────
                if low_conf:
                    st.warning(
                        f"⚠️ {len(low_conf)} low-confidence words detected."
                    )

                # ─────────────────────────────────────────
                # EXTRACTED TEXT
                # ─────────────────────────────────────────
                st.markdown("## 📄 Extracted Text")

                full_text = "\n".join(all_lines)

                st.text_area(
                    "",
                    value=full_text,
                    height=300,
                    label_visibility="collapsed"
                )

                # ─────────────────────────────────────────
                # WORD DETAILS
                # ─────────────────────────────────────────
                if show_words:

                    st.markdown("## 🔤 Word-Level Detail")

                    rows = []

                    for page in result.analyze_result.read_results:
                        for line in page.lines:
                            for w in line.words:

                                row = {
                                    "Word": w.text,
                                    "Confidence": f"{w.confidence:.2%}"
                                }

                                if show_bbox:
                                    row["Bounding Box"] = str(w.bounding_box)

                                rows.append(row)

                    st.dataframe(
                        rows,
                        use_container_width=True
                    )

                # ─────────────────────────────────────────
                # DOWNLOAD SECTION
                # ─────────────────────────────────────────
                st.markdown("## 💾 Download Results")

                d1, d2 = st.columns(2)

                with d1:
                    st.download_button(
                        "⬇️ Download TXT",
                        data=full_text,
                        file_name=f"{os.path.splitext(uploaded_file.name)[0]}_ocr.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

                with d2:
                    st.download_button(
                        "⬇️ Download JSON",
                        data=json.dumps(json_data, indent=2),
                        file_name=f"{os.path.splitext(uploaded_file.name)[0]}_ocr.json",
                        mime="application/json",
                        use_container_width=True
                    )

            except Exception as e:
                st.error(f"❌ Error: {e}")

else:
    st.info("👆 Upload an image to start OCR processing.")
