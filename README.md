# Sales lead generation tool - final project of data engineer intensive training program

## Business requirements

Proof-of-concept of a lead generator tool to help sales teams in this case to find interesting prospects that would have a high possibility to hire data engineers.

A Power BI Tool is needed to be used by a sales team. The tool should be able to:
- List, filter and rank sales leads from multiple sources

## Sources

Vainu:
- Main source for company data


Job posting sites (Duunitori):
- Job posting volume, keywords

## Prospect validation
- Turnover more than 500k€
- Staff number over 10 people
- Country: FI
- Cities: "helsinki", "tampere", "vantaa", "espoo", "oulu", "turku", "lahti", "jyväskylä"

## Team members and responsibilities
- Samu Syväoja (code, Fabric, Power BI)
- Linda Ulma (code, Azure, Fabric, Power BI)
- Tomi Jolkkonen (code, Power BI)  

## Tech used
- Microsoft Fabric
- Python
- Azure
- Azure Blob Storage
- Azure Key Vault
- Fabric Lakehouse
- Fabric PySpark Notebook
- Fabric data pipelines
- Power BI
- DAX measures


## What's included in the project and how it's set up

### 1. Scrapers
- Duunitori.fi scraper for scraping job postings in data engineering (code can be found in GitHub)
- Ampparit.com scraper for scraping news in IT and looking for certaing keywords (code can be found in GitHub)

#### Running scrapers
- Scrapers need to be run manually and locally, preferably in VS Code
- Config file needs to be created under the scrapers folder, which wants to be run
- In config file, add two rows:  
KEY_VAULT_URL = "key vault url here to access vainu API data"  
SECRET_NAME = "insert your secret name here"
- Dependencies need to be installed before running code, to do that, in the "web-scraper" -folder run command: pip install -r requirements.txt
- To run the code for job-posting scraper, click Run in the main.py file under web-scraper folder
- To get job-postings data to Power BI, run the "clean_job_postings" -notebook and after that "Dataflow jobs" in Fabric
- To run the code for news scraper, click Run in the ampparit-scraper.py file under news-scraper folder. Note that news are currently not included in the resulting data in Power BI, but there is a "clean_news" -notebook in Fabric.
- Note: if you also need to update Vainu data, first run the scrapers and then you can just run the "Master pipeline" instead of the notebook and Dataflow

### 2. GitHub
- Repository including code for scrapers
- Technical documentation (README)

### 2. Azure
- Storage account / Data Lake: leadgeneratorstorage
- Vainu api key and storage account connection string are stored in Key Vault

### 3. Fabric
- Lakehouse: lead_generator_lakehouse for bronze, silver and gold data (news weren't used in gold data after all)
- Warehouse: lead_generator_warehouse original plan was to use warehouse for gold data, but the idea had to be ditched since there were problems with creating relationships between tables
- Notebooks for transforming and cleaning data: clean_job_postings, clean_news, vainu_api_bronze_to_lakehouse, vainu_bronze_to_silver
- Master pipeline to run all notebooks and create gold data

#### Fetching data from Vainu
- In Fabric, first run "vainu_api_bronze_to_lakehouse" -notebook
- Next run "vainu_bronze_to_silver" -notebook
- Run dataflows "Dataflow general", "Dataflow financial", "Dataflow industries official" and "Dataflow vainu industries"
- Note: if you also need to update job-postings data, first run the scrapers (instructions under "Running scrapers") and then you can ignore the instructions above and just run the "Master pipeline"

### 4. PowerBI
- App for sales team to look for leads

### 5. Jira
- Kanban board including all tasks related to the project
- Also some documentation included

### Overview of master pipeline
![image](https://github.com/user-attachments/assets/369ce3c4-125e-4be5-8ab4-3c865f5886bb)
1. Notebooks for fetching data and transforming data are ran simultaneously
2. Dataflows for creating gold tables of the data and loading the gold tables back to the lakehouse (if warehouse wants to be used, only destination for tables needs to be modified)
3. Two stored procedures for moving data from one schema to another in the warehouse and for creating relationships. These are currently not activated, since warehouse didn't work, but they can be used, if warehouse starts working later
4. If all data needs to be updated, the pipeline can be run. If only for example job-postings need to fetched, please follow the instructions under "Running scrapers" in this file.

### Architecture
![lead-generator architecture](https://github.com/user-attachments/assets/eae8349c-52b9-4dde-8fe2-8290c656cc13)

### Color palette for Power BI
Color palette for Power BI report can be found [here](https://coolors.co/1a2239-262d49-ef376d-fac10e-38d989-39c2f0)

## Lead Score Calculation
- Company Size Score: Company is evaluated based on turnover
- Financial Health Score: Company is evaluated based on profit margin
- Growth Score: Company is evaluated based on turnover and profit margin growth
- Job Posting Score: Company is evaluated based on job postings with relevant keywords
- Industry Score: Company is evaluated based on industry related keywords determined by Vainu
- Lead Score: Weighted calculation of all of the above

## Final result
A Power BI app for ranking leads
![image](https://github.com/user-attachments/assets/35ce3207-e352-4d79-a72d-b718eb70d9c6)


## Future development opportunities
- Slicer for adjusting weights for the lead score
- Industry slicer to view scores per industry
