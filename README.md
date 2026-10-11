# 📰 AI News Briefer

> 🎓 This project was built during the [**Tips Hindawi**](https://www.tipshindawi.com/) **Internship (August–October) 2026**.

## 👤 Participant

| Field | Value |
|---|---|
| Full Name | Suehaila Taher Yehia |
| Project Name | AI_News_Briefer |
| GitHub Username | Suehaila-Yehia |
| Internship Batch | August–October 2026 |
| Training Program | Large Language Models (LLMs) Program |
| Organization | [**Edrak for Ai**](https://edrak4ai.com/en) |

---

# 📖 Project Overview

**AI News Briefer** is a multi-agent LLM application that automatically aggregates the latest news from RSS feeds, synthesizes it into a concise daily digest, and delivers it straight to your inbox as a formatted HTML email.

The system is built as a small team of specialized agents that hand work off to each other:

1. **NewsAgent** — fetches and cleans the latest articles from any RSS feed (BBC, TechCrunch, NYT, or a custom URL).
2. **SummarizerAgent** — feeds the raw articles into a locally-hosted, 4-bit quantized Qwen 2.5 LLM and generates an objective, bullet-point briefing with clickable source links.
3. **EmailAutomationAgent** — converts the Markdown digest into a styled HTML email and dispatches it via Gmail SMTP.

Everything runs inside a **Streamlit** web interface exposed to the public through an **ngrok** tunnel — meaning the full pipeline (model + UI + email) can be launched from a single Google Colab notebook with a T4 GPU, no local setup required.

---

# ✨ Features


- 📡 **Multi-source RSS aggregation** — plug in BBC World News, TechCrunch, NYT World News, or any custom RSS URL.
- 🎚️ **Adjustable summary detail** — choose **Brief** (1 sentence/story), **Standard** (1–2 sentences), or **Detailed** (2–3 analytical sentences explaining *what* happened and *why* it matters).
- 🌡️ **Hallucination control** — a temperature slider lets you dial LLM creativity vs. factual grounding.
- 🔗 **Citation-preserving output** — every bullet point ends with a `[Read Full Story](URL)` link to the original article.
- 📧 **One-click HTML email dispatch** — Gmail SMTP delivery with graceful plain-text fallback for older clients.
- 🔍 **Audit trail** — an expandable panel shows the exact raw RSS JSON fed to the LLM, so you can verify there's no hallucinated content.

---

# 🛠️ Technologies Used

| Category | Tools |
|---|---|
| **LLM** | [Qwen 2.5-3B-Instruct](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct) |
| **Model loading & quantization** | `transformers`, `accelerate`, `bitsandbytes` (4-bit NF4) |
| **Deep learning framework** | `PyTorch` (CUDA) |
| **News ingestion** | `feedparser` |
| **Frontend / UI** | `Streamlit` |
| **Public tunneling** | `pyngrok` + [ngrok](https://ngrok.com/) |
| **Email** | Python `smtplib`, `email.mime` (Gmail SMTP) |
| **Markdown → HTML** | `markdown` |
| **Runtime environment** | Google Colab (T4 GPU, 15 GB VRAM) |
| **Language** | Python 3.11 |

---

# ⚙️ Installation

### Option A — Run in Google Colab (recommended)

1. Open a new Colab notebook and set **Runtime → Change runtime type → T4 GPU**.
2. Install dependencies:

   ```bash
   !pip install -q streamlit pyngrok feedparser markdown transformers accelerate bitsandbytes
