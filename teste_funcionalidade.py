import requests
from collections import Counter
import json
import typer
from bs4 import BeautifulSoup

app = typer.Typer()

# Função para listar as principais skills de um trabalho
def list_skills(job_title: str):
    # Substituir espaços por hífens e converter para minúsculas
    formatted_job_title = job_title.lower().replace(' ', '-')
    
    # Criar o URL correto para a pesquisa de vagas
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

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    # Extrair skills da página
    skills_elements = soup.find_all('div', class_='show-flex chips-cont')
    skills = [skill.get_text(strip=True) for skill in skills_elements]

    # Contar a frequência de cada skill
    skills_count = Counter(skills).most_common(10)

    # Formatar em JSON
    skills_json = [{"skill": skill, "count": count} for skill, count in skills_count]

    print(json.dumps(skills_json, indent=4))
