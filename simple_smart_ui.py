#!/usr/bin/env python3
"""
AI Network Brain — Streamlit (all‑Python, Vercel‑style UI)
Vercel-style chat UI in pure Streamlit that integrates your sidebar features:
- 🔧 Settings (API URL persisted in session)
- 📊 Network Status (wifi / internet / performance)
- 🤖 AI Brain Status (model + RAG)
- 💬 Chat with analysis details (ai_model_used, rag_enabled, timestamp)
- 🔁 Auto-refresh health cards every 5s (without disrupting chat)

Requires: streamlit, requests
Run: streamlit run app.py
"""
from __future__ import annotations
import json
import time
from datetime import datetime
from typing import Any, Dict, Optional

import requests
import streamlit as st

# ------------------------------
# Page config
# ------------------------------
st.set_page_config(
    page_title="AI Network Brain",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------
# Custom CSS (Vercel-ish, soft gradients)
# ------------------------------
st.markdown(
    """
    <style>
      :root {
        --ring: 0 0 0 2px rgba(99,102,241,.35);
      }
      .ver-card { border:1px solid #e5e7eb; border-radius: 1rem; padding: 1rem; background: #fff; }
      .ver-card.gradient-purple { background: linear-gradient(90deg,#6366f1 0%,#a855f7 100%); color:#fff; border:none; }
      .ver-card.gradient-aqua { background: linear-gradient(90deg,#fb7185 0%,#2dd4bf 100%); color:#fff; border:none; }
      .pill { display:inline-flex; align-items:center; gap:.4rem; border-radius:999px; padding:.25rem .6rem; font-size:.75rem; border:1px solid #e5e7eb; background:#fff; }
      .dot { width:10px; height:10px; border-radius:50%; display:inline-block; }
      .good { background:#22c55e; }
      .warn { background:#f59e0b; }
      .bad  { background:#ef4444; }
      .muted { background:#94a3b8; }
      .chip { border:1px solid #e5e7eb; border-radius:999px; padding:.25rem .75rem; font-size:.75rem; cursor:pointer; }
      .chip:hover { background:#f1f5f9; }
      .input { width:100%; border:1px solid #e5e7eb; border-radius:1rem; padding:.6rem .9rem; outline:none; }
      .input:focus { box-shadow: var(--ring); }
      .send { border-radius:1rem; padding:.6rem 1rem; font-weight:600; border:none; background:#4f46e5; color:#fff; }
      .send:disabled { background:#e5e7eb; color:#94a3b8; }
      .msg { border-radius:1rem; padding:1rem; border:1px solid #e5e7eb; background:#f8fafc; }
      .msg.user { background:#0f172a; color:#fff; border-color:#0b1222; }
      .avatar { width:36px; height:36px; border-radius:999px; display:flex; align-items:center; justify-content:center; font-size:18px; }
      .avatar.user { background:#0b1222; color:#fff; }
      .avatar.assistant { background:#fff; border:1px solid #e5e7eb; }
      details summary { cursor:pointer; color:#64748b; }
      .footer { color:#94a3b8; font-size:.75rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------
# Session State
# ------------------------------
DEFAULT_API = "http://localhost:8088"
if "api_url" not in st.session_state:
    st.session_state.api_url = DEFAULT_API
if "messages" not in st.session_state:
    st.session_state.messages = []  # list[dict(role, content, meta?)]
if "_last_health_pull" not in st.session_state:
    st.session_state._last_health_pull = 0.0
if "_health_cache" not in st.session_state:
    st.session_state._health_cache = {"network": None, "ai": None}

# ------------------------------
# API Helpers
# ------------------------------

def _get(url: str, timeout: float = 8.0) -> Optional[Dict[str, Any]]:
    try:
        r = requests.get(url, timeout=timeout)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None
    return None


def _post(url: str, payload: Dict[str, Any], timeout: float = 15.0) -> Optional[Dict[str, Any]]:
    try:
        r = requests.post(url, json=payload, timeout=timeout)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None
    return None


def pull_health(force: bool = False) -> Dict[str, Any]:
    """Poll /network-status and /ai-status at most once every 5s.
    Returns cached dict: {"network":..., "ai":...}
    """
    now = time.time()
    if force or (now - st.session_state._last_health_pull) > 5:
        ns = _get(f"{st.session_state.api_url}/network-status")
        ai = _get(f"{st.session_state.api_url}/ai-status")
        st.session_state._health_cache = {"network": ns, "ai": ai}
        st.session_state._last_health_pull = now
    return st.session_state._health_cache


# ------------------------------
# UI Helpers
# ------------------------------

def status_dot(kind: str) -> str:
    cls = {"good": "good", "warning": "warn", "error": "bad"}.get(kind, "muted")
    return f'<span class="dot {cls}"></span>'


def card(title: str, body: str, gradient: Optional[str] = None):
    cls = "ver-card " + (f"gradient-{gradient}" if gradient else "")
    st.markdown(f"<div class='{cls}'><div style='font-weight:600;font-size:.85rem;opacity:.9'>{title}</div><div style='margin-top:.5rem'>{body}</div></div>", unsafe_allow_html=True)


# ------------------------------
# Sidebar
# ------------------------------
with st.sidebar:
    st.markdown("## 🧠 AI Network Brain\nControl Panel")

    # Settings
    api_url = st.text_input("API URL", value=st.session_state.api_url, help="Your AI brain API, e.g., http://localhost:8088")
    if api_url != st.session_state.api_url:
        st.session_state.api_url = api_url
        # on change we force a health pull
        pull_health(force=True)

    st.divider()

    # Health
    health = pull_health()
    net = (health.get("network") or {}).get("network_data", {}) if health.get("network") else {}
    wifi = net.get("wifi", {})
    conn = net.get("connectivity", {})
    perf = net.get("performance", {})
    ai = health.get("ai") or {}

    # Network Status card
    wifi_kind = "good" if wifi.get("status") == "connected" else ("warning" if wifi.get("status") == "unknown" else ("error" if wifi else "muted"))
    internet_kind = "good" if conn.get("internet_connected") else ("error" if conn else "muted")

    wifi_html = f"""
      <div style='margin-bottom:.75rem'>
        <div style='font-weight:600'>Wi‑Fi</div>
        <div>{status_dot(wifi_kind)} {('Connected to <b>'+wifi.get('ssid','Unknown')+'</b>') if wifi.get('status')=='connected' else ('Status unknown' if wifi.get('status')=='unknown' else ('Not connected' if wifi else 'No data'))}</div>
        {('<div style="opacity:.9">Signal: '+str(wifi.get('signal_strength'))+' dBm</div>') if wifi.get('signal_strength') is not None else ''}
      </div>
      <div style='margin-bottom:.75rem'>
        <div style='font-weight:600'>Internet</div>
        <div>{status_dot(internet_kind)} {('Online' if conn.get('internet_connected') else ('Offline' if conn else 'No data'))}</div>
        {('<div style="opacity:.9">Latency: '+str(conn.get('latency'))+'</div>') if conn.get('latency') is not None else ''}
      </div>
      <div>
        <div style='font-weight:600'>Performance</div>
        <div style='opacity:.9'>Quality: {(perf.get('network_quality') or '—') if perf is not None else '—'}</div>
        <div style='opacity:.9'>Active Connections: {perf.get('active_connections','—')}</div>
      </div>
    """
    card("📊 Network Status", wifi_html, gradient="purple")

    st.markdown("")

    # AI Brain Status card
    model_kind = "good" if ai.get("ai_model_loaded") else ("warning" if ai else "muted")
    rag_kind = "good" if ai.get("rag_enabled") else ("error" if ai else "muted")

    ai_html = f"""
      <div class='ver-card' style='background:rgba(255,255,255,.15); border-radius:.75rem'>
        <div style='font-weight:600; display:flex; align-items:center; gap:.5rem'>{status_dot(model_kind)} Model</div>
        <div style='opacity:.9'>{'distilgpt2 Loaded' if ai.get('ai_model_loaded') else ('Rule‑based Mode' if ai else 'No data')}</div>
      </div>
      <div style='height:.5rem'></div>
      <div class='ver-card' style='background:rgba(255,255,255,.15); border-radius:.75rem'>
        <div style='font-weight:600; display:flex; align-items:center; gap:.5rem'>{status_dot(rag_kind)} RAG Knowledge</div>
        <div style='opacity:.9'>{(str(ai.get('knowledge_base_size',0))+' Items Loaded') if ai.get('rag_enabled') else ('Not Available' if ai else 'No data')}</div>
      </div>
    """
    card("🤖 AI Brain Status", ai_html, gradient="aqua")

    st.markdown("")

    # Quick prompts
    st.markdown("### 💡 Ask the AI Brain")
    cols = st.columns(2)
    examples = [
        "What's wrong with my Wi‑Fi?",
        "My internet is slow, help me",
        "How can I improve my signal?",
        "Check my network security",
        "Why is my connection dropping?",
    ]
    for i, ex in enumerate(examples):
        with cols[i % 2]:
            if st.button(ex, key=f"ex_{i}"):
                # stage it in a temp key used by main area to populate input
                st.session_state.__staged_prompt = ex

    st.markdown("<div class='footer'>v7.0.0 • Real‑time CLI • RAG + distilgpt2</div>", unsafe_allow_html=True)

# Auto-refresh health panes every 5s without resetting inputs
st.experimental_singleton.clear()  # no-op pattern to keep Streamlit quiet if using caching elsewhere
st.autorefresh = st.experimental_rerun  # placeholder alias to show we won't call it directly here
# Note: We rely on pull_health() throttling instead of st_autorefresh to avoid chat flicker.

# ------------------------------
# Main
# ------------------------------
st.markdown("""
# AI Network Brain
Intelligent network analysis powered by RAG + lightweight AI model
""")

# Existing transcript
for m in st.session_state.messages:
    with st.chat_message(m.get("role","assistant")):
        st.markdown(m.get("content",""))
        if m.get("role") == "assistant" and m.get("meta"):
            meta = m["meta"]
            with st.expander("🧠 AI Brain Analysis Details"):
                st.write(f"**AI Model Used:** {'Yes (distilgpt2)' if meta.get('ai_model_used') else 'No (rule‑based)'}")
                st.write(f"**RAG Knowledge:** {'Enabled' if meta.get('rag_enabled') else 'Disabled'}")
                st.write(f"**Response Time:** {meta.get('timestamp','Unknown')}")

# Composer
st.markdown("### 💬 Chat with AI Brain")

def send_chat_message_py(message: str) -> Optional[Dict[str, Any]]:
    return _post(f"{st.session_state.api_url}/chat", {"message": message})

# prefill from sidebar chips if any
prefill = st.session_state.pop("__staged_prompt", None)

if prompt := st.chat_input("Ask the AI brain about your network…", key="chat_input", disabled=False):
    # normal input path
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("🧠 AI brain is analyzing your network..."):
            resp = send_chat_message_py(prompt)
            if resp:
                answer = resp.get("response", "Sorry, I couldn't process your request.")
                st.markdown(answer)
                with st.expander("🧠 AI Brain Analysis Details"):
                    st.write(f"**AI Model Used:** {'Yes (distilgpt2)' if resp.get('ai_model_used') else 'No (rule‑based)'}")
                    st.write(f"**RAG Knowledge:** {'Enabled' if resp.get('rag_enabled') else 'Disabled'}")
                    st.write(f"**Response Time:** {resp.get('timestamp','Unknown')}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "meta": {
                        "ai_model_used": resp.get("ai_model_used"),
                        "rag_enabled": resp.get("rag_enabled"),
                        "timestamp": resp.get("timestamp"),
                    },
                })
            else:
                st.error(f"❌ Failed to get response from AI brain at {st.session_state.api_url}.")

elif prefill is not None:
    # staged from chip: just stuff it in the input so the user can edit
    st.session_state.chat_input = prefill
    st.experimental_rerun()

st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**AI Brain:** RAG + distilgpt2")
with col2:
    st.markdown("**Analysis:** Real-time CLI")
with col3:
    st.markdown("**Version:** 7.0.0")
