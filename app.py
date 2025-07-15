import streamlit as st
import requests
import json
import time
import html
import re
from datetime import datetime
from typing import Dict, List
from streamlit.components.v1 import html as st_html
import markdown

# Page configuration
st.set_page_config(
    page_title="AI Multi-Agent Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def clean_llm_output(text):
    """Removes markdown/code ticks and HTML tags from LLM output."""
    if not text:
        return ""
    # Remove triple backticks and `json` word
    text = re.sub(r"```(json)?", "", text)
    text = re.sub(r"</?div.*?>", "", text)  # Remove div tags, can be expanded
    text = re.sub(r"</?strong.*?>", "", text)
    text = text.strip('`').strip()
    # Optionally: remove any remaining HTML tags
    text = re.sub(r'<.*?>', '', text)
    return text.strip()

# Custom CSS for futuristic styling
st.markdown(""" 
        <style>
        .stApp {
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            background-attachment: fixed;
        }

        /* Animations */
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes slideInLeft {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        
        /* Button styling */
        
        .stButton > button,
        .stFormSubmitButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 25px !important;
            padding: 10px 30px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        }

        .stButton > button:hover,
        .stFormSubmitButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
        }
        
        
        
        /* Sidebar styling */
        .css-1d391kg {
            background: rgba(0, 0, 0, 0.3) !important;
            backdrop-filter: blur(10px);
        }
        
        /* Timestamp styling */
        .timestamp {
            font-size: 11px;
            color: rgba(255, 255, 255, 0.5);
            margin-top: 5px;
        }
        
        /* Loading animation */
        .loading-dots {
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }
        
        .loading-dots span {
            width: 8px;
            height: 8px;
            background: rgba(255, 255, 255, 0.6);
            border-radius: 50%;
            animation: bounce 1.4s ease-in-out infinite;
        }
        
        .loading-dots span:nth-child(2) {
            animation-delay: 0.2s;
        }
        
        .loading-dots span:nth-child(3) {
            animation-delay: 0.4s;
        }
        
        @keyframes bounce {
            0%, 80%, 100% {
                transform: scale(0.8);
                opacity: 0.5;
            }
            40% {
                transform: scale(1.2);
                opacity: 1;
            }
        }

        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        /* Header styling */
        h1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            font-size: 3em;
            font-weight: 700;
            margin-bottom: 30px;
            text-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
        }
        
        /* Select box styling */
        .stSelectbox > div > div {
            background: rgba(255, 255, 255, 0.1) !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            border-radius: 10px !important;
            color: white !important;
        }
        
        
        /* Remove red border and outline on input focus or error */
        div[data-baseweb="input"] > div:focus-within {
            outline: none !important;
            box-shadow: none !important;
            border: 1.5px solid #7051bc !important; /* Use your purple border */
        }

        /* Remove "error" state border (red) */
        div[data-baseweb="input"] > div[aria-invalid="true"] {
            border: 1.5px solid #7051bc !important; /* Again, purple border */
            box-shadow: none !important;
            outline: none !important;
        }

        /* Remove red border on actual input element focus */
        input[data-testid="stTextInput"]:focus {
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
        }

        /* Glassy blur and theme color */
        div[data-baseweb="input"] > div {
            background: rgba(48, 18, 90, 0.6) !important;
            backdrop-filter: blur(8px) !important;
            border-radius: 12px !important;
            color: #fff !important;
            border: 1.5px solid #7051bc !important;
            transition: border 0.3s;
        }
        input[data-testid="stTextInput"] {
            color: #fff !important;
        }
        input[data-testid="stTextInput"]::placeholder {
            color: #c3aaff !important;
            opacity: 1;
        }
        /* Hide the 'Press Enter to submit form' tooltip message */
        div[role="tooltip"] {
            display: none !important;
        }

        /* Reduce gap between chat and input */
        .chat-container {
            # margin-bottom: 20px !important;
        }

        .st-emotion-cache-gsx7k2{
        height: 500px    
        }
        .st-emotion-cache-hjhvlk{
            height: 80px
        }

        # .st-emotion-cache-v3w3zg {
        # height: 10px


        
        </style>
        """, unsafe_allow_html=True)


custom_css = """
<style>
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        background-attachment: fixed;
    }
    
    /* Chat container */
    .chat-container {
        background: rgba(255,255,255,0.04);
        border-radius: 20px;
        padding: 20px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 80px;
        
        height: calc(100vh - 180px); /* adjust as needed for your header/footer/input */
        min-height: 300px;
        max-height: none;
        overflow-y: auto;
    }
    
    /* Message bubbles */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        margin: 10px 0;
        max-width: 70%;
        float: right;
        clear: both;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        animation: slideInRight 0.3s ease-out;
    }
    
    /* AI Message bubbles */
    .ai-message {
        
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 4px;
        margin: 10px 0;
        max-width: 70%;
        float: left;
        clear: both;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        animation: slideInLeft 0.3s ease-out;
        
    }
    
    /* Animations */
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    
    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(0, 0, 0, 0.3) !important;
        backdrop-filter: blur(10px);
    }
    
    /* Avatar styling */
    .avatar {
        width: 35px;
        height: 35px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 10px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }
    
    .user-avatar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .ai-avatar {
        background: linear-gradient(135deg, #00c9ff 0%, #92fe9d 100%);
    }
    
    /* Timestamp styling */
    .timestamp {
        font-size: 11px;
        color: rgba(255, 255, 255, 0.5);
        margin-top: 5px;
    }
    
    /* Loading animation */
    .loading-dots {
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }
    
    .loading-dots span {
        width: 8px;
        height: 8px;
        background: rgba(255, 255, 255, 0.6);
        border-radius: 50%;
        animation: bounce 1.4s ease-in-out infinite;
    }
    
    .loading-dots span:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .loading-dots span:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes bounce {
        0%, 80%, 100% {
            transform: scale(0.8);
            opacity: 0.5;
        }
        40% {
            transform: scale(1.2);
            opacity: 1;
        }
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.3);
    }
    
    /* Header styling */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 3em;
        font-weight: 700;
        margin-bottom: 30px;
        text-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
    }
    
    /* Select box styling */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 10px !important;
        color: white !important;
    }
</style>"""

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_agent' not in st.session_state:
    st.session_state.current_agent = "Tech"
if 'chat_session' not in st.session_state:
    st.session_state.chat_session = None

# API configuration
API_URL = "https://purshare-dev-env-402934621063.europe-west9.run.app/api/chat/chat-thread/"

def stream_chat_api(query: str, agent: str):
    """Stream response from the API using SSE"""
    url = "https://purshare-dev-env-402934621063.europe-west9.run.app/api/chat/chat-thread/"
    payload = {"query": query, "agent": agent, "session_id": st.session_state.chat_session}
    
    try:
        with requests.post(url, json=payload, stream=True, timeout=120) as response:
            if response.status_code != 200:
                yield f"\n[Error: API HTTP {response.status_code} - {response.text}]\n"
                return
                
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith("data:"):
                        data = line[len("data:"):].strip()
                        if data:
                            try:
                                parsed = json.loads(data)
                                if parsed.get("type") == "chunk":
                                    yield parsed["content"]
                            except Exception as e:
                                yield f"\n[Error: Failed to parse: {data} ({e})]\n"
                        else:
                            yield "[Error: Empty SSE data]\n"
    except Exception as e:
        yield f"\n[Error: {str(e)}]\n"



def render_message_html(message: Dict) -> str:
    """Return HTML for a single message with avatar and styling"""
    if message["role"] == "user":
        content = html.escape(message['content']) if message['content'] else ''
        return f"""
       <div style="clear: both; margin: 20px 0;">
            <div style="float: right; display: flex; align-items: start; max-width: 70%;">
                <div style="margin-right: 10px;">
                    <div class="user-message">
                        {content}
                        <div class="timestamp">{message['timestamp']} - You</div>
                    </div>
                </div>
                <div class="avatar user-avatar" style="margin-top: 5px;">
                    <span style="display: flex; align-items: center; justify-content: center; height: 100%; font-size: 18px;">👤</span>
                </div>
            </div>
        </div>
        """
    else:
        if message.get('streaming', False) and not message['content']:
            display_content = '<div class="loading-dots"><span></span><span></span><span></span></div>'
        else:
            # Convert markdown to HTML before inserting into chat bubble!
            display_content = markdown.markdown(message['content'] or "")
        return f"""
        <div style="clear: both; margin: 20px 0;">
            <div style="float: left; display: flex; align-items: start; max-width: 70%;">
                <div class="avatar ai-avatar" style="margin-top: 5px;">
                    <span style="display: flex; align-items: center; justify-content: center; height: 100%; font-size: 18px;">🤖</span>
                </div>
                <div style="margin-left: 10px;">
                    <div class="ai-message">
                        {display_content}
                        <div class="timestamp">{message['timestamp']} - {message['agent']} Agent</div>
                    </div>
                </div>
            </div>
        </div>
        """


# Sidebar
with st.sidebar:
    st.markdown("### 🤖 AI Agent Selection")
    st.markdown("---")
    
    # Agent selector
    agent = st.selectbox(
        "Choose an Agent:",
        options=["Tech", "Sport", "GK"],
        index=["Tech", "Sport", "GK"].index(st.session_state.current_agent),
        key="agent_selector"
    )
    
    
    if agent != st.session_state.current_agent:
        st.session_state.current_agent = agent
        
    
    chat_session_id = st.text_input(
        label="session",
        placeholder="Chat Session ID"
    )
    if chat_session_id:
        st.session_state.chat_session = chat_session_id
    
    st.markdown("---")
    st.markdown("### 📊 Chat Statistics")
    st.metric("Total Messages", len(st.session_state.messages))
    st.metric("Current Agent", st.session_state.current_agent)
    
    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main chat interface heading
st.markdown("<h1>🚀 AI Multi-Agent Chat</h1>", unsafe_allow_html=True)


chat_container = st.container()
with chat_container:
    # Collect all message HTMLs
    chat_html = custom_css + '<div class="chat-container">'
    for message in st.session_state.messages:
        chat_html += render_message_html(message)
    chat_html += '</div>'
    # st.components.v1.html(chat_html, height=800, scrolling=True)
    st.components.v1.html(chat_html, height=650, scrolling=True)


st.markdown("""
<style>

</style>
""", unsafe_allow_html=True)


# Fixed input area at bottom
st.markdown('<div class="fixed-input-container">', unsafe_allow_html=True)
with st.form(key="message_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            "Type your message...",
            key="user_input",
            label_visibility="collapsed"
        )
    with col2:
        send_button = st.form_submit_button(
            "🚀",
            use_container_width=True
        )

st.markdown('</div>', unsafe_allow_html=True)



# --- Stage 1: On submit, add user and assistant (thinking...) message, rerun
if send_button and user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().strftime("%H:%M"),
        "agent": st.session_state.current_agent
    })
    st.session_state.messages.append({
        "role": "assistant",
        "content": "",
        "timestamp": datetime.now().strftime("%H:%M"),
        "agent": st.session_state.current_agent,
        "streaming": True
    })
    st.session_state.pending_stream = True
    st.rerun()

# --- Stage 2: If pending_stream, do streaming and update last assistant message
if st.session_state.get("pending_stream"):
    user_msg = None
    for msg in reversed(st.session_state.messages):
        if msg["role"] == "user":
            user_msg = msg
            break
    if user_msg is not None:
        full_response = ""
        for chunk in stream_chat_api(user_msg["content"], st.session_state.current_agent):
            full_response += chunk
        st.session_state.messages[-1]["content"] = full_response
        st.session_state.messages[-1]["streaming"] = False
    st.session_state.pending_stream = False
    st.rerun()


# Auto-scroll JavaScript
st.markdown("""
<script>
    // Auto-scroll to bottom of chat
    var chatContainer = document.querySelector('.chat-container');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
</script>
""", unsafe_allow_html=True)