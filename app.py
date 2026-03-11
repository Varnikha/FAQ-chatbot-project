# ============================================================
# Advanced FAQ Chatbot - Python + Streamlit
# Features: Fuzzy Matching, Groq AI NLP, Persistent Analytics
# Groq Version — Free, Fast, Powerful (Llama 3.3)
# ============================================================

import streamlit as st
import string
import pandas as pd
from difflib import get_close_matches
from datetime import datetime
import os

# Groq import with error handling
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(page_title="FAQ Chatbot", page_icon="🤖", layout="wide")

# ------------------------------------------------------------
# CSV FILE for persistent analytics
# ------------------------------------------------------------
ANALYTICS_FILE = "analytics.csv"

# ------------------------------------------------------------
# FAQ Knowledge Base
# ------------------------------------------------------------
faq = {
    "what are your working hours": "We are open Monday to Friday, 9:00 AM to 6:00 PM.",
    "where are you located": "We are located at 123 Main Street, New York, NY 10001.",
    "what is your contact number": "You can reach us at +1 (800) 123-4567.",
    "what is your email address": "Our email address is support@mycompany.com.",
    "do you offer customer support": "Yes! We offer 24/7 customer support via email and phone.",
    "what services do you offer": "We offer web development, app development, and digital marketing services.",
    "how can i place an order": "You can place an order by visiting our website or calling our sales team.",
    "how do i track my order": "You can track your order by visiting our website and entering your order ID in the 'Track Order' section.",
    "can i cancel my order": "Yes, you can cancel your order within 24 hours of placing it. Contact support for assistance.",
    "how do i modify my order": "To modify your order, contact our support team within 12 hours of placing the order.",
    "do you offer free shipping": "Yes, we offer free shipping on all orders above $50.",
    "how long does delivery take": "Standard delivery takes 3-5 business days. Express delivery takes 1-2 days.",
    "do you ship internationally": "Yes, we ship to over 50 countries. International delivery takes 7-14 business days.",
    "what are the shipping charges": "Shipping is free above $50. Below $50, a flat fee of $5.99 is charged.",
    "what is your return policy": "We have a 30-day hassle-free return policy for all products.",
    "how do i return a product": "To return a product, visit our website, go to 'My Orders', and click 'Return Item'.",
    "when will i get my refund": "Refunds are processed within 5-7 business days after we receive the returned item.",
    "is there a restocking fee": "No, we do not charge any restocking fee for returns.",
    "do you have a physical store": "Yes, we have a physical store at our Main Street location. Walk-ins welcome!",
    "what payment methods do you accept": "We accept credit cards, debit cards, PayPal, and bank transfers.",
    "do you offer discounts": "Yes! We offer seasonal discounts and special deals. Subscribe to our newsletter to stay updated.",
    "do you have a loyalty program": "Yes, our loyalty program gives you points on every purchase which can be redeemed for discounts.",
    "what are your current offers": "Check our website's 'Offers' section for the latest deals and promotions.",
    "do you offer gift cards": "Yes, we offer gift cards in denominations of $25, $50, and $100.",
    "how do i create an account": "Click on 'Sign Up' on our website and fill in your details to create a free account.",
    "how do i reset my password": "Click on 'Forgot Password' on the login page and follow the instructions sent to your email.",
    "is my data safe with you": "Yes, we use industry-standard encryption to protect all your personal data.",
}

# Stop words to ignore during keyword matching
STOP_WORDS = {"what", "is", "are", "the", "a", "an", "do", "does", "how", "can",
              "i", "my", "your", "you", "me", "we", "us", "it", "in", "to", "of",
              "for", "with", "this", "that", "there", "have", "has", "be", "been"}

# ------------------------------------------------------------
# Greetings
# ------------------------------------------------------------
greetings = ["hi", "hello", "hey", "hii", "helo", "howdy", "good morning", "good evening", "good afternoon"]

# ------------------------------------------------------------
# Analytics Functions
# ------------------------------------------------------------
def load_analytics():
    if os.path.exists(ANALYTICS_FILE):
        try:
            return pd.read_csv(ANALYTICS_FILE).to_dict("records")
        except Exception:
            return []
    return []

def save_analytics(record):
    try:
        df_new = pd.DataFrame([record])
        if os.path.exists(ANALYTICS_FILE):
            df_new.to_csv(ANALYTICS_FILE, mode="a", header=False, index=False)
        else:
            df_new.to_csv(ANALYTICS_FILE, mode="w", header=True, index=False)
    except Exception as e:
        st.warning(f"Could not save analytics: {e}")

def clear_analytics():
    if os.path.exists(ANALYTICS_FILE):
        os.remove(ANALYTICS_FILE)

# ------------------------------------------------------------
# Helper: Clean Input
# ------------------------------------------------------------
def clean_input(text):
    return text.translate(str.maketrans("", "", string.punctuation)).strip().lower()

# ------------------------------------------------------------
# Helper: Extract meaningful keywords
# ------------------------------------------------------------
def get_keywords(text):
    words = text.split()
    return [w for w in words if w not in STOP_WORDS and len(w) > 2]

# ------------------------------------------------------------
# Helper: Fuzzy Match
# ------------------------------------------------------------
def fuzzy_match(normalized_input):
    faq_keys = list(faq.keys())
    matches = get_close_matches(normalized_input, faq_keys, n=1, cutoff=0.55)
    if matches:
        return faq[matches[0]], "fuzzy"
    return None, None

# ------------------------------------------------------------
# Helper: Groq AI Response
# Using llama-3.3-70b-versatile — latest active free model
# ------------------------------------------------------------
def groq_response(user_input, api_key):
    if not GROQ_AVAILABLE:
        return None, None
    try:
        client = Groq(api_key=api_key)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful FAQ assistant for a company that offers web development, "
                        "app development, and digital marketing services. "
                        "Answer customer questions clearly and concisely in 2-3 sentences. "
                        "Be professional and friendly."
                    )
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            model="llama-3.3-70b-versatile",  # ✅ Latest active Groq model
            max_tokens=200,
            temperature=0.7,
        )
        answer = chat_completion.choices[0].message.content.strip()
        if answer:
            return answer, "groq"
        return None, None
    except Exception as e:
        st.error(f"Groq Error: {e}")
        return None, None

# ------------------------------------------------------------
# Main Response Function
# ------------------------------------------------------------
def get_response(user_input):
    normalized_input = clean_input(user_input)

    # Guard: empty input
    if not normalized_input:
        return "Please type a question so I can help you! 😊", "fallback"

    # Step 1: Greetings
    if normalized_input in greetings:
        return "Hello! 👋 Welcome! How can I help you today?", "greeting"

    # Step 2: Exact match
    if normalized_input in faq:
        return faq[normalized_input], "exact"

    # Step 3: Strict keyword-based partial match (Jaccard similarity)
    input_keywords = set(get_keywords(normalized_input))
    if input_keywords:
        best_score = 0
        best_answer = None
        for question, answer in faq.items():
            question_keywords = set(get_keywords(question))
            if not question_keywords:
                continue
            intersection = input_keywords & question_keywords
            union = input_keywords | question_keywords
            score = len(intersection) / len(union)
            if score > best_score:
                best_score = score
                best_answer = answer
        if best_score >= 0.4 and best_answer:
            return best_answer, "partial"

    # Step 4: Fuzzy match
    answer, match_type = fuzzy_match(normalized_input)
    if answer:
        return answer, "fuzzy"

    # Step 5: Groq AI fallback
    if st.session_state.get("groq_key"):
        answer, match_type = groq_response(user_input, st.session_state.groq_key)
        if answer:
            return answer, "groq"

    # Step 6: Final fallback
    return (
        "Sorry, I don't have an answer for that. "
        "Please contact us at support@mycompany.com or call +1 (800) 123-4567."
    ), "fallback"

# ------------------------------------------------------------
# Badge helper
# ------------------------------------------------------------
def get_badge(match_type):
    return {
        "exact":    "🟢 Exact Match",
        "partial":  "🔵 Partial Match",
        "fuzzy":    "🟡 Fuzzy Match",
        "groq":     "⚡ Groq AI Answer (Llama 3.3)",
        "greeting": "👋 Greeting",
        "fallback": "🔴 No Match Found"
    }.get(match_type, "")

# ------------------------------------------------------------
# Initialize session state
# ------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! 👋 I'm your smart FAQ assistant powered by Groq AI. How can I help you today?"
        }
    ]

if "groq_key" not in st.session_state:
    st.session_state.groq_key = ""

# ------------------------------------------------------------
# UI LAYOUT
# ------------------------------------------------------------
tab1, tab2 = st.tabs(["💬 Chat", "📊 Analytics"])

# ========================
# TAB 1: CHAT
# ========================
with tab1:
    st.title("🤖 Smart FAQ Chatbot")
    st.write("Ask me anything! I use Groq AI (free & fast) to answer even questions not in the FAQ.")

    with st.expander("⚙️ Add Groq API Key (Free — for AI-powered answers)"):
        if not GROQ_AVAILABLE:
            st.warning("⚠️ Groq not installed. Run: `python -m pip install groq`")
        else:
            st.info("🆓 Groq is completely FREE! Get your key at: https://console.groq.com")
            key_input = st.text_input(
                "Paste your Groq API Key here:",
                type="password",
                placeholder="gsk_..."
            )
            if key_input:
                st.session_state.groq_key = key_input
                st.success("✅ Groq API Key saved! Llama 3.3 AI will now answer unknown questions.")
            st.caption("Get your free key at: https://console.groq.com/keys")

    with st.expander("💡 Sample Questions (click to expand)"):
        cols = st.columns(2)
        for i, question in enumerate(faq.keys()):
            cols[i % 2].write(f"• {question.capitalize()}?")

    st.divider()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if message["role"] == "assistant" and "match_type" in message:
                badge = get_badge(message["match_type"])
                if badge:
                    st.caption(badge)

    user_input = st.chat_input("Type your question here...")

    if user_input:
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.spinner("Thinking..."):
            response, match_type = get_response(user_input)

        with st.chat_message("assistant"):
            st.write(response)
            badge = get_badge(match_type)
            if badge:
                st.caption(badge)

        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "match_type": match_type
        })

        save_analytics({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "question": user_input,
            "match_type": match_type
        })

# ========================
# TAB 2: ANALYTICS
# ========================
with tab2:
    st.title("📊 Chatbot Analytics")
    st.caption("✅ Data is saved permanently — even after you close or restart the app.")

    all_data = load_analytics()

    if not all_data:
        st.info("No data yet. Start chatting to see analytics!")
    else:
        df = pd.DataFrame(all_data)
        total = len(df)
        counts = df["match_type"].value_counts().to_dict()

        st.subheader("📈 All-Time Summary")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Questions", total)
        c2.metric("🟢 FAQ Answered", counts.get("exact", 0) + counts.get("partial", 0) + counts.get("fuzzy", 0))
        c3.metric("⚡ Groq AI", counts.get("groq", 0))
        c4.metric("👋 Greetings", counts.get("greeting", 0))
        c5.metric("❌ Not Answered", counts.get("fallback", 0))

        st.divider()

        st.subheader("🔍 Match Type Breakdown")
        chart_df = df["match_type"].value_counts().reset_index()
        chart_df.columns = ["Match Type", "Count"]
        st.bar_chart(chart_df.set_index("Match Type"))

        st.divider()

        st.subheader("📋 Question Log")
        if "date" in df.columns:
            dates = ["All"] + sorted(df["date"].unique().tolist(), reverse=True)
            selected_date = st.selectbox("Filter by Date:", dates)
            if selected_date != "All":
                df = df[df["date"] == selected_date]

        st.dataframe(df.rename(columns={
            "date": "Date",
            "time": "Time",
            "question": "Question Asked",
            "match_type": "Match Type"
        }), use_container_width=True)

        st.divider()

        if st.button("🗑️ Clear All Analytics"):
            clear_analytics()
            st.success("Analytics cleared!")
            st.rerun()