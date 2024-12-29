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

# Função para buscar skills de um determinado trabalho
def get_skills(job_title: str):
    # Codificando o título do trabalho para ser utilizado na URL, substituindo espaços por '-'
    job_title = job_title.replace(" ", "-")
    url = f"https://www.ambitionbox.com/jobs/search?tag={job_title}"

    # Fazendo a requisição HTTP para a página com os headers fornecidos
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # Usando o BeautifulSoup para parsear o HTML da página
    soup = BeautifulSoup(response.text, 'html.parser')

    # Encontrar as tags de skills na página com a classe correta
    skills_elements = soup.find_all('a', class_='body-medium chip')
    
    # Extrair os nomes das skills
    skills = [skill.get_text(strip=True).lower() for skill in skills_elements]

    # Contando as ocorrências das skills
    skill_count = Counter(skills)

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
