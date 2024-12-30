import typer
import requests
from bs4 import BeautifulSoup
import json
import csv
from typing import Optional
from collections import Counter
import re

app = typer.Typer()

def export_to_csv2(data, export_csv: Optional[str]):
    if export_csv:
        try:
            with open(export_csv, mode='w', newline='', encoding='utf-8') as csv_file:
                fieldnames = data[0].keys()  # Pega as chaves do primeiro item na lista
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)

            print(f"Dados exportados para o arquivo CSV: {export_csv}")
        except Exception as e:
            print(f"Erro ao exportar dados para CSV: {e}")


def get_job_urls(job_title: str):
    job_title_formatted = re.sub(r'\s+', '-', job_title.lower())
    url = f"https://www.ambitionbox.com/jobs/{job_title_formatted}-jobs-prf"

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
    
    job_urls = []
    page = 1
    
    while page <= 10:
        paginated_url = f"{url}?page={page}"
        print(f"Fetching jobs from page {page}...")

        try:
            response = requests.get(paginated_url, headers=headers)
            if response.status_code != 200:
                print(f"Erro ao acessar a página {page}: {response.status_code}")
                break

            soup = BeautifulSoup(response.text, 'lxml')
            job_elements = soup.find_all('div', class_='jobsInfoCardCont')
            if not job_elements:
                print("Nenhum emprego encontrado na página atual. Finalizando...")
                break

            new_job_urls = [f"https://www.ambitionbox.com{job.find('a')['href']}" for job in job_elements]
            job_urls.extend(new_job_urls)
            print(f"Encontrados {len(new_job_urls)} empregos na página {page}. Total acumulado: {len(job_urls)} URLs.")

            page += 1

        except Exception as e:
            print(f"Erro ao processar a página {page}: {e}")
            print("Continuando com as URLs obtidas até agora.")

    print(f"Coleta finalizada. Total de URLs coletados: {len(job_urls)}")
                
    return job_urls


def get_skills_from_job(job_url: str):
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

    try:
        response = requests.get(job_url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        skills_elements = soup.find_all('a', class_='body-medium chip')
        skills = [skill.get_text(strip=True).lower() for skill in skills_elements]
        return skills
    except Exception as e:
        print(f"Erro ao obter habilidades do URL {job_url}: {e}")
        return []


@app.command()
def list_skills(job_title: str, export_csv: Optional[str] = None):
    try:
        job_urls = get_job_urls(job_title)

        all_skills = []

        for url in job_urls:
            skills = get_skills_from_job(url)
            all_skills.extend(skills)

        # Remover duplicatas e limpar dados
        all_skills = list(filter(None, all_skills))  # Remove elementos vazios
        skill_count = Counter(all_skills)

        # Top skills sem duplicatas
        top_skills = skill_count.most_common(10)

        result = [{"skill": skill, "count": count} for skill, count in top_skills]

        print(json.dumps(result, indent=4))

        # Exportar dados para CSV (opcional)
        export_to_csv2(result, export_csv)

    except Exception as e:
        print(f"Erro: {e}")


if __name__ == "__main__":
    list_skills("data scientist")
