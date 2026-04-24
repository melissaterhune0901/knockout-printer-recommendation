import streamlit as st
from google import genai
from google.genai import types

# --- PAGE CONFIG ---
st.set_page_config(page_title="Printer Replacement Expert", page_icon="🖨️")
st.title("🖨️ Canon Printer Matcher")
st.markdown("MBA Project: AI-Driven Competitive Replacement Tool")

# --- API SETUP ---
# Securely pulls the key from Streamlit Cloud Secrets
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# --- SYSTEM DATA ---
# This is the "Brain" containing your specific Canon product list
system_instructions = """
You are a Printer Replacement Expert. I will provide you with a list of our company's printers. 
When a user tells you a competitor printer model, compare its specs to our list and recommend the best 1-to-1 replacement. 
Explain why based on Price, PPM (Pages Per Minute), and Functions. 
If you don't know the competitor model, ask for its specs.

OUR PRODUCT LIST:
1. imageCLASS LBP246dx | Category: Home | Vol: 750-4,000 | Lease: $81 | Fast Printing, Wifi
2. ImageRUNNER Advance 4925i | Category: Office | Vol: 10,000-50,000 | Lease: $500 | B&W, 25 ppm
3. Color imageCLASS X LBP1538C II | Category: Home/Small Office | Vol: 5,000-10,000 | Lease: $400 | Color, Compact
"""

# --- CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
# --- THE UPDATED INTERACTION BLOCK ---
if prompt := st.chat_input("Enter a competitor model..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Finding your 1-to-1 match..."):
            try:
                # Force the AI to be a recommender, not a chatter
                forced_prompt = f"Analyze {prompt}. Give a final Canon recommendation immediately. No questions."
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash", 
                    contents=forced_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=instructions,
                        tools=[types.Tool(google_search=types.GoogleSearch())],
                        temperature=0.1,
                    ),
                )
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Connection issue: {e}")

