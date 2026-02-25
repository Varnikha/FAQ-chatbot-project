# ============================================================
# Advanced FAQ Chatbot - Python + Streamlit
# Features: Fuzzy Matching, Persistent Analytics (CSV)
# ============================================================

import streamlit as st
import string
import pandas as pd
from difflib import get_close_matches
from datetime import datetime
import os

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(page_title="FAQ Chatbot", page_icon="🤖", layout="wide")

# ------------------------------------------------------------
# CSV FILE PATH for persistent analytics
# ------------------------------------------------------------
ANALYTICS_FILE = "analytics.csv"

# ------------------------------------------------------------
# EXPANDED FAQ Knowledge Base (26 Questions)
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

# ------------------------------------------------------------
# Greetings
# ------------------------------------------------------------
greetings = ["hi", "hello", "hey", "hii", "helo", "howdy", "good morning", "good evening", "good afternoon"]

# ------------------------------------------------------------
# Analytics: Load from CSV (persistent across sessions)
# ------------------------------------------------------------
def load_analytics():
    """Load analytics from CSV file if it exists."""
    if os.path.exists(ANALYTICS_FILE):
        return pd.read_csv(ANALYTICS_FILE).to_dict("records")
    return []

def save_analytics(record):
    """Append a new record to the CSV file."""
    df_new = pd.DataFrame([record])
    if os.path.exists(ANALYTICS_FILE):
        # Append to existing file
        df_new.to_csv(ANALYTICS_FILE, mode="a", header=False, index=False)
    else:
        # Create new file with header
        df_new.to_csv(ANALYTICS_FILE, mode="w", header=True, index=False)

def clear_analytics():
    """Delete the CSV file to clear all analytics."""
    if os.path.exists(ANALYTICS_FILE):
        os.remove(ANALYTICS_FILE)

# ------------------------------------------------------------
# Initialize session state
# ------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! 👋 I'm your smart FAQ assistant. How can I help you today?"
    })

# ------------------------------------------------------------
# Helper: Clean Input
# ------------------------------------------------------------
def clean_input(text):
    """Remove punctuation, lowercase, strip spaces."""
    return text.translate(str.maketrans("", "", string.punctuation)).strip().lower()

# ------------------------------------------------------------
# Helper: Fuzzy Match
# ------------------------------------------------------------
def fuzzy_match(normalized_input):
    """Use difflib to find the closest FAQ question."""
    faq_keys = list(faq.keys())
    matches = get_close_matches(normalized_input, faq_keys, n=1, cutoff=0.5)
    if matches:
        return faq[matches[0]], "fuzzy"
    return None, None

# ------------------------------------------------------------
# Main Response Function
# ------------------------------------------------------------
def get_response(user_input):
    """
    1. Check greetings
    2. Exact match
    3. Partial word match
    4. Fuzzy match (difflib)
    5. Fallback message
    """
    normalized_input = clean_input(user_input)

    # Step 1: Greetings
    if normalized_input in greetings:
        return "Hello! 👋 Welcome! How can I help you today?", "greeting"

    # Step 2: Exact match
    if normalized_input in faq:
        return faq[normalized_input], "exact"

    # Step 3: Partial word match (2+ words)
    input_words = normalized_input.split()
    for question, answer in faq.items():
        question_words = question.split()
        if all(word in question_words for word in input_words) and len(input_words) >= 2:
            return answer, "partial"

    # Step 4: Fuzzy match
    answer, match_type = fuzzy_match(normalized_input)
    if answer:
        return answer, "fuzzy"

    # Step 5: Final fallback
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
        "greeting": "👋 Greeting",
        "fallback": "🔴 No Match Found"
    }.get(match_type, "")

# ------------------------------------------------------------
# UI LAYOUT - Two Tabs: Chat | Analytics
# ------------------------------------------------------------
tab1, tab2 = st.tabs(["💬 Chat", "📊 Analytics"])

# ========================
# TAB 1: CHAT
# ========================
with tab1:
    st.title("🤖 Smart FAQ Chatbot")
    st.write("Ask me anything about our services, orders, shipping, and more!")

    # Sample Questions
    with st.expander("💡 Sample Questions (click to expand)"):
        cols = st.columns(2)
        faq_list = list(faq.keys())
        for i, question in enumerate(faq_list):
            cols[i % 2].write(f"• {question.capitalize()}?")

    st.divider()

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if message["role"] == "assistant" and "match_type" in message:
                badge = get_badge(message["match_type"])
                if badge:
                    st.caption(badge)

    # Chat Input
    user_input = st.chat_input("Type your question here...")

    if user_input:
        # Show user message
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Get response
        response, match_type = get_response(user_input)

        # Show bot response
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

        # Save to CSV (persistent analytics)
        record = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "question": user_input,
            "match_type": match_type
        }
        save_analytics(record)

# ========================
# TAB 2: ANALYTICS
# ========================
with tab2:
    st.title("📊 Chatbot Analytics")
    st.caption("✅ Data is saved permanently — even after you close or restart the app.")

    # Load all analytics from CSV
    all_data = load_analytics()

    if not all_data:
        st.info("No data yet. Start chatting to see analytics!")
    else:
        df = pd.DataFrame(all_data)

        total = len(df)
        counts = df["match_type"].value_counts().to_dict()

        # Metric cards
        st.subheader("📈 All-Time Summary")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Questions", total)
        c2.metric("✅ FAQ Answered", counts.get("exact", 0) + counts.get("partial", 0) + counts.get("fuzzy", 0))
        c3.metric("👋 Greetings", counts.get("greeting", 0))
        c4.metric("❌ Not Answered", counts.get("fallback", 0))

        st.divider()

        # Match type bar chart
        st.subheader("🔍 Match Type Breakdown")
        chart_df = df["match_type"].value_counts().reset_index()
        chart_df.columns = ["Match Type", "Count"]
        st.bar_chart(chart_df.set_index("Match Type"))

        st.divider()

        # Filter by date
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

        # Clear analytics button
        if st.button("🗑️ Clear All Analytics"):
            clear_analytics()
            st.success("Analytics cleared!")
            st.rerun()