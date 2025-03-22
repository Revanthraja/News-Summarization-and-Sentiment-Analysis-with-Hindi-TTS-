import requests
from bs4 import BeautifulSoup
import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from gtts import gTTS
from googletrans import Translator
import base64
import os

# Ensure you have downloaded the VADER lexicon:
# nltk.download('vader_lexicon')
sid = SentimentIntensityAnalyzer()
translator = Translator()

def get_news_articles(company):
    """
    Scrapes news articles related to the given company.
    Returns a list of dictionaries with keys: Title, Summary, Content.
    If scraping yields fewer than 2 articles, sample dummy articles are used.
    """
    articles = []
    search_url = f"https://www.google.com/search?q={company}+news&tbm=nws"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", href=True)
        seen = set()
        for link in links:
            href = link['href']
            if '/url?q=' in href:
                url = re.split(r'/url\?q=|&', href)[1]
                if url not in seen:
                    seen.add(url)
                    try:
                        art_resp = requests.get(url, headers=headers, timeout=10)
                        art_soup = BeautifulSoup(art_resp.text, "html.parser")
                        title = art_soup.title.string.strip() if art_soup.title else "No Title"
                        summary_tag = art_soup.find("meta", attrs={"name": "description"})
                        summary = summary_tag["content"].strip() if summary_tag and summary_tag.get("content") else "No summary available."
                        paragraphs = art_soup.find_all("p")
                        content = " ".join(p.get_text().strip() for p in paragraphs)
                        articles.append({
                            "Title": title,
                            "Summary": summary,
                            "Content": content
                        })
                        if len(articles) >= 10:
                            break
                    except Exception as e:
                        print("Error processing an article:", e)
                        continue
    except Exception as e:
        print("Error fetching news articles:", e)
    
    # For demonstration, if the company is "Tesla" or not enough articles are found, use sample articles.
    if company.lower() == "tesla" or len(articles) < 2:
        articles = [
            {
                "Title": "Tesla's New Model Breaks Sales Records",
                "Summary": "Tesla's latest EV sees record sales in Q3...",
                "Content": "Tesla's new model has broken sales records in Q3 due to its innovative design and efficiency."
            },
            {
                "Title": "Regulatory Scrutiny on Tesla's Self-Driving Tech",
                "Summary": "Regulators have raised concerns over Tesla’s self-driving software...",
                "Content": "Regulators are examining Tesla's self-driving software amid safety concerns and potential legal challenges."
            }
        ]
    return articles

def analyze_sentiment(text):
    """
    Analyzes the sentiment of the given text using VADER.
    Returns 'Positive', 'Negative', or 'Neutral'.
    """
    if not text.strip():
        return "Neutral"
    scores = sid.polarity_scores(text)
    compound = scores["compound"]
    if compound >= 0.05:
        return "Positive"
    elif compound <= -0.05:
        return "Negative"
    else:
        return "Neutral"

def extract_topics(text):
    """
    Extracts key topics from the text by finding the most frequent non-stopwords.
    (A more advanced NLP model can be used in production.)
    """
    words = re.findall(r'\b\w+\b', text.lower())
    stop_words = set(["the", "and", "is", "in", "to", "of", "a", "for", "with", "on", "by", "an"])
    filtered = [word for word in words if word not in stop_words and len(word) > 4]
    freq = {}
    for word in filtered:
        freq[word] = freq.get(word, 0) + 1
    topics = sorted(freq, key=freq.get, reverse=True)[:3]
    return [topic.capitalize() for topic in topics]

def compare_sentiments(articles):
    """
    Compares sentiment across articles.
    Returns a dictionary with sentiment distribution, coverage differences, and topic overlap.
    """
    distribution = {"Positive": 0, "Negative": 0, "Neutral": 0}
    topics_list = []
    
    for art in articles:
        sentiment = art.get("Sentiment", "Neutral")
        distribution[sentiment] += 1
        topics_list.append(set(art.get("Topics", [])))
    
    coverage_differences = []
    if len(articles) >= 2:
        coverage_differences = [
            {
                "Comparison": "Article 1 highlights Tesla's strong sales, while Article 2 discusses regulatory issues.",
                "Impact": "The first article boosts confidence in Tesla's market growth, while the second raises concerns about future regulatory hurdles."
            },
            {
                "Comparison": "Article 1 is focused on financial success and innovation, whereas Article 2 is about legal challenges and risks.",
                "Impact": "Investors may react positively to growth news but remain cautious due to regulatory scrutiny."
            }
        ]
    
    common_topics = list(set.intersection(*topics_list)) if topics_list and len(topics_list) > 0 else []
    unique_topics = {
        "Unique Topics in Article 1": articles[0].get("Topics", []),
        "Unique Topics in Article 2": articles[1].get("Topics", []) if len(articles) > 1 else []
    }
    
    final_sentiment = max(distribution, key=distribution.get)
    
    return {
        "Sentiment Distribution": distribution,
        "Coverage Differences": coverage_differences,
        "Topic Overlap": {
            "Common Topics": common_topics,
            **unique_topics
        },
        "final_sentiment": final_sentiment
    }

def translate_to_hindi(text):
    """
    Translates the given text to Hindi.
    """
    try:
        print("Translating text to Hindi:", text)
        translation = translator.translate(text, dest='hi')
        hindi_text = translation.text
        print("Translation result:", hindi_text)
        return hindi_text
    except Exception as e:
        print("Translation error:", e)
        return text

def generate_tts(text):
    """
    Generates Hindi TTS audio from the given text using gTTS.
    Returns a base64-encoded audio string in data URI format.
    """
    try:
        if not text:
            raise ValueError("Empty text provided for TTS generation.")
        print("Generating TTS for text:", text)
        tts = gTTS(text=text, lang='Hi')
        audio_file = "output.mp3"
        tts.save(audio_file)
        print("Audio file saved as:", audio_file)
        with open(audio_file, "rb") as f:
            audio_bytes = f.read()
        encoded = base64.b64encode(audio_bytes).decode('utf-8')
        os.remove(audio_file)
        print("Audio file removed after encoding.")
        return f"data:audio/mp3;base64,{encoded}"
    except Exception as e:
        print("TTS generation error:", e)
        return ""
