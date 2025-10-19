#!/usr/bin/env python3
# streamlit run layout.py

import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="AI Network Brain",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- THEME & CSS ----------
st.markdown("""
<style>
:root{
  --bg-grad: linear-gradient(135deg, #0f2027 0%, #203a43 25%, #2c5364 50%, #1a2a6c 75%, #0f1642 100%);
  --glass: rgba(255,255,255,0.08);
  --glass-border: rgba(255,255,255,0.2);
  --text: #e7eef8;
  --muted: #b8c6d9;
}
html, body, [data-testid="stAppViewContainer"]{
  background: var(--bg-grad) !important;
  color: var(--text);
}
[data-testid="stHeader"] { background: transparent; }
.block-container{ padding-top: 0; }

.pulse-wrap{
  position: fixed; inset: 0; overflow: hidden; pointer-events: none; z-index:0;
}
.blob{
  position:absolute; width:24rem; height:24rem; filter: blur(48px); border-radius:9999px;
  animation: pulse 6s ease-in-out infinite;
}
.blob.b1{ top:-2rem; left:-2rem; background: rgba(59,130,246,.20); animation-duration:4s; }
.blob.b2{ right:-2rem; bottom:-2rem; background: rgba(79,70,229,.20); animation-duration:6s; animation-delay:1.5s; }
.blob.b3{ left:50%; top:50%; transform:translate(-50%,-50%); background: rgba(8,145,178,.15); animation-duration:8s; animation-delay:3s; }

@keyframes pulse {
  0%,100% { transform: translate(0,0) scale(1); opacity: .9; }
  50%     { transform: translate(10px,-8px) scale(1.06); opacity: 1; }
}

/* Glass header & footer */
.glass{
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  background: var(--glass);
  border: 1px solid var(--glass-border);
  border-left: 0; border-right: 0;
  box-shadow: 0 0 0 1px rgba(255,255,255,0.05) inset, 0 10px 30px rgba(0,0,0,0.25);
}

/* Brain badge */
.badge{
  width: 3rem; height: 3rem;
  display:flex; align-items:center; justify-content:center;
  border-radius: 1rem;
  background: linear-gradient(135deg,#3b82f6 0%, #4f46e5 100%);
  border:1px solid var(--glass-border);
  box-shadow: 0 0 30px rgba(59,130,246,0.5);
}

/* Grid footer */
.footer-grid{
  display:grid; grid-template-columns: 1fr;
  gap: 1rem; text-align:center;
}
@media(min-width: 640px){
  .footer-grid{ grid-template-columns: repeat(3,1fr); }
}

/* Utility */
.h1{ font-size: clamp(1.25rem, 2.4vw, 1.75rem); font-weight: 800; color: #fff; margin: 0; }
.sub{ font-size: .95rem; color: #bfdbfe; margin-top: .2rem; }
.center{ display:flex; align-items:center; gap:.75rem; }
.container{ max-width: 80rem; margin-inline:auto; padding: 1rem 1.25rem; }
.section{ position:relative; z-index:1; }
.card{
  border-radius: 1rem; padding: 1rem;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.12);
}
</style>

<div class="pulse-wrap">
  <div class="blob b1"></div>
  <div class="blob b2"></div>
  <div class="blob b3"></div>
</div>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown("""
<div class="glass section">
  <div class="container">
    <div class="center" style="justify-content:center;">
      <div class="badge">
        <!-- Inline SVG "brain" icon -->
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
          <path d="M12 3a3 3 0 0 0-3 3v.5a2.5 2.5 0 0 0-2.5 4.33A2.999 2.999 0 0 0 6 14a3 3 0 0 0 3 3h.5A2.5 2.5 0 0 0 12 20a2.5 2.5 0 0 0 2.5-3H15a3 3 0 0 0 3-3c0-.61-.18-1.17-.5-1.64A2.5 2.5 0 0 0 17.5 6H17a3 3 0 0 0-5-3Z" stroke="white" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <div style="text-align:left;">
        <div class="h1">AI Network Brain</div>
        <div class="sub">Intelligent network analysis powered by RAG + AI</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------- (Optional) MOBILE MENU / SIDEBAR ACTION ----------
# Streamlit doesn’t have a native mobile hamburger toggle, but we can provide a compact menu.
with st.container():
    cols = st.columns([1,1,1,6])
    with cols[0]:
        st.button("☰ Menu", help="Quick actions", use_container_width=True)
    with cols[1]:
        st.page_link("https://github.com", label="Docs", help="Project docs")
    with cols[2]:
        st.page_link("https://example.com", label="Status", help="System status")

# ---------- MAIN CONTENT (replace with your children) ----------
st.markdown('<div class="section">', unsafe_allow_html=True)
with st.container():
    st.markdown("### Dashboard")
    st.markdown(
        "Use this area like `{children}` in React. Drop your Streamlit components here."
    )

    # Example cards to show style
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="card">**AI Brain:** RAG + distilgpt2</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card">**Analysis:** Real-time CLI</div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="card">**Now:** {datetime.now().strftime("%b %d, %Y %I:%M %p")}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ---------- FOOTER ----------
st.markdown("""
<div class="glass section" style="margin-top:2rem;">
  <div class="container">
    <div class="footer-grid" style="font-size:.95rem; color:#bfdbfe;">
      <div><span style="color:#fff; font-weight:700;">AI Brain:</span> RAG + distilgpt2</div>
      <div><span style="color:#fff; font-weight:700;">Analysis:</span> Real-time CLI</div>
      <div><span style="color:#fff; font-weight:700;">Version:</span> 8.0.0</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)