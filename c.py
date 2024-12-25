
import re
import requests
from bs4 import BeautifulSoup
import typer
import json
from collections import Counter

app = typer.Typer()

# Função para obter a lista de trabalho da API do itjobs.pt
def get_api():
    url = "https://api.itjobs.pt/job/list.json?api_key=09ad1042ebaf1704533805cd2fab64f1"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    return response.json()

# Função para obter o id da empresa relativo ao jobid pedido
def find_company_name(job_id):
    data = get_api()
    jobs = data.get("results", [])

    for job in jobs:
        if job["id"] == job_id:
            # Retornar o nome da empresa associada ao job_id
            company_name = job["company"]["name"]
            return company_name
    return None

# Função para obter o HTML da empresa do website ambitionbox.com
def get_html(job_id):
    company_name = find_company_name(job_id)
    if company_name is None:
        print(f"Empresa não encontrada para o job ID {job_id}.")
        return

    company_name1 = company_name.lower()
    company_name2 = re.sub(r'\s+', '-', company_name1)

    url = f"https://www.ambitionbox.com/overview/{company_name2}-overview"

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

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    return soup

# Função para listar as principais skills de um trabalho
def list_skills(job_title: str):
    job_title_formatted = re.sub(r'\s+', '%20', job_title.lower())
    url = f"https://www.ambitionbox.com/jobs/search?tag={job_title_formatted}"

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

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    # Extrair skills da página
    skills_elements = soup.find_all('span', class_='skill-text')
    skills = [skill.get_text(strip=True) for skill in skills_elements]

    # Contar a frequência de cada skill
    skills_count = Counter(skills).most_common(10)

    # Formatar em JSON
    skills_json = [{"skill": skill, "count": count} for skill, count in skills_count]

    print(json.dumps(skills_json, indent=4))

# Adicionar comando à CLI
@app.command()
def list_skills_cli(job_title: str):
    """Listar as principais skills para um trabalho."""
    list_skills(job_title)

if __name__ == "__main__":
    app()
