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
    page_title="OCR Vision",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────
# CUSTOM CSS FOR MODERN UI
# ─────────────────────────────────────────
st.markdown("""
<style>
    /* Main background gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Custom card styling */
    .upload-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
    }
    
    /* Title styling */
    .custom-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .custom-subtitle {
        text-align: center;
        color: #ffffff;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Download buttons */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 10px;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        border: 2px dashed #667eea;
    }
    
    /* Success/Warning messages */
    .stSuccess {
        background-color: rgba(40, 167, 69, 0.1);
        border-left: 4px solid #28a745;
        border-radius: 8px;
    }
    
    .stWarning {
        background-color: rgba(255, 193, 7, 0.1);
        border-left: 4px solid #ffc107;
        border-radius: 8px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] .css-1d391kg {
        color: white;
    }
    
    /* Text area */
    .stTextArea textarea {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        font-family: 'Courier New', monospace;
    }
    
    /* Dataframe */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# 🔐 LOAD CREDENTIALS SECURELY
# ─────────────────────────────────────────
try:
    endpoint = st.secrets["AZURE_ENDPOINT"]
    api_key = st.secrets["AZURE_API_KEY"]
except Exception:
    st.error("⚠️ Azure credentials not configured. Please add them to Streamlit Secrets.")
    st.info("Go to: Settings → Secrets → Add AZURE_ENDPOINT and AZURE_API_KEY")
    st.stop()

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    show_words = st.checkbox("📝 Show word-level detail", value=False)
    show_bbox = st.checkbox("📐 Show bounding boxes", value=False)
    
    st.markdown("---")
    st.markdown("### 🔐 Security")
    st.success("✅ Credentials loaded securely from Streamlit Secrets")
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    This app uses **Azure Computer Vision** to extract text from images using OCR technology.
    
    **Features:**
    - 📸 Upload any image
    - 🔤 Extract all text
    - 📊 Confidence scores
    - 💾 Export as TXT/JSON
    """)

# ─────────────────────────────────────────
# OCR FUNCTION
# ─────────────────────────────────────────
def run_ocr(image_bytes, endpoint, api_key):
    client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(api_key))
    
    import io
    response = client.read_in_stream(io.BytesIO(image_bytes), raw=True)
    operation_id = response.headers["Operation-Location"].split("/")[-1]
    
    for _ in range(30):
        result = client.get_read_result(operation_id)
        if result.status not in [OperationStatusCodes.running,
                                  OperationStatusCodes.not_started]:
            break
        time.sleep(1)
    
    if result.status != OperationStatusCodes.succeeded:
        raise RuntimeError(f"OCR failed: {result.status}")
    
    return result

# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
st.markdown('<h1 class="custom-title">🔍 OCR Vision</h1>', unsafe_allow_html=True)
st.markdown('<p class="custom-subtitle">Extract text from images instantly using AI-powered OCR</p>', unsafe_allow_html=True)

# ─────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────
uploaded_file = st.file_uploader(
    "📤 Drop your image here or click to browse",
    type=["png", "jpg", "jpeg", "bmp", "tiff", "gif"],
    label_visibility="collapsed"
)

if uploaded_file:
    st.markdown("---")
    
    # Image preview and info
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📸 Uploaded Image")
        st.image(uploaded_file, use_container_width=True)
    
    with col2:
        st.markdown("### 📋 File Details")
        st.markdown(f"""
        <div style='background: white; padding: 1.5rem; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);'>
            <p style='margin: 0.5rem 0; font-size: 1.1rem;'><strong>📄 Name:</strong> {uploaded_file.name}</p>
            <p style='margin: 0.5rem 0; font-size: 1.1rem;'><strong>📦 Size:</strong> {uploaded_file.size / 1024:.1f} KB</p>
            <p style='margin: 0.5rem 0; font-size: 1.1rem;'><strong>🔖 Type:</strong> {uploaded_file.type}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        run_btn = st.button("🚀 Extract Text", type="primary", use_container_width=True)
    
    if run_btn:
        with st.spinner("🔄 Processing image with Azure Computer Vision..."):
            try:
                image_bytes = uploaded_file.read()
                result = run_ocr(image_bytes, endpoint, api_key)
                
                # Collect results
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
                                {"word": w.text,
                                 "confidence": round(w.confidence, 4),
                                 "bounding_box": w.bounding_box}
                                for w in line.words
                            ]
                        })
                
                avg_conf = sum(w.confidence for w in all_words) / len(all_words) if all_words else 0
                low_conf = [w for w in all_words if w.confidence < 0.7]
                
                st.markdown("---")
                st.success("✅ Text extraction completed successfully!")
                
                # Stats
                st.markdown("### 📊 Statistics")
                m1, m2, m3 = st.columns(3)
                m1.metric("📝 Lines", len(all_lines))
                m2.metric("🔤 Words", len(all_words))
                m3.metric("🎯 Avg Confidence", f"{avg_conf:.1%}")
                
                if low_conf:
                    st.warning(f"⚠️ **{len(low_conf)} low-confidence words detected (< 70%):** " 
                              + ", ".join(f"`{w.text}`" for w in low_conf[:5]) 
                              + ("..." if len(low_conf) > 5 else ""))
                
                # Extracted text
                st.markdown("### 📄 Extracted Text")
                full_text = "\n".join(all_lines)
                st.text_area("", value=full_text, height=250, label_visibility="collapsed")
                
                # Word-level detail
                if show_words:
                    st.markdown("### 🔤 Word-Level Analysis")
                    rows = []
                    for page in result.analyze_result.read_results:
                        for line in page.lines:
                            for w in line.words:
                                row = {"Word": w.text, "Confidence": f"{w.confidence:.2%}"}
                                if show_bbox:
                                    row["Bounding Box"] = str(w.bounding_box)
                                rows.append(row)
                    st.dataframe(rows, use_container_width=True, height=400)
                
                # Download buttons
                st.markdown("### 💾 Download Results")
                d1, d2 = st.columns(2)
                
                with d1:
                    st.download_button(
                        "📄 Download as TXT",
                        data=full_text,
                        file_name=f"{os.path.splitext(uploaded_file.name)[0]}_ocr.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                
                with d2:
                    st.download_button(
                        "📋 Download as JSON",
                        data=json.dumps(json_data, indent=2),
                        file_name=f"{os.path.splitext(uploaded_file.name)[0]}_ocr.json",
                        mime="application/json",
                        use_container_width=True
                    )
                
            except Exception as e:
                st.error(f"❌ **Error during OCR processing:** {str(e)}")
                st.info("💡 Make sure your Azure credentials are correct and the service is active.")

else:
    # Empty state
    st.markdown("""
    <div style='text-align: center; padding: 3rem; background: rgba(255,255,255,0.9); border-radius: 20px; margin-top: 2rem;'>
        <h2 style='color: #667eea; margin-bottom: 1rem;'>👆 Upload an image to get started</h2>
        <p style='color: #666; font-size: 1.1rem;'>Supported formats: PNG, JPG, JPEG, BMP, TIFF, GIF</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: white; padding: 1rem;'>
    <p>Powered by <strong>Azure Computer Vision</strong> | Built with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)