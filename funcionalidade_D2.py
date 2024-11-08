import typer
import requests
import json
import re

app = typer.Typer()

API_KEY = "09ad1042ebaf1704533805cd2fab64f1"
BASE_URL = "https://api.itjobs.pt/job/list.json"
headers = {"User-Agent": ""}

@app.command()
def skills(
    skills: str = typer.Argument(..., help="Lista de skills separadas por vírgulas, por exemplo: python,django,sql")
):
    """
    Mostra os trabalhos que requerem uma lista de skills específica.
    """
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
                "skills": skill_list,
                "publishedAt": job.get("publishedAt"),
                "locations": [location.get("name") for location in job.get("locations", [])],
                "allowRemote": job.get("allowRemote"),
                "wage": job.get("wage"),
                "types": [job_type.get("name") for job_type in job.get("types", [])],
            }
            filtered_jobs.append(job_data)

    # Exibe o resultado em JSON formatado
    typer.echo(json.dumps(filtered_jobs, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    app()
