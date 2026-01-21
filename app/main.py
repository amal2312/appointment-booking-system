import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from models.llm import get_chatgroq_model
from db.database import init_db, save_booking, get_all_bookings
from utils.email_utils import send_confirmation_email
from app.booking_flow import handle_booking_flow, reset_booking
from app.chat_logic import handle_user_message
from app.rag_pipeline import build_vectorstore
from app.admin_dashboard import admin_dashboard_page
import PyPDF2
import time

# ========== AMAZING CUSTOM STYLING ==========
def inject_custom_css():
    """Inject beautiful, modern CSS with animations and glassmorphism"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* ROOT COLORS - Modern Gradient Palette */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --success-gradient: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        --warning-gradient: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    }
    
    /* MAIN BACKGROUND */
    .stApp {
        background: linear-gradient(135deg, #0f0e1e 0%, #1a1a3e 50%, #0f0e1e 100%);
        min-height: 100vh;
    }
    
    /* PAGE BACKGROUND */
    [data-testid="stAppViewContainer"] {
        background: transparent;
    }
    
    /* HEADER STYLING */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
        animation: fadeInDown 0.8s ease-out;
    }
    
    h2 {
        color: #e0e7ff;
        font-weight: 700;
        margin-top: 2rem;
    }
    
    h3 {
        color: #c7d2fe;
        font-weight: 600;
    }
    
    /* GLASS MORPHISM EFFECT */
    .glass-effect {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
    }
    
    /* CHAT MESSAGES */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.02) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
        animation: slideInUp 0.4s ease-out;
    }
    
    .stChatMessage [data-testid="chatMessageContent"] {
        color: #e0e7ff;
        font-size: 1rem;
    }
    
    /* USER MESSAGE */
    .stChatMessage[data-testid*="user"] {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.15)) !important;
        border-color: rgba(102, 126, 234, 0.3) !important;
    }
    
    /* ASSISTANT MESSAGE */
    .stChatMessage[data-testid*="assistant"] {
        background: linear-gradient(135deg, rgba(240, 147, 251, 0.1), rgba(245, 87, 108, 0.1)) !important;
        border-color: rgba(240, 147, 251, 0.2) !important;
    }
    
    /* CHAT INPUT */
    .stChatInputContainer {
        border-top: 1px solid rgba(255, 255, 255, 0.1) !important;
        margin-top: 2rem !important;
        padding-top: 1.5rem !important;
    }
    
    .stChatInputContainer input {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: #e0e7ff !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
        padding: 12px 16px !important;
        transition: all 0.3s ease;
    }
    
    .stChatInputContainer input:focus {
        background: rgba(255, 255, 255, 0.12) !important;
        border-color: rgba(102, 126, 234, 0.6) !important;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* BUTTONS */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3) !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.85rem !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 32px rgba(102, 126, 234, 0.5) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) !important;
    }
    
    /* SIDEBAR */
    .stSidebar {
        background: linear-gradient(180deg, rgba(15, 14, 30, 0.9), rgba(26, 26, 62, 0.9)) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    .stSidebar [data-testid="stSidebarContent"] {
        background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23667eea' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    }
    
    .stSidebar .stRadio > label {
        color: #e0e7ff !important;
        padding: 12px 16px !important;
        border-radius: 10px !important;
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        transition: all 0.3s ease;
        margin-bottom: 0.5rem !important;
    }
    
    .stSidebar .stRadio > label:hover {
        background: rgba(102, 126, 234, 0.15) !important;
        border-color: rgba(102, 126, 234, 0.4) !important;
    }
    
    /* INFO/SUCCESS/ERROR BOXES */
    .stAlert {
        border-radius: 12px !important;
        border-left: 4px solid !important;
        background: rgba(255, 255, 255, 0.03) !important;
        padding: 1.2rem !important;
        backdrop-filter: blur(5px);
    }
    
    .stSuccess {
        border-left-color: #38ef7d !important;
        background: linear-gradient(135deg, rgba(17, 153, 142, 0.1), rgba(56, 239, 125, 0.1)) !important;
    }
    
    .stInfo {
        border-left-color: #667eea !important;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)) !important;
    }
    
    .stWarning {
        border-left-color: #fee140 !important;
        background: linear-gradient(135deg, rgba(250, 112, 154, 0.1), rgba(254, 225, 64, 0.1)) !important;
    }
    
    .stError {
        border-left-color: #f5576c !important;
        background: linear-gradient(135deg, rgba(245, 87, 108, 0.1), rgba(250, 112, 154, 0.1)) !important;
    }
    
    .stAlert > div {
        color: #e0e7ff !important;
    }
    
    /* SPINNERS & PROGRESS */
    .stSpinner > div {
        border-color: rgba(102, 126, 234, 0.3) !important;
        border-right-color: #667eea !important;
    }
    
    /* TEXT CONTENT */
    p, span, div {
        color: #c7d2fe;
    }
    
    /* SEPARATOR */
    hr {
        border-color: rgba(255, 255, 255, 0.08) !important;
    }
    
    /* DATA TABLE */
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden;
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* ANIMATIONS */
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes glow {
        0%, 100% { text-shadow: 0 0 20px rgba(102, 126, 234, 0.5); }
        50% { text-shadow: 0 0 30px rgba(102, 126, 234, 0.8); }
    }
    
    /* METRIC CARDS */
    .stMetric {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)) !important;
        border: 1px solid rgba(102, 126, 234, 0.3) !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
    }
    
    .stMetric > div {
        color: #e0e7ff !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ========== BOOKING INTENT DETECTION ==========
def is_booking_intent(text: str) -> bool:
    keywords = ["book", "booking", "appointment", "doctor", "schedule", "visit"]
    return any(word in text.lower() for word in keywords)


# ========== LLM CHAT RESPONSE ==========
def get_chat_response(chat_model, messages, system_prompt):
    formatted = [SystemMessage(content=system_prompt)]
    for m in messages:
        if m["role"] == "user":
            formatted.append(HumanMessage(content=m["content"]))
        else:
            formatted.append(AIMessage(content=m["content"]))
    return chat_model.invoke(formatted).content


# ========== MAIN CHAT PAGE WITH STUNNING UI ==========
def chat_page():
    # Page layout
    st.markdown("""<div style='text-align: center; margin-bottom: 2rem;'><h1 style='font-size: 2.5rem;'>🩺 MediBot: AI Appointment Assistant</h1></div>""", unsafe_allow_html=True)
    
    chat_model = get_chatgroq_model()
    system_prompt = "You are a professional, friendly medical appointment assistant. Help users book appointments, answer questions about healthcare, and provide guidance. Be empathetic and clear."

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "booking_mode" not in st.session_state:
        st.session_state.booking_mode = False
    if "awaiting_confirmation" not in st.session_state:
        st.session_state.awaiting_confirmation = False
    if "booking_data" not in st.session_state:
        st.session_state.booking_data = reset_booking()

    # Display welcome message if no messages
    if not st.session_state.messages:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.markdown("""
            <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)); 
            border: 1px solid rgba(102, 126, 234, 0.3); border-radius: 16px; backdrop-filter: blur(10px);'>
                <h3 style='color: #e0e7ff; margin-top: 0;'>👋 Welcome!</h3>
                <p style='color: #c7d2fe;'>Start a conversation or ask me to book an appointment</p>
            </div>
            """, unsafe_allow_html=True)

    # Chat messages container
    chat_container = st.container()
    
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🤖"):
                st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("💬 Type your message here...", key=f"input_{len(st.session_state.messages)}"):
        
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Generate response
        assistant_response = ""

        # Booking confirmation flow
        if st.session_state.awaiting_confirmation:
            if prompt.lower() == "yes":
                booking_id = save_booking(st.session_state.booking_data)
                
                try:
                    send_confirmation_email(
                        st.session_state.booking_data["email"],
                        booking_id,
                        st.session_state.booking_data
                    )
                    email_status = "✅ Confirmation email sent!"
                except Exception as e:
                    email_status = "⚠️ Email couldn't be sent, but booking is confirmed!"

                booking_info = f"""
**🎉 APPOINTMENT CONFIRMED!**

**Booking Details:**
• 📌 ID: `{booking_id}`
• 👤 Name: {st.session_state.booking_data.get('name', 'N/A')}
• 📅 Date: {st.session_state.booking_data.get('date', 'N/A')}
• ⏰ Time: {st.session_state.booking_data.get('time', 'N/A')}
• 📧 Email: {st.session_state.booking_data.get('email', 'N/A')}
• 📞 Phone: {st.session_state.booking_data.get('phone', 'N/A')}

{email_status}

Is there anything else I can help you with?
                """
                assistant_response = booking_info
                
                st.session_state.booking_mode = False
                st.session_state.awaiting_confirmation = False
                st.session_state.booking_data = reset_booking()
                
            elif prompt.lower() == "no":
                assistant_response = "❌ Booking cancelled. No problem! Feel free to book again whenever you're ready."
                st.session_state.booking_mode = False
                st.session_state.awaiting_confirmation = False
                st.session_state.booking_data = reset_booking()
            else:
                assistant_response = "Please type **yes** to confirm or **no** to cancel your booking."

        # Booking flow
        elif st.session_state.booking_mode:
            assistant_response = handle_booking_flow(prompt, st.session_state.booking_data)
            if "Type **yes** to confirm" in assistant_response:
                st.session_state.awaiting_confirmation = True

        # Normal chat with RAG
        else:
            tool_reply = handle_user_message(prompt)
            
            if tool_reply:
                assistant_response = tool_reply
            elif is_booking_intent(prompt):
                st.session_state.booking_mode = True
                assistant_response = "📝 Great! Let's book your appointment. **What's your full name?**"
            else:
                assistant_response = get_chat_response(chat_model, st.session_state.messages, system_prompt)

        # Display assistant response
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(assistant_response)

        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        
        # Auto-scroll
        time.sleep(0.5)
        st.rerun()


# ========== SIDEBAR & PDF UPLOAD ==========
with st.sidebar:
    st.markdown("<h2 style='font-size: 1.3rem; color: #e0e7ff;'>📚 Knowledge Base</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #c7d2fe;'>Upload PDFs to enhance responses</p>", unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Select PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        key="sidebar_pdf_upload"
    )

    if uploaded_files:
        progress_bar = st.progress(0)
        texts = []
        
        for idx, file in enumerate(uploaded_files):
            try:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    if page.extract_text():
                        texts.append(page.extract_text())
                progress_bar.progress((idx + 1) / len(uploaded_files))
            except Exception as e:
                st.error(f"Error reading {file.name}")

        if texts:
            with st.spinner("🔄 Processing documents..."):
                build_vectorstore(texts)
            st.success(f"✅ Indexed {len(uploaded_files)} document(s)!")
    
    st.markdown("---")


# ========== MAIN APPLICATION ==========
def main():
    init_db()

    st.set_page_config(
        page_title="Doctor Appointment Assistant",
        page_icon="🩺",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply stunning CSS
    inject_custom_css()

    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h2 style='font-size: 1.2rem; color: #667eea;'>🏥 MediBot</h2>
            <p style='font-size: 0.85rem; color: #c7d2fe;'>AI Appointment Assistant</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        page = st.radio(
            "Select Page",
            ["💬 Chat", "📊 Admin Panel"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat", width='stretch'):
                st.session_state.clear()
                st.rerun()
        
        with col2:
            if st.button("🔄 Refresh", width='stretch'):
                st.rerun()
        
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #8892b0; font-size: 0.8rem; margin-top: 3rem;'>
            <p>Powered by AI & LangChain</p>
            <p>v1.0 • Always Learning</p>
        </div>
        """, unsafe_allow_html=True)

    if "Chat" in page:
        chat_page()
    else:
        admin_dashboard_page()


if __name__ == "__main__":
    main()
