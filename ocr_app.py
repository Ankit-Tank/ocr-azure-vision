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
    page_title="OCR — Azure Computer Vision",
    page_icon="🔍",
    layout="centered"
)

st.title("🔍 OCR — Azure Computer Vision")
st.markdown("Upload an image and extract all text from it instantly.")

# ─────────────────────────────────────────
# SIDEBAR — Azure Credentials
# ─────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Azure Configuration")
    endpoint = st.text_input(
        "Endpoint URL",
        value="https://cv97898657.cognitiveservices.azure.com/",
        type="default"
    )
    api_key = st.text_input(
        "API Key",
        value="3rjI2tJgEjvUS9ve9DnwGTdgu0JW5B5i0u2mE8QpRzgaCPh4l1AwJQQJ99CEACYeBjFXJ3w3AAAFACOG0FxE",
        type="password"
    )
    st.markdown("---")
    show_words = st.checkbox("Show word-level detail", value=False)
    show_bbox  = st.checkbox("Show bounding boxes", value=False)

# ─────────────────────────────────────────
# OCR FUNCTION
# ─────────────────────────────────────────
def run_ocr(image_bytes, endpoint, api_key):
    client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(api_key))

    import io
    response = client.read_in_stream(io.BytesIO(image_bytes), raw=True)
    operation_id = response.headers["Operation-Location"].split("/")[-1]

    for _ in range(30):  # timeout after 30s
        result = client.get_read_result(operation_id)
        if result.status not in [OperationStatusCodes.running,
                                  OperationStatusCodes.not_started]:
            break
        time.sleep(1)

    if result.status != OperationStatusCodes.succeeded:
        raise RuntimeError(f"OCR failed: {result.status}")

    return result

# ─────────────────────────────────────────
# MAIN UI — Upload Image
# ─────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Upload Image",
    type=["png", "jpg", "jpeg", "bmp", "tiff", "gif"]
)

if uploaded_file:
    col1, col2 = st.columns(2)
    with col1:
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
    with col2:
        st.markdown(f"**File:** `{uploaded_file.name}`")
        st.markdown(f"**Size:** `{uploaded_file.size / 1024:.1f} KB`")
        run_btn = st.button("▶️ Run OCR", type="primary", use_container_width=True)

    if run_btn:
        if not endpoint or not api_key:
            st.error("Please fill in your Azure Endpoint and API Key in the sidebar.")
        else:
            with st.spinner("Running OCR..."):
                try:
                    image_bytes = uploaded_file.read()
                    result = run_ocr(image_bytes, endpoint, api_key)

                    # ── Collect results ──
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

                    st.success("✅ OCR Complete!")

                    # ── Stats ──
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Lines", len(all_lines))
                    m2.metric("Words", len(all_words))
                    m3.metric("Avg Confidence", f"{avg_conf:.1%}")

                    if low_conf:
                        st.warning(f"⚠️ {len(low_conf)} low-confidence word(s) detected (< 70%): "
                                   + ", ".join(f"'{w.text}'" for w in low_conf))

                    # ── Extracted Text ──
                    st.markdown("### 📄 Extracted Text")
                    full_text = "\n".join(all_lines)
                    st.text_area("", value=full_text, height=250, label_visibility="collapsed")

                    # ── Word-level detail ──
                    if show_words:
                        st.markdown("### 🔤 Word-Level Detail")
                        rows = []
                        for page in result.analyze_result.read_results:
                            for line in page.lines:
                                for w in line.words:
                                    row = {"Word": w.text, "Confidence": f"{w.confidence:.2%}"}
                                    if show_bbox:
                                        row["Bounding Box"] = str(w.bounding_box)
                                    rows.append(row)
                        st.dataframe(rows, use_container_width=True)

                    # ── Download buttons ──
                    st.markdown("### 💾 Download Results")
                    d1, d2 = st.columns(2)
                    d1.download_button(
                        "⬇️ Download as TXT",
                        data=full_text,
                        file_name=f"{os.path.splitext(uploaded_file.name)[0]}_ocr.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                    d2.download_button(
                        "⬇️ Download as JSON",
                        data=json.dumps(json_data, indent=2),
                        file_name=f"{os.path.splitext(uploaded_file.name)[0]}_ocr.json",
                        mime="application/json",
                        use_container_width=True
                    )

                except Exception as e:
                    st.error(f"❌ Error: {e}")
else:
    st.info("👆 Upload an image to get started.")
