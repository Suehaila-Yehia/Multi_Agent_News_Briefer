%%writefile news_app.py
import os

os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")

import subprocess, threading, time, socket, os
from pyngrok import ngrok, conf
import re
import html
import smtplib
import feedparser
import torch
import streamlit as st
import markdown as md_lib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

st.set_page_config(page_title="AI Daily News Briefing", page_icon="📰", layout="wide")

MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"   # 7B also fits on T4 (15 GB) but is slower


# ------------------------------------------------------------------ #
#  Model — cached so it loads only once per server process
# ------------------------------------------------------------------ #
@st.cache_resource(show_spinner="🔄 Loading LLM (first run only)…")
def load_model():
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)
    tok = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    tok.pad_token = tok.eos_token
    mdl = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, device_map="auto",
        quantization_config=bnb, trust_remote_code=True,
    )
    return tok, mdl


def generate_llm(prompt, max_tokens=300, temperature=0.7):
    tok, mdl = load_model()
    messages = [
        {"role": "system", "content": (
            "You are a professional lead news editor. Synthesize complex stories "
            "into objective, high-density bullet points without conversational filler."
        )},
        {"role": "user", "content": prompt},
    ]
    text = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tok(text, return_tensors="pt").to(mdl.device)

    temp = max(float(temperature if temperature is not None else 0.7), 0.01)
    with torch.no_grad():
        out = mdl.generate(
            **inputs, max_new_tokens=max_tokens, do_sample=True,
            temperature=temp, top_p=0.9, pad_token_id=tok.eos_token_id,
        )
    gen = out[0][inputs.input_ids.shape[1]:]
    return tok.decode(gen, skip_special_tokens=True).strip()


# ------------------------------------------------------------------ #
#  Agents
# ------------------------------------------------------------------ #
class NewsAgent:
    def __init__(self, default_rss="http://feeds.bbci.co.uk/news/world/rss.xml"):
        self.default_rss = default_rss

    def _clean(self, text):
        if not text:
            return ""
        text = html.unescape(text)
        text = re.sub(r"<[^>]+>", "", text)
        return re.sub(r"\s+", " ", text).strip()

    def fetch_latest_news(self, rss_url=None, limit=5):
        url = (rss_url.strip()
               if (rss_url and isinstance(rss_url, str) and rss_url.strip())
               else self.default_rss)
        feed = feedparser.parse(url)
        return [{
            "title":   self._clean(e.get("title", "")),
            "summary": self._clean(e.get("summary", e.get("title", ""))),
            "link":    e.get("link", "#"),
        } for e in feed.entries[: int(limit)]]


class SummarizerAgent:
    def summarize(self, news_items, temperature=0.1, length_option="Detailed"):
        if not news_items:
            return "No news items available."
        news_text = "\n".join(
            f"- Title: {i['title']} | Context: {i['summary']} | Link: {i['link']}"
            for i in news_items
        )
        count = len(news_items)

        if length_option == "Brief":
            instr, max_tok = "Write a crisp 1-sentence bullet point per story.", 400
        elif length_option == "Standard":
            instr, max_tok = "Write 1 to 2 clear, informative sentences per story.", 600
        else:
            instr = ("Write 2 to 3 detailed, comprehensive sentences per story "
                     "explaining WHAT happened and WHY it matters.")
            max_tok = 1000

        prompt = f"""You are a news editor assistant. Create a daily news briefing based strictly on the news feed provided below.

<news_feed>
{news_text}
</news_feed>

CRITICAL INSTRUCTIONS:
1. Start with the header "**Latest Headlines**".
2. Generate EXACTLY {count} bullet points (one for each story above).
3. EVERY bullet point MUST start with a hyphen and a space ("- ").
4. {instr}
5. End EVERY bullet point with: ([Read Full Story](URL))

Generate the output now:"""
        return generate_llm(prompt, max_tokens=max_tok, temperature=temperature)


def markdown_to_html_email(markdown_text):
    body = md_lib.markdown(markdown_text)
    return f"""<html><head><style>
      body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
      a {{ color: #0066cc; text-decoration: underline; font-weight: bold; }}
      li {{ margin-bottom: 12px; }}
    </style></head><body>
      <div style="max-width:650px;margin:0 auto;padding:20px;
                  border:1px solid #e0e0e0;border-radius:8px;">{body}</div>
    </body></html>"""


class EmailAutomationAgent:
    def send_email(self, recipient_email, subject, body, sender_email, sender_password):
        if not recipient_email or not sender_email or not sender_password:
            return "⚠️ Missing email credentials."
        msg = MIMEMultipart("alternative")
        msg["From"], msg["To"], msg["Subject"] = sender_email, recipient_email, subject
        msg.attach(MIMEText(body, "plain"))
        msg.attach(MIMEText(markdown_to_html_email(body), "html"))
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as s:
                s.starttls()
                s.login(sender_email, sender_password)
                s.send_message(msg)
            return f"✅ Formatted digest successfully emailed to {recipient_email}!"
        except Exception as e:
            return f"❌ Failed to send email: {e}"


# ------------------------------------------------------------------ #
#  Streamlit UI
# ------------------------------------------------------------------ #
news_agent       = NewsAgent()
summarizer_agent = SummarizerAgent()
email_agent      = EmailAutomationAgent()

st.title("📰 AI Daily News Briefing Agent")
st.caption("Aggregate RSS feeds, control LLM temperature, audit raw sources, "
           "and dispatch email briefings.")

with st.sidebar:
    st.header("⚙️ News & Model Settings")
    summary_length = st.radio("Summary Detail Level",
                              ["Brief", "Standard", "Detailed"], index=2)
    preset_rss = st.selectbox(
        "Preset Source",
        options=[
            ("BBC World News", "http://feeds.bbci.co.uk/news/world/rss.xml"),
            ("TechCrunch",     "https://techcrunch.com/feed/"),
            ("NYT World News", "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"),
        ],
        format_func=lambda x: x[0],
    )
    custom_rss    = st.text_input("Custom RSS URL (overrides preset)",
                                  placeholder="https://example.com/rss.xml")
    article_limit = st.slider("Article Count", 1, 10, 5, 1)
    temperature   = st.slider("Temperature (Hallucination Control)", 0.0, 1.0, 0.1, 0.05)

    st.header("📧 Email Credentials")
    recipient_email = st.text_input("Recipient Email", placeholder="user@example.com")
    sender_email    = st.text_input("Sender Gmail",    placeholder="your_email@gmail.com")
    sender_password = st.text_input("App Password", type="password")

    run_btn = st.button("🚀 Generate News Digest", type="primary",
                        use_container_width=True)

if run_btn:
    target_url = custom_rss.strip() if custom_rss.strip() else preset_rss[1]

    with st.spinner("📡 Fetching news items…"):
        news_items = news_agent.fetch_latest_news(rss_url=target_url, limit=article_limit)

    if not news_items:
        st.error("❌ Execution failed: Invalid or empty RSS feed.")
        st.stop()

    with st.spinner("🧠 Summarizing with LLM (first run downloads the model)…"):
        summary_report = summarizer_agent.summarize(
            news_items, temperature=temperature, length_option=summary_length
        )

    email_status = "Digest generated (Email step skipped)."
    if recipient_email and sender_email and sender_password:
        with st.spinner("✉️ Sending email…"):
            email_status = email_agent.send_email(
                recipient_email=recipient_email,
                subject=f"Daily News Digest - {datetime.now().strftime('%Y-%m-%d')}",
                body=summary_report,
                sender_email=sender_email,
                sender_password=sender_password,
            )

    st.success(email_status)
    st.markdown(summary_report)

    with st.expander("🔍 Audit Raw RSS Feed Data", expanded=False):
        st.json(news_items)
else:
    st.info("Configure options in the sidebar, then click **Generate News Digest**.")





NGROK_TOKEN = "YOUR TOKEN HERE"

# kill any stale tunnels / previous streamlit
try:
    ngrok.kill()
except Exception:
    pass
!pkill -f streamlit || true

def free_port():
    s = socket.socket()
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port

PORT = free_port()

def run_streamlit():
    env = os.environ.copy()
    env["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
    subprocess.run([
        "streamlit", "run", "news_app.py",
        "--server.port", str(PORT),
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false",
        "--browser.gatherUsageStats", "false",
    ], env=env)

threading.Thread(target=run_streamlit, daemon=True).start()
time.sleep(8)   # wait for Streamlit to boot

conf.get_default().auth_token = NGROK_TOKEN
public_url = ngrok.connect(PORT, bind_tls=True).public_url
print("🌐 Streamlit public URL:", public_url)
print("Open the URL above in a new tab — first click will download the model.")
