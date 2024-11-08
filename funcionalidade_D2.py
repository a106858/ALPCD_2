import typer
import requests
import json
import re
import csv
from typing import Optional

app = typer.Typer()

API_KEY = "09ad1042ebaf1704533805cd2fab64f1"
BASE_URL = "https://api.itjobs.pt/job/list.json"
headers = {"User-Agent": ""}

@app.command()
def skills(
    skill_check: str,
    skills: str = typer.Argument(..., help="Lista de skills separadas por vírgulas, por exemplo: python,django,sql"),
    export_csv: Optional[str] = typer.Option(None, help="Caminho para exportar o resultado em um arquivo CSV")
):
    """
    Mostra os trabalhos que requerem uma lista de skills específica e exporta para CSV se solicitado.
    """
    if skill_check == "skills": 
        # Processa a lista de skills
        skill_list = [skill.strip() for skill in skills.split(',')]
        skills_query = ','.join(skill_list)

        # Parâmetros da requisição
        params = {
            'api_key': API_KEY,
            'skills': skills_query,
        }

        # Realiza a requisição para a API
        try:
            response = requests.get(BASE_URL, params=params, headers=headers)
            response.raise_for_status()
            jobs = response.json().get("results", [])
        except requests.RequestException as e:
            typer.echo(f"Erro ao conectar com a API: {e}")
            raise typer.Exit()

        # Filtra os trabalhos que contêm as skills especificadas no corpo da descrição
        filtered_jobs = []
        for job in jobs:
            job_description = job.get("body", "").lower()
            if all(re.search(rf'\b{skill.lower()}\b', job_description) for skill in skill_list):
                job_data = {
                    "id": job.get("id"),
                    "title": job.get("title"),
                    "company": job.get("company", {}).get("name"),
                    "description": job.get("body"),
                    "publishedAt": job.get("publishedAt"),
                    "wage": job.get("wage"),
                    "locations": [location.get("name") for location in job.get("locations", [])],
                }
                filtered_jobs.append(job_data)

        # Exibe o resultado em JSON formatado
        typer.echo(json.dumps(filtered_jobs, indent=2, ensure_ascii=False))

        # Exporta para CSV, se solicitado
        if export_csv:
            try:
                with open(export_csv, mode="w", newline="", encoding="utf-8") as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(["titulo", "empresa", "descricao", "data de publicacao", "salario", "localizacao"])
                    for job in filtered_jobs:
                        writer.writerow([
                            job["title"],
                            job["company"],
                            job["description"],
                            job["publishedAt"],
                            job["wage"],
                            "; ".join(job["locations"])  # Concatena várias localizações em uma única string
                        ])
                typer.echo(f"Resultados exportados para o arquivo CSV: {export_csv}")
            except IOError as e:
                typer.echo(f"Erro ao salvar o arquivo CSV: {e}")

if __name__ == "__main__":
    app()
