import streamlit as st
import google.generativeai as genai
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

st.set_page_config(page_title=" Islamic Bot", page_icon="🕌")
st.title("🕌 Islamic Assistant")

model_name = "gemini-2.0-flash"

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat" not in st.session_state:
    st.session_state.chat = None
if "lang" not in st.session_state:
    st.session_state.lang = "English"

with st.sidebar:
    st.header("🌐 Language & Controls")
    selected_lang = st.radio(
        "Language:",
        ["English", "Urdu", "Roman Urdu"],
        index=["English","Urdu","Roman Urdu"].index(st.session_state.lang)
    )
    if st.button("🆕 New Chat"):
        if st.session_state.messages:
            st.session_state.chat_sessions.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "lang": st.session_state.lang,
                "messages": st.session_state.messages.copy()
            })
        st.session_state.messages = []; st.session_state.chat = None

    st.markdown("---")
    st.subheader("🗂️ Previous Chats")
    if st.session_state.chat_sessions:
        for i, sess in enumerate(reversed(st.session_state.chat_sessions)):
            btn = st.button(f"{sess['timestamp']} ({sess['lang']})", key=i)
            if btn:
                st.session_state.messages = sess["messages"]
                st.session_state.lang = sess["lang"]
                st.experimental_rerun()
    else:
        st.write("No previous chats yet.")


def get_instruction(lang):
    if lang=="Urdu":
        return "آپ ایک اسلامی اسسٹنٹ ہیں۔ مختصر اور مستند انداز میں صرف اردو میں جواب دیں۔"
    if lang=="Roman Urdu":
        return "Aap ek Islamic assistant hain. Mukhtasir aur authentic jawab Roman Urdu mein dein, quran ya hadees k reference k sath"
    return "You are an Islamic assistant. Answer briefly with authentic Hadith or Quran refrence in English."

if st.session_state.chat is None or st.session_state.lang != selected_lang:
    inst = get_instruction(selected_lang)
    model = genai.GenerativeModel(model_name=model_name, system_instruction=inst)
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.lang = selected_lang

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask anything about Islam…")
if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role":"user","content":prompt})
    try:
        resp = st.session_state.chat.send_message(prompt)
        reply = resp.text
    except Exception as e:
        reply = f"❌ Error: {e}"
    st.chat_message("assistant").markdown(reply)
    st.session_state.messages.append({"role":"assistant","content":reply})
