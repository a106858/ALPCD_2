import re
import requests
from bs4 import BeautifulSoup
import typer
import json
import csv
from collections import defaultdict

app = typer.Typer()

# função para obter a lista de trabalho da api do itjobs.pt
def get_api():
    url = "https://api.itjobs.pt/job/list.json?api_key=09ad1042ebaf1704533805cd2fab64f1"
    all_results = []
    page = 1
    total_results = 0

    while True:
        response = requests.get(f"{url}&page={page}", headers={"User-Agent": "Mozilla/5.0"})
        
        data = response.json()
        results = data.get("results", [])
        total = data.get("total", 0)
        total_results += len(results)

        if not results:
            break

        all_results.extend(results)
        page += 1

        if total_results >= total:
            break

    return {"results": all_results}

# função para obter o id da empresa relativo ao jobid pedido
def find_company_name(job_id):
    data = get_api()
    jobs = data.get("results", [])
    
    for job in jobs:
        if job["id"] == job_id:
            # retornar o nome da empresa associada ao job_id
            company_name = job["company"]["name"]
            return company_name
    return None

# função para obter o html da empresa do website ambitionbox.com
def get_html(job_id):
    company_name = find_company_name(job_id)
    if company_name is None:
        print(f"Empresa não encontrada para o job ID {job_id}.")
        return

    company_name1 = company_name.lower()
    company_name2 = re.sub(r'\s+', '-', company_name1)
    
    url = f"https://www.ambitionbox.com/overview/{company_name2}-overview"
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0", 
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8", 
               "Accept-Language": "en-US,en;q=0.5", 
               "Accept-Encoding": "gzip, deflate", 
               "Connection": "keep-alive", 
               "Upgrade-Insecure-Requests": "1", 
               "Sec-Fetch-Dest": "document", 
               "Sec-Fetch-Mode": "navigate", 
               "Sec-Fetch-Site": "none", 
               "Sec-Fetch-User": "?1", 
               "Cache-Control": "max-age=0"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200: 
        print(f"Website não encontrado para a empresa: {company_name}.")
        return None
    
    soup = BeautifulSoup(response.text, 'lxml')
    
    return soup

# função para obter o conteúdo do trabalho em formato json através da api
def get_api_content(job_id):
    data = get_api()
    jobs = data.get("results", [])
    
    for job in jobs:
        if job["id"] == job_id:
            api_data = {
                "id": job.get("id", "N/A"),
                "title": job.get("title", "N/A"),
                "company": job.get("company", {}).get("name", "N/A"),
            }
            return api_data
    return None

# função para obter o conteúdo da empresa em formato json através do html
def get_html_content(soup):
    if soup is None:
        return {
            "overall_rating": "N/A",
            "description": "Informações indisponíveis.",
            "benefits": {
                "work_policy": "Informações indisponíveis",
                "top_employees_benefits": "Informações indisponíveis",
            }
        }

    body = soup.find('body')
    if not body:
        return {
            "overall_rating": "N/A",
            "description": "Informações indisponíveis.",
            "benefits": {
                "work_policy": "Informações indisponíveis",
                "top_employees_benefits": "Informações indisponíveis",
            }
        }

    # encontrar o overall rating
    overall_rating_tag = body.find('span', class_="css-1jxf684 text-primary-text font-pn-700 text-[32px] leading-[32px]")
    overall_rating = overall_rating_tag.text if overall_rating_tag else "N/A"

    # encontrar a descrição da empresa
    description1 = body.find('div', dir="auto", class_="css-146c3p1 font-pn-400 text-sm text-neutral mb-2")
    description2 = body.find('div', class_="text-sm font-pn-400 [&_ul]:list-disc [&_ol]:list-[auto] [&_ul]:ml-5 [&_ol]:ml-5")
    description = (description1.text.strip() if description1 else "") + " " + (description2.find('p').text.strip() if description2 and description2.find('p') else "")
    description = description.strip() if description else "Informações indisponíveis"
    
    # encontrar os principais benefícios
    benefits_here = body.find_all('div', class_="css-175oi2r border relative rounded-md border-card-border bg-white p-4 flex flex-col gap-3 md:gap-4")
    work_policy = ["Informações indisponíveis"]
    top_employees_benefits = ["Informações indisponíveis"]
    if len(benefits_here) > 0:
        work_policy_here = benefits_here[0].find_all('div', dir="auto", class_="css-146c3p1 font-pn-400 text-sm text-primary-text")
        work_policy = [wp.text for wp in work_policy_here] if work_policy_here else ["Informações indisponíveis"]
    if len(benefits_here) > 1:
        top_employees_benefits_here = benefits_here[1].find_all('div', class_="css-146c3p1 font-pn-400 text-sm text-primary-text")
        top_employees_benefits = [tb.text for tb in top_employees_benefits_here] if top_employees_benefits_here else ["Informações indisponíveis"]
    benefits = f"work_policy: {', '.join(work_policy)}" + "; " + f"top_employees_benefits: {', '.join(top_employees_benefits)}"

    html_data = {
        "overall_rating": overall_rating,
        "description": description,
        "benefits": benefits
    }
    return html_data

# função para juntar todas as informações
@app.command()
def informations(job_id: int):
    api_data = get_api_content(job_id)
    if api_data is None:
        print(f"Job com ID {job_id} não encontrado na API.")
        return
    soup = get_html(job_id)
    html_content = get_html_content(soup)

    data = {**api_data, **html_content}

    print(json.dumps(data, indent=4))

# função para contar ocorrências de um trabalho numa localização
def count_jobs_by_zone_and_type(jobs):
    count = defaultdict(lambda: defaultdict(int))

    for job in jobs:
        locations = job.get("locations", [])
        job_title = job.get("title", "Desconhecido")

        for location in locations:
            zone = location.get("name", "Desconhecida")
            count[zone][job_title] += 1

    return count

# função para exportar as contagens para um csv
@app.command()
def statistics(job_title: str = typer.Argument(None, help="Filtrar por tipo de trabalho")):
    data = get_api()
    jobs = data.get("results", [])

    count = count_jobs_by_zone_and_type(jobs)

    # criar csv
    with open('job_statistics.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Zona", "Tipo de Trabalho", "Nº de Vagas"])
        for zone, job_types in count.items():
            for job_type, number in job_types.items():
                writer.writerow([zone, job_type, number])

    typer.echo("Ficheiro de exportação criado com sucesso.")
    
    # dados do jobtitle solicitado (opcional)
    if job_title:
        typer.echo(f"Vagas para o trabalho '{job_title}':")
        filtered_jobs = []
        for zone, job_types in count.items():
            for job_type, number in job_types.items():
                if job_title.lower() in job_type.lower():
                    filtered_jobs.append((zone, job_type, number))
                    typer.echo(f"Zona: {zone}, Tipo de Trabalho: {job_type}, Nº de Vagas: {number}")
        
        if not filtered_jobs:
            typer.echo(f"Nenhuma vaga encontrada para o trabalho '{job_title}'.")

if __name__ == "__main__":
    app()
