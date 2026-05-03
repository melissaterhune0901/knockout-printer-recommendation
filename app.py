import streamlit as st
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential

# --- 1. UPDATED INSTRUCTIONS FOR PRIORITY LOGIC ---
instructions = """
You are the Canon Product Matcher. 

ORDER OF OPERATIONS:
1. INTERNAL DATA CHECK: First, look at 'OUR PRODUCT LIST' below.
2. COMPETITOR RESEARCH: Only after checking our list, use Google Search to find the exact specs of the competitor model provided by the user.
3. SYNTHESIS: Compare the competitor's specs found via search against the volume, category, and features of our products.

OUR PRODUCT LIST:
1. imageCLASS LBP246dx | Category: Home | Vol: 750-4,000 | Lease: $81 | Fast Printing, Wifi
2. ImageRUNNER Advance 4925i | Category: Office | Vol: 10,000-50,000 | Lease: $500 | B&W, 25 ppm
3. Color imageCLASS X LBP1538C II | Category: Home/Small Office | Vol: 5,000-10,000 | Lease: $400 | Color, Compact

STRICT OUTPUT RULES:
- Start with "THE WINNING MATCH: [Model Name]".
- Explain the match by referencing specific specs from Google Search and how they align with our product's stats.
"""

st.set_page_config(page_title="Canon Knockout", page_icon="🖨️")
st.title("🖨️ Canon Competitor Knockout")

@st.cache_resource
def get_client():
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

client = get_client()
MODEL_ID = "gemini-2.5-flash" 

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
            temperature=0.0, # Lowered to 0.0 for stricter adherence to your data
            tools=[types.Tool(google_search_retrieval=types.GoogleSearchRetrieval())]
        ),
    )

if "last_comparison" not in st.session_state:
    st.session_state.last_comparison = ""

# --- 3. MAIN CHAT ---
if prompt := st.chat_input("Ex: HP LaserJet Pro M404n"):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing our inventory and searching Google for competitor specs..."):
            try:
                # We "anchor" the prompt to force the model to look at the list first
                anchored_prompt = f"Using our Canon product list as the primary source, search Google for the specs of '{prompt}' and find the best match."
                response = safe_generate(anchored_prompt)
                st.session_state.last_comparison = response.text
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Error: {e}")

# (Rest of your Sales Toolkit logic remains the same)
