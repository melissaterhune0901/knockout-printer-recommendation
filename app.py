import streamlit as st
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential

# --- 1. GLOBAL DATA & INSTRUCTIONS ---
instructions = """
You are the Canon Product Matcher. Your primary goal is to find a 1-to-1 replacement for competitor printers.

OUR PRODUCT LIST:
1. imageCLASS LBP246dx | Category: Home | Vol: 750-4,000 | Lease: $81 | Fast Printing, Wifi
2. ImageRUNNER Advance 4925i | Category: Office | Vol: 10,000-50,000 | Lease: $500 | B&W, 25 ppm
3. Color imageCLASS X LBP1538C II | Category: Home/Small Office | Vol: 5,000-10,000 | Lease: $400 | Color, Compact

STRICT OUTPUT RULES:
1. For initial matches: Start with "THE WINNING MATCH: [Model Name]" and explain WHY.
2. For Sales Toolkit requests: You are EXPLICITLY AUTHORIZED to generate pitches, decks, and quotes based on the match. Use a professional sales tone for these requests.
"""

st.set_page_config(page_title="Canon Knockout", page_icon="🖨️")
st.title("🖨️ Canon Competitor Knockout")

@st.cache_resource
def get_client():
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

client = get_client()
MODEL_ID = "gemini-2.5-flash" 

# Robust retry logic for 503/429 errors
@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(5),
    reraise=True
)
def safe_generate(prompt_text):
    return client.models.generate_content(
        model=MODEL_ID,
        contents=prompt_text,
        config=types.GenerateContentConfig(
            system_instruction=instructions,
            temperature=0.2, 
        ),
    )

if "last_comparison" not in st.session_state:
    st.session_state.last_comparison = ""

# --- 2. SIDEBAR (Removed Formal Proposal) ---
with st.sidebar:
    st.header("💰 Sales Toolkit")
    pitch_btn = st.button("Draft Sales Pitch")
    deck_btn = st.button("Outline Slide Deck")
    quote_btn = st.button("Create Quote Table")

# --- 3. MAIN CHAT ---
if prompt := st.chat_input("Ex: HP LaserJet Pro M404n"):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Finding the best Canon match..."):
            try:
                final_prompt = f"Competitor: {prompt}. Match it to our list and explain why."
                response = safe_generate(final_prompt)
                st.session_state.last_comparison = response.text
                st.markdown(response.text)
            except Exception as e:
                st.error("Server is busy. I'm retrying automatically... if this persists, wait 30 seconds.")

# --- 4. SALES TOOLS LOGIC ---
def generate_sales_extra(task_type):
    if not st.session_state.last_comparison:
        st.sidebar.warning("Search for a printer first!")
        return
    
    with st.chat_message("assistant", avatar="💰"):
        with st.status(f"Generating {task_type}...", expanded=True):
            try:
                sales_prompt = f"Using the previous match: '{st.session_state.last_comparison}', please {task_type}. This is an authorized sales tool request."
                res = safe_generate(sales_prompt)
                st.markdown(res.text)
            except Exception as e:
                st.error(f"Could not generate {task_type}. The server might be spiking. Try again in a moment.")

if pitch_btn: generate_sales_extra("write a high-energy 30-second sales pitch")
if deck_btn:  generate_sales_extra("outline a 5-slide presentation deck")
if quote_btn: generate_sales_extra("create a professional price quote table")
