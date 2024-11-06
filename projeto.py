import requests
import typer
import json

url = "https://api.itjobs.pt/job/list.json?api_key=09ad1042ebaf1704533805cd2fab64f1"

headers = {
    "User-Agent":""
}

app = typer.Typer()

@app.command()
def search(location: str, company_name: str, num_jobs: int):
    response = requests.get(url,headers=headers)
    jobs = response.json().get('results', [])
    
    filtered_jobs = [
        job for job in jobs
        if job['company']['name'].lower() == company_name.lower() and
           any(loc['name'].lower() == location.lower() for loc in job['locations']) and
           any(t['name'].lower() == 'full-time' for t in job.get('types', []))
    ][:num_jobs]
    
    print(json.dumps(filtered_jobs, indent=4))

if __name__ == "__main__":
    app()
