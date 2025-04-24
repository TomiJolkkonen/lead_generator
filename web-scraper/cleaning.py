import re
import pandas as pd

def load_keywords(file_path):
    # Load keywords from a text file
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            keywords = [line.strip() for line in file if line.strip()]
        return keywords
    except Exception as e:
        print(f"Error loading keywords: {e}")
        return []

def clean_description(text):
    # Remove emails and phone numbers
    text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b", "***", text)
    text = re.sub(r"\+?\d[\d -]{8,}\d", "******", text)

     # Replace commas inside descriptions with a space
    text = text.replace(",", " ")
    
    # Remove newline characters and replace them with a space
    text = text.replace("\n", " ")

    # Remove both single and double quotes
    text = text.replace('"', '').replace("'", "")
    
    # Remove excessive spaces (replace multiple spaces with a single space)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def clean_title(title):
    import re

def clean_title(title):
    # Remove unnecessary symbols and short words from job titles
    title = re.sub(r",", " ", title)  # Replace commas with a space
    title = re.sub(r'\s*/\s*', " ", title)  # Replace '/' with a space
    title = re.sub(r"\.{2,}", "", title)  # Remove consecutive dots (.. or more)
    title = title.replace('"', "").replace("'", "").strip()  # Remove double and single quotes and trim spaces
    title = re.sub(r"\s+", " ", title).strip() # Remove excessive spaces (replace multiple spaces with a single space)

    # Remove emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & pictographs
        "\U0001F680-\U0001F6FF"  # Transport & map symbols
        "\U0001F700-\U0001F77F"  # Alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric shapes
        "\U0001F800-\U0001F8FF"  # Supplemental symbols
        "\U0001F900-\U0001F9FF"  # Supplemental symbols and pictographs
        "\U0001FA00-\U0001FA6F"  # Symbols for legacy computing
        "\U0001FA70-\U0001FAFF"  # More symbols
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE
    )
    title = emoji_pattern.sub("", title)  # Remove emojis

    return title


def clean_location(location):
    # Standardize location names
    return location.split(",")[0].strip() if location else "Unknown"

def mark_matching_jobs(df, keywords):
    #Creates separate columns for each keyword, initializing with 0, and marking 1 if found.
    for keyword in keywords:
        df[keyword] = 0  # Initialize column with 0

        # Special rule for "ai" to match only as a full word
        if keyword.lower() == "ai":
            pattern = r"(?<!\w)ai(?!\w)"  # Ensures "ai" is not part of another word
        else:
            pattern = fr"\b{re.escape(keyword)}\b"  # Default match for other keywords

        df.loc[df["description"].str.contains(pattern, case=False, na=False), keyword] = 1
    return df

def clean_data(df):
    # Cleans and processes the scraped data, then marks keyword matches
    KEYWORDS_FILE = "web-scraper/job-keywords.txt"
    KEYWORDS = load_keywords(KEYWORDS_FILE)
    
    df["description"] = df["description"].apply(clean_description)
    df["title"] = df["title"].apply(clean_title)
    df["location"] = df["location"].apply(clean_location)
    
    # Remove hyphen from Y-tunnus
    df["y_tunnus"] = df["y_tunnus"].str.replace("-", "", regex=True)
    
    # Add keyword columns
    df = mark_matching_jobs(df, KEYWORDS)
    
    # Exclude rows that do not have any keyword match
    df = df[df[KEYWORDS].sum(axis=1) > 0]
    
    # Reorder columns
    column_order = ["y_tunnus", "company", "scrape_date", "title", "location", "description"] + KEYWORDS
    df = df[column_order]
    
    return df