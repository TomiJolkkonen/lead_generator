import aiohttp
import asyncio
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

BASE_URL = "https://duunitori.fi/tyopaikat?haku=data%20engineer"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# ✅ Define locations in Finland (for filtering)
FINLAND_LOCATIONS = {
    "Helsinki", "Espoo", "Tampere", "Vantaa", "Oulu", "Turku", "Jyväskylä", "Lahti",
    "Kuopio", "Pori", "Lappeenranta", "Vaasa", "Kotka", "Joensuu", "Seinäjoki",
    "Hyvinkää", "Nokia", "Kajaani", "Rauma", "Lohja", "Kouvola", "Rovaniemi",
    "Finland", "Suomi"
}

async def fetch(session, url):
    """Fetches a URL asynchronously."""
    async with session.get(url, headers=HEADERS) as response:
        return await response.text()

async def fetch_job_details(session, job_url):
    """Fetches job title, description, location, and Y-tunnus asynchronously."""
    try:
        html = await fetch(session, job_url)
        soup = BeautifulSoup(html, "html.parser")

        # ✅ Get the correct job title from <h1 class="text--break-word">
        title_tag = soup.select_one("h1.text--break-word")
        title = title_tag.get_text(strip=True) if title_tag else "Unknown"

        # ✅ Extract job description
        description = " ".join([
            tag.get_text(strip=True)
            for tag in soup.select("div.description-box > div.description.description--jobentry")
        ]) or "N/A"

        # ✅ Extract location
        location_tag = soup.select_one("div.info-listing__link > a > span")
        location = location_tag.get_text(strip=True) if location_tag else "Unknown"

        # ✅ Extract Y-tunnus
        y_tunnus = "Unknown"
        for block in soup.find_all("div", class_="info-listing__block"):
            heading = block.find("h4", class_="info-listing__heading")
            if heading and "Y-tunnus" in heading.get_text():
                y_tunnus_value = block.find("span", itemprop="vatID")
                if y_tunnus_value:
                    y_tunnus = y_tunnus_value.get_text(strip=True)
                    break  # ✅ Stop searching after finding the first match

        return title, description, location, y_tunnus

    except Exception:
        return "Unknown", "N/A", "Unknown", "Unknown"

async def scrape_duunitori(max_pages=5):
    """Scrapes job listings from Duunitori asynchronously and filters jobs in Finland."""
    job_listings = []

    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, f"{BASE_URL}&page={page}") for page in range(1, max_pages + 1)]
        responses = await asyncio.gather(*tasks)  # Fetch all pages concurrently

        for html in responses:
            soup = BeautifulSoup(html, "html.parser")
            job_items = soup.select(".job-box__hover.gtm-search-result")

            for item in job_items:
                company = item.get("data-company", "N/A").title()
                job_url = item["href"] if "href" in item.attrs else "N/A"
                full_url = f"https://duunitori.fi{job_url}" if job_url != "N/A" else "N/A"

                job_listings.append({
                    "scrape_date": datetime.now().strftime("%Y-%m-%d"),
                    "company": company.strip(),
                    "job_url": full_url,
                })

        # 🔄 Fetch job details concurrently
        job_tasks = [fetch_job_details(session, job["job_url"]) for job in job_listings]
        job_details = await asyncio.gather(*job_tasks)

        # ✅ Attach job details and filter only Finnish jobs
        final_listings = []
        for job, (title, description, location, y_tunnus) in zip(job_listings, job_details):
            if any(city in location for city in FINLAND_LOCATIONS):  # ✅ Keep only jobs in Finland
                final_listings.append({
                    "y_tunnus": y_tunnus,  # ✅ Column order changed
                    "company": job["company"],
                    "scrape_date": job["scrape_date"],
                    "title": title.strip(),  # ✅ Use the corrected title from job page
                    "location": location.strip(),
                    "description": description.strip(),
                })

        # ✅ Ensure columns appear in the correct order
        df = pd.DataFrame(final_listings, columns=["y_tunnus", "company", "scrape_date", "title", "location", "description"])
        return df
