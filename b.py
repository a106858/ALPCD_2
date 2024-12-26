import re
import requests
from bs4 import BeautifulSoup
import typer
import json
import csv
from collections import defaultdict

app = typer.Typer()

# função para obter a lista de trabalho da api do itjobs.pt
def get_api():
    url = "https://api.itjobs.pt/job/list.json?api_key=09ad1042ebaf1704533805cd2fab64f1"
    all_results = []
    page = 1
    total_results = 0

    while True:
        response = requests.get(f"{url}&page={page}", headers={"User-Agent": "Mozilla/5.0"})
        
        data = response.json()
        results = data.get("results", [])
        total = data.get("total", 0)
        total_results += len(results)

        if not results:
            break

        all_results.extend(results)
        page += 1

        if total_results >= total:
            break

    return {"results": all_results}

# função para contar ocorrências de um trabalho numa localização
def count_jobs_by_zone_and_type(jobs):
    count = defaultdict(lambda: defaultdict(int))

    for job in jobs:
        locations = job.get("locations", [])
        job_title = job.get("title", "Desconhecido")

        for location in locations:
            zone = location.get("name", "Desconhecida")
            count[zone][job_title] += 1

    return count

# função para exportar as contagens para um csv
@app.command()
def statistics(job_title: str = typer.Argument(None, help="Filtrar por tipo de trabalho")):
    data = get_api()
    jobs = data.get("results", [])

    count = count_jobs_by_zone_and_type(jobs)

    # criar csv
    with open('job_statistics.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Zona", "Tipo de Trabalho", "Nº de Vagas"])
        for zone, job_types in count.items():
            for job_type, number in job_types.items():
                writer.writerow([zone, job_type, number])

    typer.echo("Ficheiro de exportação criado com sucesso.")
    
    # dados do jobtitle solicitado (opcional)
    if job_title:
        typer.echo(f"Vagas para o trabalho '{job_title}':")
        filtered_jobs = []
        for zone, job_types in count.items():
            for job_type, number in job_types.items():
                if job_title.lower() in job_type.lower():
                    filtered_jobs.append((zone, job_type, number))
                    typer.echo(f"Zona: {zone}, Tipo de Trabalho: {job_type}, Nº de Vagas: {number}")
        
        if not filtered_jobs:
            typer.echo(f"Nenhuma vaga encontrada para o trabalho '{job_title}'.")

if __name__ == "__main__":
    app()
