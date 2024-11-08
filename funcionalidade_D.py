import typer
import requests
import json
from datetime import datetime

app = typer.Typer()

API_KEY = "09ad1042ebaf1704533805cd2fab64f1"
BASE_URL = "https://api.itjobs.pt/job/list.json"
headers = {"User-Agent":""}


@app.command()
def skills(
    skills: str = typer.Argument(..., help="Lista de skills separadas por vírgulas, por exemplo: python,django,sql"),
    start_date: str = typer.Argument(..., help="Data inicial no formato YYYY-MM-DD"),
    end_date: str = typer.Argument(..., help="Data final no formato YYYY-MM-DD")
):
    """
    Mostra os trabalhos que requerem uma lista de skills específica em um período de tempo.
    """
    # Processa a lista de skills
    skill_list = skills.split(',')
    skills_query = ','.join(skill_list)

    # Validação e conversão das datas
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        typer.echo("As datas devem estar no formato YYYY-MM-DD.")
        raise typer.Exit()

    # Parâmetros da requisição
    params = {
        'api_key': API_KEY,
        'skills': skills_query,
    }

    # Realiza a requisição para a API
    try:
        response = requests.get(BASE_URL, params=params,headers=headers)
        response.raise_for_status()
        jobs = response.json().get("results", [])
    except requests.RequestException as e:
        typer.echo(f"Erro ao conectar com a API: {e}")
        raise typer.Exit()

    # Filtra manualmente os resultados pelo intervalo de datas
    filtered_jobs = [
        job for job in jobs
        if 'publishedAt' in job and start_dt <= datetime.strptime(job['publishedAt'], '%Y-%m-%d %H:%M:%S') <= end_dt
    ]

    # Exibe o resultado filtrado em JSON formatado
    typer.echo(json.dumps(filtered_jobs, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    app()