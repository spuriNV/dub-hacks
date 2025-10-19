import streamlit as st
import requests
import json
import re, html
from datetime import datetime

# ---------- Page ----------
st.set_page_config(
    page_title="IT-Mobile",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- THEME & CSS (Vercel ai-chatbot-inspired) ----------
st.markdown("""
<style>
/* Font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [data-testid="stAppViewContainer"]{
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", "Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol";
}

/* Colors */
:root{
  --bg:#0a0a0b; --panel:#111214; --muted:#9aa3ae; --text:#eceff4; --soft:#1b1d22;
  --brand: linear-gradient(90deg,#06b6d4 0%, #8b5cf6 50%, #ec4899 100%);
  --ring: rgba(139,92,246,0.4);
}
html, body, [data-testid="stAppViewContainer"]{ background: var(--bg); color: var(--text); }
[data-testid="stHeader"] { background: transparent; }
.block-container{ padding-top: 1.2rem; }

/* Top nav */
.nav-wrap{
  width: 100%; display:flex; justify-content:center; position: sticky; top:0; z-index:10;
  backdrop-filter: blur(10px); background: rgba(10,10,11,0.55);
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.nav-inner{ width: min(880px, 92vw); display:flex; align-items:center; gap:.75rem; padding:.6rem 0; }
.badge{ font-size:.75rem; padding:.25rem .5rem; border-radius:.5rem; background: rgba(255,255,255,0.06); color:var(--muted); border:1px solid rgba(255,255,255,0.08); }

/* Hero */
.hero{ width:100%; display:flex; justify-content:center; margin: 10px 0 18px 0; }
.hero-inner{
  width:min(880px, 92vw); background: var(--panel); border:1px solid rgba(255,255,255,0.08);
  padding: 16px 18px; border-radius: 14px; position:relative; overflow:hidden;
}
.hero-inner:before{
  content:""; position:absolute; inset:0; pointer-events:none;
  background: radial-gradient(1000px 300px at -10% -40%, rgba(139,92,246,.18), transparent 60%),
              radial-gradient(600px 300px at 120% -20%, rgba(6,182,212,.20), transparent 60%);
}
.brand-title{ font-weight:700; letter-spacing:.3px; font-size:1.15rem; display:flex; align-items:center; gap:.5rem;
  background: var(--brand); -webkit-background-clip: text; background-clip:text; color: transparent; }
.subtle{ color: var(--muted); }

/* Chat */
.chat-wrap{ width:100%; display:flex; justify-content:center; margin-top:.5rem; }
.chat-inner{ width:min(880px, 92vw); }
.msg{ display:flex; gap:.75rem; margin: 10px 0; padding: 10px 12px; border-radius: 14px; border:1px solid rgba(255,255,255,0.08); position:relative; }
.msg.assistant{ background: rgba(255,255,255,0.03); }
.msg.user{
  background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
}
.avatar{
  width:34px; height:34px; border-radius: 10px; display:flex; align-items:center; justify-content:center;
  background: var(--soft); border:1px solid rgba(255,255,255,0.08); flex:0 0 auto; font-size: 18px;
}
.bubble{ width:100%; }
.bubble .role{ font-size:.8rem; color:var(--muted); margin-bottom:4px; }
.bubble .content{ line-height:1.6; }
.bubble code, .bubble pre{
  background: #0f1115; border:1px solid rgba(255,255,255,0.08); border-radius:10px; padding:.2rem .35rem;
}
.bubble pre { padding: .75rem .9rem; overflow:auto; }

/* Footer */
.footer{ width:100%; display:flex; justify-content:center; margin-top: 8px; color: var(--muted); font-size:.85rem; }

/* Composer — removed outer border to avoid “double bar” */
.input-wrap{ position:sticky; bottom: 10px; width:100%; display:flex; justify-content:center; margin-top: 6px; }
.input-inner{ width:min(880px, 92vw); background: transparent; border-radius: 14px; padding: 6px; border: none; }
.input-row{
  display:flex; gap:8px; align-items:center; background: #0f1115;
  border:1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 8px 10px; outline: 1.5px solid transparent;
}
.input-row:focus-within{ outline-color: var(--ring); }
.input-row textarea{ background: transparent !important; color: var(--text) !important; }
.btn{
  padding: 7px 10px; border-radius: 10px; border:1px solid rgba(255,255,255,0.12);
  background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02)); color: var(--text); cursor: pointer;
}
.btn:hover{ background: rgba(255,255,255,0.06); }
.typing{ display:inline-flex; gap:4px; align-items:center; margin-left: 3px; }
.dot{ width:6px; height:6px; background:#cbd5e1; border-radius:50%; animation: bounce 1.1s infinite ease-in-out; }
.dot:nth-child(2){ animation-delay: .15s } .dot:nth-child(3){ animation-delay: .3s }
@keyframes bounce{ 0%, 80%, 100%{ transform: translateY(0); opacity:.5;} 40%{ transform: translateY(-4px); opacity:1;} }

/* Sidebar — prettier cards */
.sidebar-card{
  background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
  border:1px solid rgba(255,255,255,0.08); border-radius: 14px; padding: 12px; margin-bottom: 12px;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,0.02);
}
.sidebar-title{ font-weight:700; margin-bottom: 6px; letter-spacing:.2px; }
.sidebar-row{ display:flex; align-items:center; justify-content:space-between; margin:6px 0; }
.sidebar-left{ display:flex; align-items:center; gap:8px; }
.status-dot{ display:inline-block; width:10px; height:10px; border-radius:50%; }
.good { background:#22c55e; } .warn { background:#f59e0b; } .err { background:#ef4444; } .muted { background:#64748b; }

/* Hide default chat chrome */
div[data-testid="stChatMessage"] { background: transparent; border: none; }
</style>
""", unsafe_allow_html=True)

# ---------- Session State ----------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_url" not in st.session_state:
    st.session_state.api_url = "http://localhost:8088"

# ---------- API helpers ----------
def get_network_status():
    try:
        resp = requests.get(f"{st.session_state.api_url}/network-status", timeout=10)
        return resp.json() if resp.status_code == 200 else None
    except Exception as e:
        st.sidebar.error(f"Network status error: {e}")
        return None

def get_ai_status():
    try:
        resp = requests.get(f"{st.session_state.api_url}/ai-status", timeout=10)
        return resp.json() if resp.status_code == 200 else None
    except Exception as e:
        st.sidebar.error(f"AI status error: {e}")
        return None

def send_chat_message(message: str):
    try:
        resp = requests.post(f"{st.session_state.api_url}/chat", json={"message": message}, timeout=30)
        return resp.json() if resp.status_code == 200 else None
    except Exception as e:
        st.error(f"Error connecting to AI brain: {e}")
        return None

# ---------- Minimal Markdown→HTML (no stray asterisks) ----------
_bold = re.compile(r"\*\*(.+?)\*\*")
_ital = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")
_code = re.compile(r"`([^`]+)`")
def md_to_html(txt: str) -> str:
    # escape HTML first
    s = html.escape(txt)
    # inline code
    s = _code.sub(r"<code>\\1</code>", s)
    # bold then italics
    s = _bold.sub(r"<strong>\\1</strong>", s)
    s = _ital.sub(r"<em>\\1</em>", s)
    # line breaks
    s = s.replace("\n", "<br>")
    return s

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown('<div class="sidebar-card"><div class="sidebar-title">🔧 Settings</div>', unsafe_allow_html=True)
    api_url = st.text_input("API URL", value=st.session_state.api_url, help="URL of the AI brain API server")
    reset = st.button("Clear Chat History")
    st.markdown('</div>', unsafe_allow_html=True)

    if api_url != st.session_state.api_url:
        st.session_state.api_url = api_url
        st.rerun()
    if reset:
        st.session_state.messages = []
        st.success("Chat history cleared.")

    # Network Status
    st.markdown('<div class="sidebar-card"><div class="sidebar-title">📊 Network Status</div>', unsafe_allow_html=True)
    net = get_network_status()
    if net:
        wifi = net.get('network_data', {}).get('wifi', {})
        conn = net.get('network_data', {}).get('connectivity', {})
        perf = net.get('network_data', {}).get('performance', {})

        wifi_status = wifi.get('status', 'unknown')
        wifi_ssid = wifi.get('ssid', 'Unknown')
        signal = wifi.get('signal_strength', 'unknown')
        dot = "good" if wifi_status == "connected" else ("warn" if wifi_status == "unknown" else "err")
        st.markdown(f"""
        <div class="sidebar-row">
          <div class="sidebar-left"><span class="status-dot {dot}"></span><strong>Wi-Fi</strong></div>
          <div>{'Connected' if wifi_status=='connected' else ('Unknown' if wifi_status=='unknown' else 'Not Connected')}</div>
        </div>
        <div class="subtle">SSID: {html.escape(str(wifi_ssid))} • Signal: {html.escape(str(signal))} dBm</div>
        """, unsafe_allow_html=True)

        dot2 = "good" if conn.get('internet_connected', False) else "err"
        st.markdown(f"""
        <div class="sidebar-row">
          <div class="sidebar-left"><span class="status-dot {dot2}"></span><strong>Internet</strong></div>
          <div>{'Online' if conn.get('internet_connected', False) else 'Offline'}</div>
        </div>
        <div class="subtle">Latency: {html.escape(str(conn.get('latency','–')))}</div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="sidebar-row"><div class="sidebar-left"><strong>Performance</strong></div><div></div></div>
        <div class="subtle">Quality: {html.escape(str(perf.get('network_quality','–')).title())} • Active Connections: {html.escape(str(perf.get('active_connections',0)))}</div>
        """, unsafe_allow_html=True)
    else:
        st.error("Unable to connect to AI brain")
    st.markdown('</div>', unsafe_allow_html=True)

    # AI Model Status
    st.markdown('<div class="sidebar-card"><div class="sidebar-title">🤖 AI Brain Status</div>', unsafe_allow_html=True)
    ai = get_ai_status()
    if ai:
        ai_model = ai.get('ai_model_loaded', False)
        rag_enabled = ai.get('rag_enabled', False)
        kb = ai.get('knowledge_base_size', 0)
        st.markdown(f"""
        <div class="sidebar-row">
          <div class="sidebar-left"><span class="status-dot {'good' if ai_model else 'warn'}"></span><strong>Model</strong></div>
          <div>{'distilgpt2' if ai_model else 'Rule-based'}</div>
        </div>
        <div class="sidebar-row">
          <div class="sidebar-left"><span class="status-dot {'good' if rag_enabled else 'err'}"></span><strong>RAG</strong></div>
          <div>{'Enabled' if rag_enabled else 'Disabled'}</div>
        </div>
        <div class="subtle">KB: {kb} items</div>
        """, unsafe_allow_html=True)
    else:
        st.error("Unable to get AI brain status")
    st.markdown('</div>', unsafe_allow_html=True)

    # Hints
    st.markdown('<div class="sidebar-card"><div class="sidebar-title">💡 Try asking</div>', unsafe_allow_html=True)
    st.markdown("- What's wrong with my WiFi?\n- My internet is slow, help me\n- How can I improve my signal?\n- Check my network security\n- Why is my connection dropping?")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Top nav ----------
st.markdown("""
<div class="nav-wrap">
  <div class="nav-inner">
    <span class="badge">v7.0.0</span>
    <span class="brand-title">AI Network Brain</span>
    <span class="badge">RAG + distilgpt2</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------- Hero / summary ----------
st.markdown("""
<div class="hero">
  <div class="hero-inner">
    <div style="display:flex; align-items:center; justify-content:space-between; gap:10px; flex-wrap:wrap;">
      <div>
        <div class="brand-title">Smart network diagnostics</div>
        <div class="subtle"> AI Powered for Wi-Fi and internet health</div>
      </div>
      <div>Real-time CLI analysis</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------- Chat history ----------
st.markdown('<div class="chat-wrap"><div class="chat-inner">', unsafe_allow_html=True)

if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hey! I can troubleshoot Wi-Fi, latency, and general connectivity. Ask me anything about your network.",
        "time": datetime.now().isoformat(timespec="seconds")
    })

for msg in st.session_state.messages:
    role = msg.get("role","assistant")
    content = msg.get("content","")
    time_str = msg.get("time","")
    avatar = "🧑‍💻" if role == "user" else "🤖"
    role_name = "You" if role == "user" else "Assistant"

    # If we stored raw markdown, render it nicely (no literal asterisks)
    safe_html = content if content.strip().startswith("<") else md_to_html(content)

    st.markdown(f"""
    <div class="msg {role}">
      <div class="avatar">{avatar}</div>
      <div class="bubble">
        <div class="role">{role_name} • <span class="subtle">{time_str}</span></div>
        <div class="content">{safe_html}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)

# ---------- Input row ----------
st.markdown('<div class="input-wrap"><div class="input-inner">', unsafe_allow_html=True)
colA, colB = st.columns([1, 7])
with colA:
    st.markdown("**Message**")
with colB:
    st.markdown('<div class="input-row">', unsafe_allow_html=True)
    prompt = st.chat_input("Ask the AI brain about your network…")
    st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div></div>', unsafe_allow_html=True)

# ---------- Handle send ----------
if prompt:
    now = datetime.now().isoformat(timespec="seconds")
    st.session_state.messages.append({"role":"user","content":prompt,"time":now})

    # Typing bubble
    st.markdown(f"""
    <div class="chat-wrap"><div class="chat-inner">
      <div class="msg user">
        <div class="avatar">🧑‍💻</div>
        <div class="bubble">
          <div class="role">You • <span class="subtle">{now}</span></div>
          <div class="content">{md_to_html(prompt)}</div>
        </div>
      </div>
      <div class="msg assistant">
        <div class="avatar">🤖</div>
        <div class="bubble">
          <div class="role">Assistant • <span class="subtle">thinking</span></div>
          <div class="content">Analyzing<span class="typing"><span class="dot"></span><span class="dot"></span><span class="dot"></span></span></div>
        </div>
      </div>
    </div></div>
    """, unsafe_allow_html=True)

    resp = send_chat_message(prompt)
    if resp:
        ai_text = resp.get("response", "Sorry, I couldn’t process that.")
        model_on = resp.get("ai_model_used", False)
        rag_on = resp.get("rag_enabled", False)
        ts = resp.get("timestamp", now)

        ai_text_html = md_to_html(ai_text)  # <-- clean markdown (no stars)
        st.session_state.messages.append({
            "role":"assistant",
            "content": ai_text_html + (
                f"<br><br><small class='subtle'>AI Model: {'distilgpt2' if model_on else 'rule-based'} • RAG: {'Enabled' if rag_on else 'Disabled'} • {ts}</small>"
            ),
            "time": ts
        })
        st.rerun()
    else:
        st.session_state.messages.append({
            "role":"assistant",
            "content":"❌ Failed to reach the AI brain. Please check if the API server is running.",
            "time": now
        })
        st.rerun()

# ---------- Footer ----------
st.markdown("""
<div class="footer">
  <div style="width:min(880px, 92vw); text-align:center;">
    Built with Streamlit • Styled after Vercel's ai-chatbot • <span class="subtle">RAG + distilgpt2</span>
  </div>
</div>
""", unsafe_allow_html=True)
