import streamlit as st
import time, json, os
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials

st.set_page_config(page_title="AI OCR Scanner", page_icon="🔍", layout="wide")

st.markdown("""
<style>
.stApp{
background:linear-gradient(135deg,#667eea,#764ba2);
}
header,footer,#MainMenu,[data-testid="stToolbar"],[data-testid="stHeader"]{
display:none !important;
}
.block-container{
padding-top:1rem !important;
max-width:1400px;
}
.main-title{
text-align:center;
font-size:60px;
font-weight:800;
color:white;
margin-bottom:0;
}
.sub{
text-align:center;
color:white;
margin-bottom:30px;
font-size:20px;
}
[data-testid="stFileUploader"]{
background:rgba(255,255,255,0.15);
padding:25px;
border-radius:20px;
border:2px dashed white;
}
.glass{
background:rgba(255,255,255,0.15);
padding:20px;
border-radius:20px;
backdrop-filter:blur(10px);
margin-bottom:20px;
}
.stTextArea textarea{
background:white !important;
color:black !important;
border-radius:15px !important;
font-size:16px !important;
}
.stButton>button,.stDownloadButton>button{
width:100%;
border:none;
border-radius:12px;
padding:12px;
font-weight:700;
background:linear-gradient(90deg,#ff758c,#ff7eb3);
color:white;
}
[data-testid="metric-container"]{
background:rgba(255,255,255,0.2);
border-radius:15px;
padding:15px;
}
.custom-footer{
text-align:center;
color:white;
margin-top:40px;
}
</style>
""", unsafe_allow_html=True)

endpoint = st.secrets["AZURE_ENDPOINT"]
api_key = st.secrets["AZURE_API_KEY"]

with st.sidebar:
    st.title("⚙️ Settings")
    show_words = st.checkbox("Show word-level detail")
    show_bbox = st.checkbox("Show bounding boxes")

def run_ocr(image_bytes):
    client = ComputerVisionClient(
        endpoint,
        CognitiveServicesCredentials(api_key)
    )

    import io
    response = client.read_in_stream(io.BytesIO(image_bytes), raw=True)
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

st.markdown('<div class="main-title">🔍 AI OCR Scanner</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">Extract text instantly using Azure AI Vision</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload Image",
    type=["png","jpg","jpeg","bmp","tiff","gif"],
    label_visibility="collapsed"
)

if uploaded_file:

    c1, c2 = st.columns([1.1,1])

    with c1:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.subheader("📸 Uploaded Image")
        st.image(uploaded_file, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.subheader("📋 File Details")
        st.write(f"**Name:** {uploaded_file.name}")
        st.write(f"**Size:** {uploaded_file.size/1024:.2f} KB")
        st.write(f"**Type:** {uploaded_file.type}")

        run_btn = st.button("🚀 Extract Text")
        st.markdown('</div>', unsafe_allow_html=True)

    if run_btn:

        with st.spinner("Processing OCR..."):

            try:
                result = run_ocr(uploaded_file.read())

                all_lines = []
                all_words = []
                json_data = []

                for page in result.analyze_result.read_results:
                    for line in page.lines:

                        all_lines.append(line.text)

                        for w in line.words:
                            all_words.append(w)

                        json_data.append({
                            "line": line.text,
                            "words": [
                                {
                                    "word": x.text,
                                    "confidence": round(x.confidence,4),
                                    "bounding_box": x.bounding_box
                                }
                                for x in line.words
                            ]
                        })

                full_text = "\n".join(all_lines)

                avg_conf = (
                    sum(w.confidence for w in all_words)/len(all_words)
                    if all_words else 0
                )

                st.success("✅ OCR Completed Successfully")

                m1,m2,m3 = st.columns(3)

                m1.metric("Lines", len(all_lines))
                m2.metric("Words", len(all_words))
                m3.metric("Confidence", f"{avg_conf:.1%}")

                st.subheader("📄 Extracted Text")

                st.text_area(
                    "",
                    value=full_text,
                    height=250,
                    label_visibility="collapsed"
                )

                if show_words:

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

                    st.dataframe(rows, use_container_width=True)

                st.subheader("💾 Download Results")

                d1,d2 = st.columns(2)

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
                st.error(f"Error: {e}")

else:

    st.markdown("""
    <div class="glass" style="text-align:center;">
    <h2 style="color:white;">👆 Upload an image to begin OCR</h2>
    </div>
    """, unsafe_allow_html=True)

st.markdown(
"""
<div class="custom-footer">
Made with ❤️ by Ankit-Tank
</div>
""",
unsafe_allow_html=True
)
