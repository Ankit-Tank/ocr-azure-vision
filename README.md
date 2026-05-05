# 🔍 OCR Azure Vision

Extract text from any image using **Azure Computer Vision** — available as both a Jupyter Notebook and a live **Streamlit** web app.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-red?logo=streamlit)
![Azure](https://img.shields.io/badge/Azure-Computer%20Vision-0078D4?logo=microsoftazure)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- 📄 Extract text line-by-line from images (PNG, JPG, JPEG, BMP, TIFF)
- 🔤 Word-level output with **confidence scores**
- ⚠️ Flags low-confidence words (< 70%)
- 💾 Export results as `.txt` or `.json`
- 🌐 Run as a **web app** in the browser via Streamlit
- 📓 Also available as a **Jupyter Notebook** (works in Colab & VS Code)

---

## 📁 Project Structure

```
ocr-azure-vision/
├──.env.example
├──.gitignore
├──LICENSE
├── ocr_app.py          # Streamlit web app
├── OCR_Secure.ipynb  # Jupyter Notebook version
├── requirements.txt    # Python dependencies
└── README.md
```

---

## ⚙️ Prerequisites

- Python 3.8+
- An **Azure account** with a **Computer Vision** resource
  - Get your `Endpoint` and `API Key` from the Azure Portal

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/Ankit-Tank/ocr-azure-vision.git
cd ocr-azure-vision
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your Azure credentials

Open `ocr_app.py` and update:
```python
ENDPOINT = "https://your-resource.cognitiveservices.azure.com/"
API_KEY  = "your-api-key-here"
```

---

## 🖥️ Run Locally (Streamlit)

```bash
streamlit run ocr_app.py
```

Opens at `http://localhost:8501` — upload an image and click **Run OCR**.

---

## 📓 Run as Jupyter Notebook

**VS Code:**
1. Place your image in the same folder as `OCR_Secure.ipynb`
2. Update `IMAGE_PATH` in Cell 3 to your image path
3. Run all cells

**Google Colab:**
1. Upload `OCR_Secure.ipynb` to Colab
2. Run Cell 3 — it will prompt you to upload your image
3. Run remaining cells

---

## 🌐 Deploy on Streamlit Cloud (Free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New App** → select your repo → set file to `ocr_app.py`
4. Click **Deploy**

> 🔐 **Tip:** Store your API key in Streamlit Secrets (Settings → Secrets) instead of hardcoding it.
```toml
# .streamlit/secrets.toml
AZURE_ENDPOINT = "https://your-resource.cognitiveservices.azure.com/"
AZURE_API_KEY  = "your-api-key"
```

---

## Deployment link

[![Live App](https://img.shields.io/badge/Live-App-brightgreen)](https://ankit-ocr-azure-vision.streamlit.app/)

---

## 📸 Sample Output

```
📄 OCR Result:
──────────────────────────────────────
In Database Management System, a
relation refers to a table consisting of
rows & columns. Relations follow certain
rules to maintain consistency & structure.

📊 Summary:
  Total lines :  8
  Total words :  47
  Avg confidence: 96.3%
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Azure Computer Vision | OCR engine |
| Streamlit | Web app framework |
| Python | Core language |
| Jupyter Notebook | Interactive exploration |

---

## 📄 License

MIT License — free to use and modify.

---

## 🙋 Author

Made by **Ankit Tank** — feel free to ⭐ the repo if you found it useful!
