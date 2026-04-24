# To run this code you need to install the following dependencies:
# pip install google-genai

import os
from google import genai
from google.genai import types


def generate():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-3-flash-preview"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""INSERT_INPUT_HERE"""),
            ],
        ),
    ]
    tools = [
        types.Tool(googleSearch=types.GoogleSearch(
        )),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level="HIGH",
        ),
        tools=tools,
        system_instruction=[
            types.Part.from_text(text="""You are a Printer Replacement Expert. I will provide you with a list of our company's printers. When a user tells you a competitor printer model, compare its specs to our list and recommend the best 1-to-1 replacement. Explain why based on Price, PPM (Pages Per Minute), and Functions. If you don't know the competitor model, ask for its specs.

Customer Name	Current Equipment	Current Monthly Volume	Pain Points
Terhune Company	5 HP LaserJet Printers	8000	High repair costs, slow scanning


Canon Model	Categrory	Max Monthly Volume	Key Features	Est. Monthly Lease
imageCLASS LBP246dx	Home Printers	750-4,000	Easy Wifi Setup, Fast Printing Speeds, Intuitive 5-Line LCD	$81
ImageRUNNER Advance 4925i	Office Printers & Copiers	10000-50000	Black and white, multifunction, print up to 25 ppm	$500
Color imageCLASS X LBP1538C II	Home/Small Office Printers	5000-10000	Color Printer, Compact, User Friendly	$400
				"""),
        ],
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if text := chunk.text:
            print(text, end="")

if __name__ == "__main__":
    generate()


