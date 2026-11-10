
import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
from datetime import datetime, timezone

# ==================================
# OPPORTUNITYAI - FIRST DATA SOURCE
# ==================================

API_URL = "https://remotive.com/api/remote-jobs"

KEYWORDS = [
    "data science",
    "data scientist",
    "data analyst",
    "data engineer",
    "machine learning",
    "artificial intelligence",
    "AI engineer",
    "deep learning",
    "natural language processing",
    "NLP",
    "computer vision",
    "health informatics",
    "business intelligence",
    "Power BI",
    "data annotation",
    "Python",
    "SQL"
]


def clean_html(html):
    """Remove HTML tags from job descriptions."""
    soup = BeautifulSoup(html or "", "html.parser")
    return soup.get_text(" ", strip=True)


def find_matches(title, description, category):
    """Identify opportunities relevant to our portfolio."""
    text = f"{title} {description} {category}".lower()

    matches = []

    for keyword in KEYWORDS:
        if keyword.lower() == "ai":
            found = re.search(r"\bai\b", text)
        else:
            found = keyword.lower() in text

        if found:
            matches.append(keyword)

    return matches


def scrape_opportunities():

    print("=" * 55)
    print("       OPPORTUNITYAI - DATA COLLECTION")
    print("=" * 55)

    params = {
        "search": "data",
        "limit": 100
    }

    headers = {
        "User-Agent": "OpportunityAI/1.0"
    }

    try:
        response = requests.get(
            API_URL,
            params=params,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()
        jobs = data.get("jobs", [])

        print(f"Jobs received from Remotive: {len(jobs)}")

        opportunities = []

        for job in jobs:

            title = job.get("title", "")
            company = job.get("company_name", "")
            description = clean_html(
                job.get("description", "")
            )

            category = job.get("category", "")

            matches = find_matches(
                title,
                description,
                category
            )

            if matches:

                opportunities.append({
                    "Title": title,
                    "Company": company,
                    "Category": category,
                    "Location": job.get(
                        "candidate_required_location", "Not specified"
                    ),
                    "Job Type": job.get("job_type", "Not specified"),
                    "Salary": job.get("salary", "Not disclosed"),
                    "Published": job.get("publication_date", ""),
                    "Matched Skills": ", ".join(matches),
                    "Description": description[:500],
                    "Application Link": job.get("url", ""),
                    "Source": "Remotive"
                })

        print(f"Relevant opportunities found: {len(opportunities)}")

        if opportunities:

            df = pd.DataFrame(opportunities)

            df.to_csv(
                "opportunities.csv",
                index=False,
                encoding="utf-8-sig"
            )

            print("\nTOP MATCHING OPPORTUNITIES\n")

            for index, job in enumerate(opportunities[:15], 1):

                print(f"{index}. {job['Title']}")
                print(f"   Company: {job['Company']}")
                print(f"   Location: {job['Location']}")
                print(f"   Matching skills: {job['Matched Skills']}")
                print(f"   Apply: {job['Application Link']}")
                print("   Source: Remotive")
                print("-" * 55)

            print("\nCSV file successfully created!")

        else:
            print("No matching opportunities found.")

        print("\nCollection completed:", datetime.now(timezone.utc))

    except requests.RequestException as error:
        print("Website connection error:", error)

    except ValueError as error:
        print("Invalid API response:", error)


if __name__ == "__main__":
    scrape_opportunities()

