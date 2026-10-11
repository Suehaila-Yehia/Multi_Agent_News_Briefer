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
Write the app to a file (%%writefile news_app.py) — see the notebook NGROK_Kaggle.ipynb / Multi_Agent_News_Breifer.ipynb for the full source.

Launch Streamlit and open the ngrok tunnel:

Python
import subprocess, threading, time, socket, os
from pyngrok import ngrok, conf

NGROK_TOKEN = "your_ngrok_authtoken_here"   # from [https://dashboard.ngrok.com](https://dashboard.ngrok.com)

def free_port():
    s = socket.socket(); s.bind(("", 0))
    port = s.getsockname()[1]; s.close(); return port

PORT = free_port()

def run():
    subprocess.run([
        "streamlit", "run", "news_app.py",
        "--server.port", str(PORT),
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false",
    ])

threading.Thread(target=run, daemon=True).start()
time.sleep(8)

conf.get_default().auth_token = NGROK_TOKEN
print("🌐 Public URL:", ngrok.connect(PORT, bind_tls=True).public_url)
Open the printed URL in a new tab.

Option B — Run locally on your own machine
If you prefer running the application locally on your desktop or laptop without Google Colab or ngrok:

Clone the repository and navigate to the project directory:

Bash
git clone [https://github.com/Suehaila-Yehia/AI_News_Briefer.git](https://github.com/Suehaila-Yehia/AI_News_Briefer.git)
cd AI_News_Briefer
Install the required dependencies:

Bash
pip install streamlit feedparser markdown transformers accelerate bitsandbytes
Run the Streamlit app:

Bash
streamlit run news_app.py
Open http://localhost:8501 in your browser.

Hardware Note: An NVIDIA GPU with ≥ 6 GB VRAM (CUDA-enabled) is strongly recommended for local inference. The app can run on CPU, but generation will be very slow.

Gmail setup (required for email dispatch)
You must use a Google App Password, not your real Gmail password:

Enable 2-Step Verification: https://myaccount.google.com/security

Generate an App Password: https://myaccount.google.com/apppasswords

Copy the 16-character code (remove the spaces).

# 🚀 Usage
Open the Streamlit app at the ngrok URL (or http://localhost:8501 if local).

In the left sidebar, configure the run:

Summary Detail Level — Brief / Standard / Detailed.

Preset Source — pick BBC, TechCrunch, or NYT, or paste a Custom RSS URL (overrides the preset).

Article Count — 1 to 10 stories.

Temperature — 0.0 (strictly factual) to 1.0 (creative). Default 0.1.

(Optional) Enter Recipient Email, Sender Gmail, and the 16-character App Password to enable automatic email delivery.

Click 🚀 Generate News Digest.

The generated briefing appears in the main panel. Expand 🔍 Audit Raw RSS Feed Data to verify the underlying source articles.

If email credentials were provided, the formatted HTML digest is delivered to the recipient inbox.

First run takes ~1–3 minutes while the ~6 GB model downloads and loads into VRAM. Subsequent generations are fast.


# 📸 Demo
Streamlit interface
┌────────────────────────┬──────────────────────────────────────┐
│  ⚙️ News & Model       │  Automation Status:                  │
│     Settings           │  ✅ Formatted digest successfully    │
│                        │     emailed to user@example.com!     │
│  Summary Detail Level: │                                      │
│  ○ Brief               │  **Latest Headlines**                │
│  ○ Standard            │                                      │
│  ● Detailed            │  - The UN Security Council held an   │
│                        │    emergency session on …            │
│  Preset Source:        │    ([Read Full Story](https://…))    │
│  BBC World News ▾      │                                      │
│                        │  - TechCrunch reports that …         │
│  Article Count: ──●── 5│    ([Read Full Story](https://…))    │
│                        │                                      │
│  Temperature:   ●─── 0.1│  ▼ 🔍 Audit Raw RSS Feed Data         │
│                        │                                      │
│  📧 Email Credentials  │                                      │
│  Recipient: …          │                                      │
│  Sender:    …          │                                      │
│  App Pass:  ********   │                                      │
│                        │                                      │
│  [🚀 Generate Digest]  │                                      │
└────────────────────────┴──────────────────────────────────────┘

<img width="1407" height="713" alt="Screenshot 2026-10-11 220226" src="https://github.com/user-attachments/assets/8135c133-9763-4e0e-91be-d0a9f70459eb" />

<img width="1488" height="722" alt="Screenshot 2026-10-11 222111" src="https://github.com/user-attachments/assets/6f794b45-ad2b-4356-9dbc-684a48506aa9" />

<img width="1097" height="661" alt="Screenshot 2026-10-11 221255" src="https://github.com/user-attachments/assets/c80d186b-2cdf-4b92-8a4b-83065d0f585f" />

<img width="1097" height="661" alt="Screenshot 2026-10-11 221255" src="https://github.com/user-attachments/assets/f34bbcb2-e01d-4602-ba33-7e7e61e55b55" />

<img width="1453" height="712" alt="Screenshot 2026-10-11 222304" src="https://github.com/user-attachments/assets/1c1e44a7-c525-47be-afd9-590888360bc0" />




# 📈 Results
✅ Successfully aggregates live news from multiple public RSS feeds (BBC, TechCrunch, NYT).

✅ Generates accurate, citation-linked bullet summaries at three configurable detail levels.

✅ Runs entirely on a single free-tier T4 GPU (15 GB VRAM) with 4-bit quantization, leaving VRAM headroom for larger models.

✅ Delivers formatted HTML digests to any inbox via Gmail SMTP with no paid email API.

✅ Reproducible end-to-end from a single Colab notebook + one ngrok token.



# 🔮 Future Improvements

- 🗓️ Scheduled digests — add a daily cron trigger so the briefing arrives every morning without manual clicks.

- 🌍 Multi-language support — translate and summarize non-English sources using the LLM's multilingual capability.

- 🧠 Sentiment & topic tagging — auto-label each story with a topic (Politics / Tech / Economy) and sentiment score.

- 📊 Story clustering & deduplication — group reports on the same event from multiple outlets into one merged bullet.

- 🔐 Credential vault — replace the raw sidebar password field with Colab userdata or Streamlit secrets.toml.

- 📱 Mobile-friendly layout — polish the Streamlit theme for phone screens.

- 🧪 Evaluation harness — ROUGE / BERTScore comparison against human-written summaries from the same feeds.

# 📚 About the Internship
This project was developed as part of the Tips Hindawi Internship (August–October) 2026, and it will be showcased on the official Tips Hindawi website.

Tips Hindawi is the internships department of Edrak for Ai, and the internship encourages participants to build real-world projects, apply practical skills, and showcase their work through GitHub.

For more information about the internship, training programs, and upcoming batches, visit the official Tips Hindawi website.

# 📄 License
This project is shared for educational and portfolio purposes.
