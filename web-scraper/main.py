import os
import asyncio
import pandas as pd
from datetime import datetime
from duunitori import scrape_duunitori
from cleaning import clean_data
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from config import KEY_VAULT_URL, SECRET_NAME

# Folder where to store the files in blob storage
BLOB_FOLDER = "job_listings"

# Fetch the connection string from Azure Key Vault
credential = DefaultAzureCredential()
client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)

# Retrieve the connection string for your storage account from Key Vault
connection_string = client.get_secret(SECRET_NAME).value

# Initialize BlobServiceClient using the connection string
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_name = "duunitori-data"

async def main():
    print("Starting job scraping...")
    raw_data = await scrape_duunitori()  # Run the async scraper
    cleaned_data = clean_data(raw_data)  # Clean the data and add keyword column

    if cleaned_data.empty:
        print("❌ No jobs found. Exiting...")
        return

    # 🇫🇮 Generate Finnish-style timestamp filename (DD-MM-YYYY_HH-MM-SS)
    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    output_file = f"listing_{timestamp}.csv"

    # Define the path in the folder within Blob Storage
    blob_path = f"{BLOB_FOLDER}/{output_file}"

    # Convert the DataFrame to CSV format and store it in memory
    csv_data = cleaned_data.to_csv(index=False)

    # Upload the CSV data to the specified folder in Blob Storage
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_path)

    try:
        blob_client.upload_blob(csv_data, overwrite=True)  # Upload the CSV content to the Blob Storage
        print(f"✅ Scraped and cleaned job listings uploaded to {blob_path} in Azure Blob Storage.")
    except Exception as e:
        print(f"Error uploading blob: {e}")

if __name__ == "__main__":
    asyncio.run(main())
