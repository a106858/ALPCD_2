import requests
from collections import Counter
import json
import typer
from bs4 import BeautifulSoup

app = typer.Typer()

# Function to list the main skills for a job
def list_skills(job_title: str):
    # Replace spaces with hyphens and convert to lowercase
    formatted_job_title = job_title.lower().replace(' ', '-')
    
    # Create the correct URL for the job search
    url = f"https://www.ambitionbox.com/jobs/{formatted_job_title}-jobs-prf"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        soup = BeautifulSoup(response.text, 'lxml')

        # Extract skills from the page
        skills_elements = soup.select('div.ab_checkbox label div.text-wrap span.label')  # Updated selector
        counts_elements = soup.select('div.ab_checkbox label div.text-wrap span:nth-of-type(2)')  # For counts

        if not skills_elements:
            print("No skills found. Please verify the page structure.")
            return

        # Parse skills and counts
        skills = [skill.get_text(strip=True) for skill in skills_elements]
        counts = [int(count.get_text(strip=True).strip('()')) for count in counts_elements]

        # Combine skills with counts
        skills_data = list(zip(skills, counts))

        # Count the frequency of each skill (if needed)
        skills_json = [{"skill": skill, "count": count} for skill, count in skills_data]

        print(json.dumps(skills_json, indent=4))
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    typer.run(list_skills)
