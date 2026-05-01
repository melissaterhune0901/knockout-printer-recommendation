import streamlit as st
from google import genai
from google.genai import types

# --- 1. GLOBAL DATA & INSTRUCTIONS ---
# Added "Sales Persona" instructions to the bottom of your existing text
instructions = """
You are a Printer Replacement Expert and Strategic Sales Consultant. 
I will provide you with a list of our company's printers. 
When a user tells you a competitor printer model, compare its specs to our list and recommend the best 1-to-1 replacement. 

OUR PRODUCT LIST:
1. imageCLASS LBP246dx | Category: Home | Vol: 750-4,000 | Lease: $81 | Fast Printing, Wifi
2. ImageRUNNER Advance 4925i | Category: Office | Vol: 10,000-50,000 | Lease: $500 | B&W, 25 ppm
3. Color imageCLASS X LBP1538C II | Category: Home/Small Office | Vol: 5,000-10,000 | Lease: $400 | Color, Compact

STRICT RULES:
1. TECHNICAL RECOMMENDATION: If the user provides a model, give the best match immediately.
2. SALES PITCH: If asked for a pitch, write a persuasive, high-energy 30-second script focusing on ROI and superiority.
3. SALES PROPOSAL: If asked for a proposal, create a formal professional letter for a client.
4. SALES QUOTE: If asked for a quote, create a clean markdown table showing the competitor vs. our machine and the lease price.
5. SLIDE DECK: If asked for a deck, provide a 5-slide outline with headlines and bullet points.
"""

# --- 2. APP UI SETUP ---
st.set_page_config(page_title="Printer Matcher AI", page_icon="🖨️")
st.title("🖨️ Canon Competitor Knockout")

# --- 3. THE CONNECTION ---
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Initialize Session State to store the comparison for the buttons
if "last_comparison" not in st.session_state:
    st.session_state.last_comparison = ""

# --- 4. SIDEBAR SALES TOOLS ---
with st.sidebar:
    st.header("💰 Sales Toolkit")
    st.info("First, enter a printer model in the chat. Then use these buttons to generate sales materials.")
    
    # These buttons only work if a comparison has been made first
    pitch_btn = st.button("Draft Sales Pitch")
    prop_btn = st.button("Generate Formal Proposal")
    deck_btn = st.button("Outline Slide Deck")
    quote_btn = st.button("Create Quote Table")

# --- 5. MAIN CHAT INTERACTION ---
if prompt := st.chat_input("Ex: HP LaserJet Pro M404n"):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Finding your 1-to-1 match..."):
            try:
                final_prompt = f"Find the best replacement for: {prompt}. Give the recommendation now."
                
                response = client.models.generate_content(
                    model="gemini-1.5-flash", # Updated to current flash model
                    contents=final_prompt,
             
                    config=types.GenerateContentConfig(
                    system_instruction=instructions,
                # tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.1,
),
                )
                # Store the result in session state so the buttons can "see" it
                st.session_state.last_comparison = response.text
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Error: {e}")

# --- 6. BUTTON LOGIC ---
# If a button is clicked, we send the "last_comparison" back to Gemini with a new request
def generate_sales_extra(task_prompt):
    if st.session_state.last_comparison == "":
        st.sidebar.warning("Please run a comparison in the chat first!")
        return
    
    with st.expander(f"✨ Your {task_prompt}", expanded=True):
        with st.spinner("Writing..."):
            full_request = f"Based on this comparison: '{st.session_state.last_comparison}', please {task_prompt}."
            res = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=full_request,
                config=types.GenerateContentConfig(system_instruction=instructions)
            )
            st.markdown(res.text)

if pitch_btn:
    generate_sales_extra("write a persuasive 30-second sales pitch")

if prop_btn:
    generate_sales_extra("draft a formal 1-page sales proposal letter")

if deck_btn:
    generate_sales_extra("outline a 5-slide presentation deck")

if quote_btn:
    generate_sales_extra("create a professional price quote table")

