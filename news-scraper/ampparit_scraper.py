import os
import aiohttp
import asyncio
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import re
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient
from config import KEY_VAULT_URL, SECRET_NAME

# ✅ Load keywords from a file
def load_keywords(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            keywords = [line.strip() for line in file if line.strip()]
        return keywords
    except Exception as e:
        print(f"Error loading keywords: {e}")
        return []

def mark_matching_keywords(headline, keywords):
    # Returns True if at least one keyword is found in the headline. 
    return any(re.search(r"\b" + re.escape(keyword) + r"\b", headline, re.IGNORECASE) for keyword in keywords)

async def fetch(session, url, headers):
    # Fetches a webpage asynchronously
    async with session.get(url, headers=headers) as response:
        return await response.text()

async def scrape_ampparit(search_urls, keywords, headers):
    # Scrapes Ampparit.com for news related to multiple keywords
    async with aiohttp.ClientSession() as session:
        news_list = []

        for url in search_urls:
            html = await fetch(session, url, headers)
            soup = BeautifulSoup(html, "html.parser")

            # 🔹 Find all news items
            articles = soup.select("div.item-text")

            for article in articles:
                # ✅ Extract headline
                headline_tag = article.find("a", class_="news-item-headline")
                headline = headline_tag.get_text(strip=True) if headline_tag else None

                # ✅ Extract media (news source)
                source_tag = article.find("span", class_="item-details__detail_source")
                media = source_tag.get_text(strip=True) if source_tag else None

                # ✅ Filter: Only save headlines that contain any of the keywords
                if headline and media and mark_matching_keywords(headline, keywords):
                    news_list.append({"media": media, "headline": headline})

        return pd.DataFrame(news_list, columns=["media", "headline"])

async def save_to_blob(news_data, container_name, blob_folder, blob_service_client):
    # Saves news data to Azure Blob Storage
    if news_data.empty:
        print("❌ No matching news found.")
        return

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    output_file = f"ampparit_news_{timestamp}.csv"
    blob_path = f"{blob_folder}/{output_file}"

    # Convert DataFrame to CSV format
    csv_data = news_data.to_csv(index=False, encoding="utf-8")

    # Upload CSV to Blob Storage
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_path)
    
    try:
        blob_client.upload_blob(csv_data, overwrite=True)
        print(f"✅ Scraped news saved to Azure Blob Storage: {blob_path}")
    except Exception as e:
        print(f"Error uploading to Azure Blob Storage: {e}")

async def main():
    # ✅ Define the path to the keywords file and other configurations inside main
    KEYWORDS_FILE = "news-scraper/news-keywords.txt"  # Adjust the path as needed
    KEYWORDS = load_keywords(KEYWORDS_FILE)

    SEARCH_URLS = [f"https://www.ampparit.com/haku?q={keyword}" for keyword in KEYWORDS]
    HEADERS = {"User-Agent": "Mozilla/5.0"}

    # Azure Storage details
    CONTAINER_NAME = "news-data"
    BLOB_FOLDER = "news_listings"

    # Fetch the connection string from Azure Key Vault
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)
    connection_string = client.get_secret(SECRET_NAME).value

    # Initialize BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    print("Starting news scraping...")
    news_data = await scrape_ampparit(SEARCH_URLS, KEYWORDS, HEADERS)
    await save_to_blob(news_data, CONTAINER_NAME, BLOB_FOLDER, blob_service_client)

if __name__ == "__main__":
    asyncio.run(main())