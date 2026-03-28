import requests
from bs4 import BeautifulSoup
import json
import os

# Path to the JSON file you created in Step 2
JSON_PATH = os.path.join(os.path.dirname(__file__), '../../data/et_masterclasses.json')

def scrape_et_masterclasses():
    print("Fetching live data from ET Masterclass...")
    url = "https://economictimes.indiatimes.com/masterclass"
    
    # We use a standard User-Agent so the website doesn't block our request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        new_classes = []
        
        # NOTE: HTML structures change. Based on typical ET layout, we look for heading tags or specific class names.
        # If the exact class names change on the live site, this generic fallback grabs all h2/h3 tags.
        course_elements = soup.find_all(['h2', 'h3']) 
        
        for i, element in enumerate(course_elements):
            title = element.get_text(strip=True)
            # Skip empty tags or generic navigation text
            if len(title) > 10 and "Masterclass" not in title:
                
                # Attempt to find the paragraph immediately following the title for a description
                desc_tag = element.find_next_sibling('p')
                description = desc_tag.get_text(strip=True) if desc_tag else "A comprehensive masterclass by industry experts."

                course_data = {
                    "product_id": f"scraped_mc_{i}",
                    "title": title,
                    "type": "masterclass",
                    "target_audience": "professionals, general audience",
                    "description": description,
                    "url": url
                }
                new_classes.append(course_data)

        # 4. Merge with our hardcoded scenario data!
        if os.path.exists(JSON_PATH):
            with open(JSON_PATH, 'r') as file:
                existing_data = json.load(file)
        else:
            existing_data = []

        # Combine them, ensuring we don't overwrite the hardcoded ones
        combined_data = existing_data + new_classes

        with open(JSON_PATH, 'w') as file:
            json.dump(combined_data, file, indent=2)
            
        print(f"Successfully scraped {len(new_classes)} live classes and added them to the database!")

    except requests.exceptions.RequestException as e:
        print(f"Error scraping the website: {e}")

if __name__ == "__main__":
    scrape_et_masterclasses()