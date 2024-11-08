<<<<<<< HEAD
import typer
import requests
import re

app = typer.Typer()

# A URL da API que contém todos os jobs
API_URL = "https://api.itjobs.pt/job/list.json?api_key=09ad1042ebaf1704533805cd2fab64f1"
headers = {"User-Agent":""}

def fetch_job_details():
    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        jobs = response.json().get("results", [])
        return jobs
    except requests.exceptions.RequestException as e:
        typer.echo(f"Erro ao buscar dados da API: {e}")
        raise typer.Exit()

def extract_wage(job_data):
    # Tenta pegar o valor direto do campo 'wage'
    wage = job_data.get("wage")
    if wage:
        return f"Salário encontrado no campo específico: {wage}"

    # Se wage for nulo, tenta encontrar um valor no campo 'body' usando expressões regulares
    body_text = job_data.get("body", "")
    salary_patterns = re.findall(r"€?\d{3,5}(?:\s?(?:euros|EUR|€))?", body_text, re.IGNORECASE)

    if salary_patterns:
        return f"Salário encontrado no campo 'body': {', '.join(salary_patterns)}"
    
    return "Salário não encontrado em nenhum campo."

@app.command()
def get_salary(job_id: int):
    """
    Obtém o salário oferecido para o job especificado pelo job_id.
    """
    typer.echo(f"Buscando salário para o job ID: {job_id}...")
    jobs = fetch_job_details()

    # Procurar o trabalho pelo job_id
    job_data = next((job for job in jobs if job["id"] == job_id), None)
    
    if job_data:
        wage_info = extract_wage(job_data)
        typer.echo(wage_info)
    else:
        typer.echo(f"Job ID {job_id} não encontrado.")
        raise typer.Exit()

if __name__ == "__main__":
    app()
=======
import typer
import requests
import re

app = typer.Typer()

# A URL da API que contém todos os jobs
API_URL = "https://api.itjobs.pt/job/list.json?api_key=09ad1042ebaf1704533805cd2fab64f1"
headers = {"User-Agent":""}

def fetch_job_details():
    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        jobs = response.json().get("results", [])
        return jobs
    except requests.exceptions.RequestException as e:
        typer.echo(f"Erro ao buscar dados da API: {e}")
        raise typer.Exit()

def extract_wage(job_data):
    # Tenta pegar o valor direto do campo 'wage'
    wage = job_data.get("wage")
    if wage:
        return f"Salário encontrado no campo específico: {wage}"

    # Se wage for nulo, tenta encontrar um valor no campo 'body' usando expressões regulares
    body_text = job_data.get("body", "")
    salary_patterns = re.findall(r"€?\d{3,5}(?:\s?(?:euros|EUR|€))?", body_text, re.IGNORECASE)

    if salary_patterns:
        return f"Salário encontrado no campo 'body': {', '.join(salary_patterns)}"
    
    return "Salário não encontrado em nenhum campo."

@app.command()
def get_salary(job_id: int):
    """
    Obtém o salário oferecido para o job especificado pelo job_id.
    """
    typer.echo(f"Buscando salário para o job ID: {job_id}...")
    jobs = fetch_job_details()

    # Procurar o trabalho pelo job_id
    job_data = next((job for job in jobs if job["id"] == job_id), None)
    
    if job_data:
        wage_info = extract_wage(job_data)
        typer.echo(wage_info)
    else:
        typer.echo(f"Job ID {job_id} não encontrado.")
        raise typer.Exit()

if __name__ == "__main__":
    app()
>>>>>>> 4e9c63adb5ad5e7276b5cded9e11aebfb984bb49
