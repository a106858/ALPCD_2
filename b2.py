import re
import requests
from bs4 import BeautifulSoup
import typer
import json
import csv
import os

app = typer.Typer()

# função para obter a lista de trabalho da api do itjobs.pt
def get_api():
    all_results = []
    url = "https://api.itjobs.pt/job/list.json?api_key=09ad1042ebaf1704533805cd2fab64f1"
    page = 1

    while page <= 10:  # Limite de 10 páginas
        response = requests.get(f"{url}&page={page}", headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            print(f"Erro ao acessar a API: {response.status_code}")
            break

        data = response.json()
        results = data.get("results", [])
        if not results:
            break

        all_results.extend(results)
        page += 1

        if len(results) < data.get("limit", 50):  # Finaliza se menos resultados que o limite
            break

    return {"results": all_results}

def process_jobs(jobs):
    job_groups = {}
    
    for job in jobs:
        locations = job.get('locations', [])
        if not locations:
            continue
        
        locations = [loc.get('name') for loc in locations]
        
        for location in locations:
            key = f"{location}_{job.get('title', '')}"
            if key not in job_groups:
                job_groups[key] = {"Zona": location, "Tipo de Trabalho": job['title'], "Nº de vagas": 0}
            
            #job_groups[key]["Nº de vagas"] += 1
    
    return list(job_groups.values())

def main():
    jobs = get_api()["results"]
    processed_jobs = process_jobs(jobs)
    
    with open("vagas_por_tipo_e_regiao.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["Zona", "Tipo de Trabalho", "Nº de vagas"])
        writer.writeheader()
        for job in processed_jobs:
            writer.writerow(job)


    print("CSV file generated successfully!")

if __name__ == "__main__":
    main()
