import streamlit as st
import time
import json
import os
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials

# =========================================
# PAGE CONFIG
# =========================================
st.set_page_config(
    page_title="Neon OCR AI",
    page_icon="⚡",
    layout="wide"
)

# =========================================
# CYBERPUNK UI
# =========================================
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif;
}

/* BACKGROUND */
.stApp{
    background:
    radial-gradient(circle at top left, #00ffff22 0%, transparent 30%),
    radial-gradient(circle at bottom right, #ff00aa22 0%, transparent 30%),
    linear-gradient(135deg,#050816,#0b1020,#09090f);

    color:white;
}

/* REMOVE STREAMLIT */
header, footer, #MainMenu,
[data-testid="stToolbar"],
[data-testid="stHeader"]{
    display:none !important;
}

/* LAYOUT */
.block-container{
    max-width:1500px;
    padding-top:1rem;
}

/* TITLE */
.main-title{
    text-align:center;
    font-size:78px;
    font-family:'Orbitron', sans-serif;
    font-weight:900;

    background:linear-gradient(
        90deg,
        #00f7ff,
        #7b61ff,
        #ff00aa
    );

    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;

    text-shadow:
    0 0 20px #00f7ff55,
    0 0 40px #7b61ff55;

    margin-bottom:10px;
}

.sub{
    text-align:center;
    color:#cbd5e1;
    font-size:22px;
    margin-bottom:40px;
    letter-spacing:1px;
}

/* PANELS */
.cyber-panel{

    background:
    linear-gradient(
        145deg,
        rgba(255,255,255,0.05),
        rgba(255,255,255,0.02)
    );

    border:1px solid rgba(0,247,255,0.2);

    border-radius:28px;

    padding:25px;

    backdrop-filter:blur(18px);

    box-shadow:
    0 0 20px rgba(0,247,255,0.08),
    inset 0 0 20px rgba(255,255,255,0.03);

    margin-bottom:20px;
}

/* FILE UPLOADER */
[data-testid="stFileUploader"]{
    background:
    linear-gradient(
        145deg,
        rgba(255,255,255,0.04),
        rgba(255,255,255,0.02)
    );

    border:2px dashed #00f7ff88;
    border-radius:28px;

    padding:35px;

    box-shadow:
    0 0 20px #00f7ff22,
    inset 0 0 30px #ffffff05;
}

/* BUTTONS */
.stButton>button,
.stDownloadButton>button{

    width:100%;

    border:none;

    border-radius:16px;

    padding:14px;

    font-size:17px;

    font-weight:700;

    color:white;

    background:
    linear-gradient(
        90deg,
        #00c6ff,
        #7b61ff,
        #ff00aa
    );

    box-shadow:
    0 0 20px #7b61ff44;

    transition:0.3s;
}

.stButton>button:hover,
.stDownloadButton>button:hover{

    transform:translateY(-3px);

    box-shadow:
    0 0 25px #00f7ff88,
    0 0 50px #ff00aa55;
}

/* TEXT AREA */
.stTextArea textarea{

    background:#050816 !important;

    color:#00f7ff !important;

    border:1px solid #00f7ff55 !important;

    border-radius:24px !important;

    font-size:17px !important;

    font-family:Consolas !important;

}

/* METRICS */
[data-testid="metric-container"]{

    background:
    linear-gradient(
        145deg,
        rgba(255,255,255,0.06),
        rgba(255,255,255,0.03)
    );

    border:1px solid #ffffff12;

    border-radius:24px;

    padding:22px;

    box-shadow:
    0 0 20px #00f7ff11;
}

/* SIDEBAR */
[data-testid="stSidebar"]{

    background:
    linear-gradient(
        180deg,
        #060816,
        #0f172a
    );

    border-right:1px solid #00f7ff22;
}

/* FOOTER */
.custom-footer{

    text-align:center;

    margin-top:50px;

    color:#94a3b8;

    font-size:16px;

    letter-spacing:1px;
}

/* SCANLINE */
.scanline{

    position:fixed;

    top:0;
    left:0;

    width:100%;
    height:100%;

    pointer-events:none;

    background:
    repeating-linear-gradient(
        to bottom,
        transparent,
        transparent 2px,
        rgba(255,255,255,0.02) 3px
    );

    opacity:0.15;

    z-index:9999;
}

</style>

<div class="scanline"></div>

""", unsafe_allow_html=True)

# =========================================
# SECRETS
# =========================================
endpoint = st.secrets["AZURE_ENDPOINT"]
api_key = st.secrets["AZURE_API_KEY"]

# =========================================
# SIDEBAR
# =========================================
with st.sidebar:

    st.markdown("## ⚙️ OCR CONTROLS")

    show_words = st.checkbox("Word-level detail")
    show_bbox = st.checkbox("Bounding boxes")

    st.markdown("---")

    st.markdown("""
### 🚀 SYSTEM STATUS

✅ Azure Connected  
✅ OCR Engine Active  
✅ Neural Vision Ready  
""")

# =========================================
# OCR FUNCTION
# =========================================
def run_ocr(image_bytes):

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

    return result

# =========================================
# HEADER
# =========================================
st.markdown(
"""
<div class="main-title">
⚡OCR AI
</div>

<div class="sub">
TEXT EXTRACTION SYSTEM
</div>
""",
unsafe_allow_html=True
)

# =========================================
# FILE UPLOAD
# =========================================
uploaded_file = st.file_uploader(
    "Upload Image",
    type=["png","jpg","jpeg","bmp","tiff","gif"],
    label_visibility="collapsed"
)

# =========================================
# MAIN UI
# =========================================
if uploaded_file:

    left, right = st.columns([1.2, 0.8])

    with left:

        st.markdown('<div class="cyber-panel">', unsafe_allow_html=True)

        st.subheader("📸 IMAGE PREVIEW")

        st.image(
            uploaded_file,
            use_container_width=True
        )

        st.markdown('</div>', unsafe_allow_html=True)

    with right:

        st.markdown('<div class="cyber-panel">', unsafe_allow_html=True)

        st.subheader("🧠 FILE ANALYTICS")

        st.write(f"**FILE:** {uploaded_file.name}")
        st.write(f"**SIZE:** {uploaded_file.size/1024:.2f} KB")
        st.write(f"**TYPE:** {uploaded_file.type}")

        run_btn = st.button(
            "⚡ INITIALIZE OCR"
        )

        st.markdown('</div>', unsafe_allow_html=True)

    if run_btn:

        with st.spinner("Neural OCR scanning in progress..."):

            try:

                result = run_ocr(uploaded_file.read())

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

                full_text = "\n".join(all_lines)

                avg_conf = (
                    sum(w.confidence for w in all_words)/len(all_words)
                    if all_words else 0
                )

                st.success("✅ OCR SYSTEM COMPLETE")

                # METRICS
                m1,m2,m3 = st.columns(3)

                m1.metric("LINES", len(all_lines))
                m2.metric("WORDS", len(all_words))
                m3.metric("CONFIDENCE", f"{avg_conf:.1%}")

                # TEXT OUTPUT
                st.markdown("## 🧾 OCR OUTPUT")

                st.text_area(
                    "",
                    value=full_text,
                    height=320,
                    label_visibility="collapsed"
                )

                # WORD ANALYSIS
                if show_words:

                    st.markdown("## 🔍 WORD ANALYSIS")

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

                # DOWNLOADS
                st.markdown("## 💾 EXPORT DATA")

                d1,d2 = st.columns(2)

                with d1:
                    st.download_button(
                        "⬇️ EXPORT TXT",
                        data=full_text,
                        file_name=f"{os.path.splitext(uploaded_file.name)[0]}_ocr.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

                with d2:
                    st.download_button(
                        "⬇️ EXPORT JSON",
                        data=json.dumps(json_data, indent=2),
                        file_name=f"{os.path.splitext(uploaded_file.name)[0]}_ocr.json",
                        mime="application/json",
                        use_container_width=True
                    )

            except Exception as e:

                st.error(f"OCR FAILURE: {e}")

else:

    st.markdown("""
    <div class="cyber-panel" style="text-align:center;padding:70px;">

    <h1 style="
    font-size:70px;
    margin-bottom:10px;
    ">
    ⚡
    </h1>

    <h2 style="
    color:white;
    font-size:34px;
    margin-bottom:10px;
    font-family:'Orbitron';
    ">
    DROP IMAGE TO START OCR
    </h2>

    <p style="
    color:#94a3b8;
    font-size:18px;
    ">
    PNG • JPG • JPEG • BMP • TIFF • GIF
    </p>

    </div>
    """, unsafe_allow_html=True)

# =========================================
# FOOTER
# =========================================
st.markdown(
    """
    <div class="custom-footer">
        Made with ❤️ by 
        <a href="https://github.com/Ankit-Tank" target="_blank">
        Ankit-Tank
        </a>
    </div>
    """,
    unsafe_allow_html=True
)
