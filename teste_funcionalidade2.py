import typer
import requests
from bs4 import BeautifulSoup
import json
from collections import Counter

# Definindo a instância do Typer para a CLI
app = typer.Typer()

# Headers a serem usados na requisição HTTP
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0'
}

# Função para buscar skills de um job específico
def get_skills_from_job(job_url: str):
    response = requests.get(job_url, headers=headers)
    response.raise_for_status()

    # Usando o BeautifulSoup para parsear o HTML da página do job
    soup = BeautifulSoup(response.text, 'html.parser')

    # Encontrar as tags de skills na página com a classe correta
    skills_elements = soup.find_all('a', class_='body-medium chip')

    # Extrair os nomes das skills
    skills = [skill.get_text(strip=True).lower() for skill in skills_elements]

    return skills

# Função para buscar os links dos jobs na página de busca
def get_job_urls(job_title: str):
    # Codificando o título do trabalho para ser utilizado na URL, substituindo espaços por '-'
    job_title = job_title.replace(" ", "-")
    url = f"https://www.ambitionbox.com/jobs/{job_title}-jobs-prf"

    # Fazendo a requisição HTTP para a página com os headers fornecidos
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # Usando o BeautifulSoup para parsear o HTML da página
    soup = BeautifulSoup(response.text, 'html.parser')

    # Encontrar os divs que contêm os links para os jobs
    job_elements = soup.find_all('div', class_='jobsInfoCardCont')

    # Extrair os URLs dos jobs
    job_urls = [f"https://www.ambitionbox.com{job.find('a')['href']}" for job in job_elements]

    return job_urls

# Função principal para buscar as skills de vários jobs
def get_skills(job_title: str):
    job_urls = get_job_urls(job_title)

    all_skills = []

    # Para cada URL de job, buscar as skills
    for url in job_urls:
        skills = get_skills_from_job(url)
        all_skills.extend(skills)

    # Contando as ocorrências das skills
    skill_count = Counter(all_skills)

    # Pegando as 10 skills mais comuns
    top_skills = skill_count.most_common(10)

    # Formatando a saída como uma lista de dicionários para JSON
    result = [{"skill": skill, "count": count} for skill, count in top_skills]

    return result

# Comando da CLI para listar as skills
@app.command()
def list_skills(job_title: str):
    """Comando para listar as skills mais pedidas para um trabalho."""
    try:
        skills = get_skills(job_title)
        # Exibindo a saída no formato JSON
        print(json.dumps(skills, indent=4))
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    app()
