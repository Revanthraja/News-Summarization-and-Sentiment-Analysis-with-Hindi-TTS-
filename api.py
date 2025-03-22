from flask import Flask, request, jsonify
import utils

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    company = data.get('company')
    if not company:
        return jsonify({"error": "No company provided"}), 400

    # Extract news articles
    articles = utils.get_news_articles(company)
    
    # Process each article: add sentiment and topics
    for article in articles:
        content = article.get("Content", "")
        article["Sentiment"] = utils.analyze_sentiment(content)
        article["Topics"] = utils.extract_topics(content)
    
    # Perform comparative analysis
    comparative = utils.compare_sentiments(articles)
    
    # Generate final summary and translate to Hindi for TTS
    final_summary = f"{company} news coverage is mostly {comparative['final_sentiment']}."
    hindi_summary = utils.translate_to_hindi(final_summary)
    audio_data = utils.generate_tts(hindi_summary)
    
    # Build the final JSON report matching your desired structure
    report = {
        "Company": company,
        "Articles": articles,
        "Comparative Sentiment Score": {
            "Sentiment Distribution": comparative.get("Sentiment Distribution", {}),
            "Coverage Differences": comparative.get("Coverage Differences", []),
            "Topic Overlap": comparative.get("Topic Overlap", {})
        },
        "Final Sentiment Analysis": final_summary,
        "Audio": audio_data  # Data URI that the frontend will decode and play.
    }
    return jsonify(report)

if __name__ == '__main__':
    app.run(debug=True)
