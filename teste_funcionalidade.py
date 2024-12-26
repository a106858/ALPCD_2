import re
import requests
from bs4 import BeautifulSoup
import typer
import json
from collections import Counter

app = typer.Typer()

# Função para buscar as skills de um trabalho específico
def get_skills_from_ambitionbox(job_title: str):
    # Formatar o título do trabalho para a URL
    job_title_formatted = job_title.replace(" ", "%20").lower()
    url = f"https://www.ambitionbox.com/jobs/search?tag={job_title_formatted}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0"
    }
    
    try:
        # Fazer o request com timeout de 10 segundos
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            typer.echo("Erro ao conectar-se ao website. Status Code:", response.status_code)
            return []
        
        # Parsear o HTML
        soup = BeautifulSoup(response.text, "lxml")
        
        # Encontrar as skills no HTML
        skills_section = soup.find_all("a", class_="skill-tag")
        
        # Extrair os nomes das skills
        skills = [skill.text.strip() for skill in skills_section]
        return skills
    
    except requests.exceptions.Timeout:
        typer.echo("O servidor não respondeu a tempo. A requisição excedeu o tempo limite.")
        return []
    
    except requests.exceptions.RequestException as e:
        # Captura outros erros como problemas de rede, DNS, etc
        typer.echo(f"Ocorreu um erro ao fazer a requisição: {e}")
        return []

@app.command()
def list_skills(job_title: str, export_csv: bool = False):
    """
    Lista as principais skills pedidas para um trabalho específico.
    """
    # Obter as skills
    skills = get_skills_from_ambitionbox(job_title)
    
    if not skills:
        typer.echo(f"Nenhuma skill encontrada para o trabalho: {job_title}")
        return
    
    # Contar as ocorrências
    skill_counts = Counter(skills).most_common(10)
    
    # Formatar para JSON
    skills_json = [{"skill": skill, "count": count} for skill, count in skill_counts]
    typer.echo(json.dumps(skills_json, indent=4))
    
    # Exportar para CSV, se solicitado
    if export_csv:
        with open(f"skills_{job_title.replace(' ', '_').lower()}.csv", "w") as f:
            f.write("Skill,Count\n")
            for skill, count in skill_counts:
                f.write(f"{skill},{count}\n")
        typer.echo(f"CSV exportado como skills_{job_title.replace(' ', '_').lower()}.csv")

if __name__ == "__main__":
    list_skills("Data Scientist", export_csv=True)