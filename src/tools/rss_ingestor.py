import feedparser
import json
import os

# Define the output path
JSON_PATH = os.path.join(os.path.dirname(__file__), '../../data/et_articles.json')

# ET RSS Feeds highly relevant to the hackathon scenarios
RSS_FEEDS = {
    "Markets": "https://economictimes.indiatimes.com/markets/rssfeeds/2146842.cms",
    "Wealth": "https://economictimes.indiatimes.com/wealth/rssfeeds/8371324.cms"
}

def ingest_rss_feeds():
    print("Fetching articles from ET RSS feeds...")
    all_articles = []
    
    for category, url in RSS_FEEDS.items():
        print(f"Parsing {category} feed...")
        feed = feedparser.parse(url)
        
        # Grab the top 15 most recent articles per feed to keep the database focused
        for entry in feed.entries[:15]:
            article_data = {
                "product_id": f"article_{entry.id if hasattr(entry, 'id') else entry.link}",
                "title": entry.title,
                "type": "article",
                "category": category,
                "description": entry.summary if hasattr(entry, 'summary') else "No summary available.",
                "url": entry.link,
                "published_date": entry.published if hasattr(entry, 'published') else "Unknown"
            }
            all_articles.append(article_data)

    # Save to JSON
    # Ensure the data directory exists just in case
    os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
    
    with open(JSON_PATH, 'w', encoding='utf-8') as file:
        json.dump(all_articles, file, indent=2, ensure_ascii=False)
        
    print(f"Successfully saved {len(all_articles)} articles to {JSON_PATH}!")

if __name__ == "__main__":
    ingest_rss_feeds()