import streamlit as st
from google import genai
from google.genai import types

# --- 1. GLOBAL DATA & INSTRUCTIONS ---
# I've tightened these instructions to prioritize the MATCHING.
instructions = """
You are the Canon Product Matcher. Your primary goal is to find a 1-to-1 replacement for competitor printers.

OUR PRODUCT LIST:
1. imageCLASS LBP246dx | Category: Home | Vol: 750-4,000 | Lease: $81 | Fast Printing, Wifi
2. ImageRUNNER Advance 4925i | Category: Office | Vol: 10,000-50,000 | Lease: $500 | B&W, 25 ppm
3. Color imageCLASS X LBP1538C II | Category: Home/Small Office | Vol: 5,000-10,000 | Lease: $400 | Color, Compact

STRICT OUTPUT RULES:
1. When provided a competitor model, start your response with: "THE WINNING MATCH: [Our Model Name]"
2. Briefly explain WHY it matches (Volume, Category, or Price).
3. Do NOT provide a sales pitch unless the user clicks a sales button.
"""

# --- 2. APP UI SETUP ---
st.set_page_config(page_title="Canon Knockout", page_icon="🖨️")
st.title("🖨️ Canon Competitor Knockout")

# --- 3. THE CONNECTION ---
# Using the stable 2026 2.5-flash model
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
MODEL_ID = "gemini-2.5-flash" 

if "last_comparison" not in st.session_state:
    st.session_state.last_comparison = ""

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("💰 Sales Toolkit")
    pitch_btn = st.button("Draft Sales Pitch")
    prop_btn = st.button("Generate Formal Proposal")
    deck_btn = st.button("Outline Slide Deck")
    quote_btn = st.button("Create Quote Table")

# --- 5. CHAT ---
if prompt := st.chat_input("Ex: HP LaserJet Pro M404n"):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing competitor specs..."):
            try:
                # Force the prompt to focus on our product list
                final_prompt = f"Identify the competitor printer: {prompt}. Match it to exactly one printer from our list. Explain why."
                
                response = client.models.generate_content(
                    model=MODEL_ID,
                    contents=final_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=instructions,
                        temperature=0.1, # Low temperature keeps it factual/consistent
                    ),
                )
                
                st.session_state.last_comparison = response.text
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"API Error: {e}")

# --- 6. SALES TOOLS LOGIC ---
def generate_sales_extra(task_prompt):
    if not st.session_state.last_comparison:
        st.sidebar.warning("Search for a printer in the chat first!")
        return
    
    with st.chat_message("assistant"):
        with st.status(f"Creating {task_prompt}...", expanded=True):
            try:
                # This prompt takes the specific match found above and transforms it
                full_request = f"Using this match: '{st.session_state.last_comparison}', please {task_prompt}."
                res = client.models.generate_content(
                    model=MODEL_ID,
                    contents=full_request,
                    config=types.GenerateContentConfig(system_instruction=instructions)
                )
                st.markdown(res.text)
            except Exception as e:
                st.error(f"Error: {e}")

if pitch_btn: generate_sales_extra("write a high-energy 30-second sales pitch")
if prop_btn:  generate_sales_extra("draft a formal 1-page sales proposal letter")
if deck_btn:  generate_sales_extra("outline a 5-slide presentation deck")
if quote_btn: generate_sales_extra("create a professional price quote table")
