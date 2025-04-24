import requests
import json
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from config import KEY_VAULT_URL, SECRET_NAME

# Vainu API Endpoint
API_URL = "https://api.vainu.io/api/v2/companies/"


# Authenticate using DefaultAzureCredential (Managed Identity, CLI, or Env Variables)
credential = DefaultAzureCredential()
client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)

# Fetch the API key
secret = client.get_secret(SECRET_NAME)
API_KEY = secret.value
#print(API_KEY)

# Headers for authentication
headers = {
    "API-Key": f"{API_KEY}",
    "Content-Type": "application/json"
}

# Define API query parameters
params = {
    "country": "FI",  # Filter by Finland
    "fields": "company_name,business_id,financial_statements,technology_data,organization_size_indicators,vainu_custom_industry",
    "business_id":"05339652"
    #"order":"turn_over"
}

# Make API request
response = requests.get(API_URL, headers=headers, params=params)

# Check response status
if response.status_code == 200:
    data = response.json()
    with open("vainu/vainu_data.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
        print("Data saved to vainu_data.json")
    # for company in data.get("results", []):
    #     print(f"Company Name: {company.get('company_name')}")
    #     print(f"Business ID: {company.get('business_id')}")
    #     print(f"Staff Count: {company.get('staff_number')} employees")
    #     print(f"Staff Count estimation: {company.get('staff_number_estimate')} employees")
    #     print(f"Development of turnover: {company.get('development_of_turnover')}")
    #     print(f"Turnover: {company.get('turn_over', 'N/A')} €")
    #     print(f"Profit: {company.get('profit', 'N/A')} %")
    #     print(f"industry: {company.get('vainu_custom_industry')}")
    #     print(f"status: {company.get('official_status')}")
    #     print(f"funding: {company.get('total_funding_usd')}")
    #     print("-" * 40)
else:
    print("Error:", response.status_code, response.text)
