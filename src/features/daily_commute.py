import requests
from gtts import gTTS
import os
from dotenv import load_dotenv
from src.core.llm_provider import get_llm

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# ---------- STEP 1: Get latest market news ----------

def get_market_news():
    url = f"https://newsapi.org/v2/everything?q=stock%20market%20india&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}"

    response = requests.get(url).json()

    headlines = []

    for article in response["articles"][:5]:
        headlines.append(article["title"])

    return headlines


# ---------- STEP 2: Generate personalized podcast script ----------

def generate_audio_script(headlines, persona="first_time_investor"):

    llm = get_llm(provider="groq")

    news_text = "\n".join(headlines)

    prompt = f"""
You are the official AI host of **ET Daily Commute**, a personalized 2-minute audio briefing from The Economic Times.

Your job is NOT just to summarize news. Your job is to:
1. Explain the market news in simple language
2. Personalize it based on the user's persona
3. Suggest ONE highly relevant Economic Times product at the end
   (like ET Masterclass, ET Prime article, or ET Markets insights)

User persona: {persona}

Here are the latest market headlines:
{news_text}

Now create a short morning podcast script using this structure:

PART 1- Friendly opening (like a daily briefing host)
PART 2 -Explain what happened in the market (in simple words if user is a beginner)
PART 3 - Why this matters for THIS user (based on persona)
PART 4 - Recommend ONE relevant ET product:
   - If persona = beginner → recommend ET Masterclass
   - If persona = investor → recommend ET Markets insights
   - If persona = news reader → recommend ET Prime article

IMPORTANT RULES:
- Make it sound like a real financial podcast
- Keep it 120–150 words only
- Keep the tone smart but friendly
- Always include one ET recommendation at the end
- Do NOT give generic advice — keep it relevant to the user

Return only the podcast script.
"""

    result = llm.invoke(prompt)

    return result.content


# ---------- STEP 3: Convert text to audio ----------

def convert_to_audio(script_text):

    tts = gTTS(script_text)

    if not os.path.exists("audio"):
        os.makedirs("audio")

    file_path = "audio/et_daily_commute.mp3"

    tts.save(file_path)

    return file_path


# ---------- MAIN FUNCTION ----------

def run_daily_commute(persona):

    print("\nFetching latest market news...")

    headlines = get_market_news()

    print("Generating personalized script...")

    script = generate_audio_script(headlines,persona)

    print("\nSCRIPT:\n")
    print(script)

    print("\nConverting to audio...")

    file = convert_to_audio(script)

    print("\nDone! Your audio file is saved at:")
    print(file)


# ---------- RUN ----------
if __name__ == "__main__":
    run_daily_commute()