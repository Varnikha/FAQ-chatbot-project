# ============================================================
# FAQ Chatbot - Simple Python + Streamlit Application
# ============================================================

import streamlit as st
import string

# ------------------------------------------------------------
# FAQ Data: Dictionary storing questions and their answers
# ------------------------------------------------------------
faq = {
    "what are your working hours": "We are open Monday to Friday, 9:00 AM to 6:00 PM.",
    "where are you located": "We are located at 123 Main Street, New York, NY 10001.",
    "what is your contact number": "You can reach us at +1 (800) 123-4567.",
    "what is your email address": "Our email address is support@mycompany.com.",
    "do you offer customer support": "Yes! We offer 24/7 customer support via email and phone.",
    "what services do you offer": "We offer web development, app development, and digital marketing services.",
    "how can i place an order": "You can place an order by visiting our website or calling our sales team.",
    "what is your return policy": "We have a 30-day hassle-free return policy for all products.",
    "do you offer free shipping": "Yes, we offer free shipping on all orders above $50.",
    "how long does delivery take": "Standard delivery takes 3-5 business days. Express delivery takes 1-2 days.",
    "do you have a physical store": "Yes, we have a physical store at our Main Street location. Walk-ins welcome!",
    "what payment methods do you accept": "We accept credit cards, debit cards, PayPal, and bank transfers.",
}

# ------------------------------------------------------------
# List of greetings the chatbot should recognize
# ------------------------------------------------------------
greetings = ["hi", "hello", "hey", "hii", "helo", "howdy", "good morning", "good evening", "good afternoon"]

# ------------------------------------------------------------
# Function to clean user input (remove punctuation)
# ------------------------------------------------------------
def clean_input(text):
    # Remove punctuation like ? ! . , from the input
    return text.translate(str.maketrans("", "", string.punctuation)).strip().lower()

# ------------------------------------------------------------
# Function to get chatbot response
# ------------------------------------------------------------
def get_response(user_input):
    """
    Takes user input, cleans it (removes punctuation, lowercases),
    checks against FAQ dictionary, and returns appropriate response.
    """
    # Clean and normalize input
    normalized_input = clean_input(user_input)

    # Handle greetings separately
    if normalized_input in greetings:
        return "Hello! 👋 Welcome! How can I help you today? Feel free to ask me anything."

    # Exact match check
    if normalized_input in faq:
        return faq[normalized_input]

    # Partial match: check if ALL words in user input appear in a FAQ key
    input_words = normalized_input.split()
    for question, answer in faq.items():
        question_words = question.split()
        # Only match if input words are actual words in the question (not substrings)
        if all(word in question_words for word in input_words) and len(input_words) >= 2:
            return answer

    # Fallback message if no match is found
    return (
        "Sorry, I don't have an answer for that. "
        "Please contact us at support@mycompany.com or call +1 (800) 123-4567."
    )

# ------------------------------------------------------------
# Streamlit UI Setup
# ------------------------------------------------------------
st.set_page_config(page_title="FAQ Chatbot", page_icon="🤖")

st.title("🤖 FAQ Chatbot")
st.write("Ask me anything! Here are some things you can ask:")

# Display sample questions as hints
with st.expander("💡 Sample Questions (click to expand)"):
    for question in faq.keys():
        st.write(f"• {question.capitalize()}?")

st.divider()

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add a welcome message from the bot
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! I'm your FAQ assistant. How can I help you today?"
    })

# Display all chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input box at the bottom
user_input = st.chat_input("Type your question here...")

if user_input:
    # Show user message in chat
    with st.chat_message("user"):
        st.write(user_input)

    # Save user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Get bot response
    response = get_response(user_input)

    # Show bot response in chat
    with st.chat_message("assistant"):
        st.write(response)

    # Save bot response to history
    st.session_state.messages.append({"role": "assistant", "content": response})