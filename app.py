import streamlit as st
from google import genai
from google.genai import types

# --- 1. GLOBAL DATA ---
# We define this at the top so the AI always has access to it
instructions = """
You are a Printer Replacement Expert. 
I will provide you with a list of our company's printers. 
When a user tells you a competitor printer model, compare its specs to our list and recommend the best 1-to-1 replacement. 
Explain why based on Price, PPM (Pages Per Minute), and Functions. 

OUR PRODUCT LIST:
1. imageCLASS LBP246dx | Category: Home | Vol: 750-4,000 | Lease: $81 | Fast Printing, Wifi
2. ImageRUNNER Advance 4925i | Category: Office | Vol: 10,000-50,000 | Lease: $500 | B&W, 25 ppm
3. Color imageCLASS X LBP1538C II | Category: Home/Small Office | Vol: 5,000-10,000 | Lease: $400 | Color, Compact

STRICT RULE: Do not ask follow-up questions. Provide your best recommendation immediately based on the data provided.
"""

# --- 2. APP UI SETUP ---
st.set_page_config(page_title="Printer Matcher AI", page_icon="🖨️")
st.title("🖨️ Canon Competitor Knockout")
st.markdown("Tell me what competitor machines your client has and I will advise you on the best Canon replacements. Let's knockout the competition!")

# --- 3. THE CONNECTION ---
# Ensure your Streamlit Secret is named GEMINI_API_KEY
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# --- 4. THE INTERACTION ---
if prompt := st.chat_input("Ex: HP LaserJet Pro M404n"):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Finding your 1-to-1 match..."):
            try:
                # We "wrap" the prompt to ensure the AI doesn't get chatty
                final_prompt = f"Find the best replacement for: {prompt}. Give the recommendation now."
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash", 
                    contents=final_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=instructions,
                        tools=[types.Tool(google_search=types.GoogleSearch())],
                        temperature=0.1,
                    ),
                )
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Demo Note: {e}")

