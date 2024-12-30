import re
import requests
from bs4 import BeautifulSoup
import typer
import json
import webbrowser
import csv
from collections import defaultdict
from typing import Optional
from collections import Counter

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

# função para criar html
def create_html(data_html):    

    contacts = ""
    if data_html['phone'] != "N/A":
        contacts += f"<p>Phone: {data_html['phone']}</p>\n"
    if data_html['email'] != "N/A":
        contacts += f"<p>Email: {data_html['email']}</p>\n"
    if data_html['url'] != "N/A":
        contacts += f"<p>URL: {data_html['url']}</p>\n"

    benefits = data_html['benefits']
    benefits_split = benefits.split("; ")
    work_policy = benefits_split[0].replace("work_policy: ", "Work Policy: ")
    top_employees_benefits = benefits_split[1].replace("top_employees_benefits: ", "Top Employees Benefits: ")

    html_content = f"""
    <!DOCTYPE html>
    <html lang=\"pt\">
    <head>
        <meta charset=\"UTF-8\">
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
        <title>{data_html['title']} at {data_html['company']}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2, h3 {{ color: #2c3e50; }}
            .company {{ display: flex; align-items: center; gap: 15px; }}
            .rating {{ font-size: 18px; margin-top: 5px; }}
            .section {{ margin-top: 30px; }}
            .section h3 {{ border-bottom: 2px solid #e1e1e1; padding-bottom: 5px; }}
        </style>
    </head>
    <body>
        <h1>{data_html['title']}</h1>
        <div class=\"section\">
            <h2>{data_html['company']}</h2>
            <p class=\"rating\">Overall rating: {data_html['overall_rating']}</p>
        </div>
        <div class=\"section\">
            <h3>Description</h3>
            <p>{data_html['description']}</p>
        </div>
        <div class=\"section\">
            <h3>Benefits</h3>
            <p>{work_policy}</p>
            <p>{top_employees_benefits}</p>
        </div>
        <div class=\"section\">
            <h3>Contacts</h3>
            {contacts}
        </div>
    </body>
    </html>
    """

    # guardar o ficheiro html
    file_name = "job_information.html"
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(html_content)

    return file_name

# função para exportar para csv
def export_to_csv(data, export_csv: Optional[str]):
    if export_csv:
        try:
            with open(export_csv, mode='w', newline='', encoding='utf-8') as csv_file:
                if isinstance(data, dict):
                    # caso de dados simples 
                    fieldnames = data.keys()
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerow(data)
                elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
                    # caso de lista de dicionários 
                    fieldnames = data[0].keys() if data else []
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
                else:
                    raise ValueError("Formato de dados não suportado para exportação.")

            print(f"Dados exportados para o arquivo CSV: {export_csv}")
        
        except Exception as e:
            print(f"Erro ao exportar dados para CSV: {e}")

# função para juntar todas as informações
@app.command()
def informations(
    job_id: int, 
    export_csv: Optional[str] = typer.Option(None, help="Exporta os dados para um arquivo CSV"), 
    generate_html: bool = typer.Option(False, help="Cria e abre o HTML com as informações.")
):
    api_data = get_api_content(job_id)
    if api_data is None:
        print(f"Job com ID {job_id} não encontrado na API.")
        return
    soup = get_html(job_id)
    html_content = get_html_content(soup)

    data = {**api_data, **html_content}
    print(json.dumps(data, indent=4))
    
    # exportar dados para csv (opcional)
    if export_csv:
        export_to_csv(data, export_csv)
    
    # criação do html solicitado (opcional)
    if generate_html:
        
        api = get_api()
        jobs = api.get("results", [])
        for job in jobs:
            if job["id"] == job_id:
                contacts = {
                    "phone": job.get("company", {}).get("phone", "N/A"),
                    "email": job.get("company", {}).get("email", "N/A"),
                    "url": job.get("company", {}).get("url", "N/A"),
                }
        
        data_html = {**data, **contacts}
        
        file_name = create_html(data_html)
        print(f"Página HTML criada: {file_name}")
        webbrowser.open(file_name)

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
def statistics(
    job_title: str = typer.Argument(None, help="Mostrar as vagas de um tipo de trabalho")
):
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
        filtered_jobs = [
            (zone, job_type, number)
            for zone, job_types in count.items()
            for job_type, number in job_types.items()
            if job_title.lower() in job_type.lower()
        ]

        if filtered_jobs:
            typer.echo(f"Vagas para o trabalho '{job_title}':")
            for zone, job_type, number in filtered_jobs:
                typer.echo(f"Zona: {zone}, Tipo de Trabalho: {job_type}, Nº de Vagas: {number}")
        else:
            typer.echo(f"Nenhuma vaga encontrada para o trabalho '{job_title}'.")

# função para ir buscar os links dos jobs na página
def get_job_urls(job_title: str):
    job_title_formatted = re.sub(r'\s+', '-', job_title.lower())
    url = f"https://www.ambitionbox.com/jobs/{job_title_formatted}-jobs-prf"

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
    
    job_urls = []
    page = 1
    
    while page <= 100:
        paginated_url = f"{url}?page={page}"

        try:
            response = requests.get(paginated_url, headers=headers)
            if response.status_code != 200:
                break

            soup = BeautifulSoup(response.text, 'lxml')
            job_elements = soup.find_all('div', class_='jobsInfoCardCont')
            if not job_elements:
                break

            new_job_urls = [f"https://www.ambitionbox.com{job.find('a')['href']}" for job in job_elements]
            job_urls.extend(new_job_urls)

            page += 1

        except Exception as e:
            pass
    
    print(f"Total de URLs: {len(job_urls)}")
                        
    return job_urls

# função para encontrar skills de um job específico
def get_skills_from_job(job_url: str):
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

    try:
        response = requests.get(job_url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        
        skills_elements = soup.find_all('a', class_='body-medium chip')
        skills = [skill.get_text(strip=True).lower() for skill in skills_elements]
        
        return skills
    
    except Exception as e:
        print(f"Erro ao obter habilidades do URL {job_url}: {e}")
        
        return []

# função para listar as principais skills de um trabalho
@app.command()
def list_skills(job_title: str, export_csv: Optional[str] = None):
    try:
        job_urls = get_job_urls(job_title)

        all_skills = []

        for url in job_urls:
            skills = get_skills_from_job(url)
            all_skills.extend(skills)

        all_skills = list(filter(None, all_skills))
        skill_count = Counter(all_skills)

        top_skills = skill_count.most_common(10)

        result = [{"skill": skill, "count": count} for skill, count in top_skills]

        print(json.dumps(result, indent=4))

        # exportar dados para csv (opcional)
        export_to_csv(result, export_csv)

    except Exception as e:
        print(f"Erro: {e}")

# função para obter o html da empresa do website indeed.com
def get_html2(job_id):
    company_name = find_company_name(job_id)
    if company_name is None:
        print(f"Empresa não encontrada para o job ID {job_id}.")
        return
    
    company_name1 = re.sub(r'\s+', '-', company_name)
    print(company_name1)
    url = f"https://pt.indeed.com/cmp/{company_name1}"
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
               "Accept-Language": "pt-PT,pt;q=0.9,pt-BR;q=0.8,en;q=0.7,en-US;q=0.6,en-GB;q=0.5",
               "Accept-Encoding": "gzip, deflate, br, zstd",
               "Cache-Control": "max-age=0",
               "Sec-Fetch-Dest": "document", 
               "Sec-Fetch-Mode": "navigate", 
               "Sec-Fetch-Site": "cross-site", 
               "Sec-Fetch-User": "?1"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200: 
        print(f"Website não encontrado para a empresa: {company_name}.")
        return None
    
    soup = BeautifulSoup(response.text, 'lxml')
    
    return soup

# função para obter o conteúdo da empresa em formato json através do html
def get_html_content2(soup):
    if soup is None:
        return {
            "overall_rating": "N/A",
            "description": "Informações indisponíveis.",
        }

    body = soup.find('body')

    if not body:
        return {
            "overall_rating": "N/A",
            "description": "Informações indisponíveis.",
        }
    
    # encontrar o overall rating
    overall_rating = body.find('span', attrs={"aria-hidden":"true"}, class_="css-4f2law e1wnkr790").text  
    overall_rating_1 = overall_rating.text if overall_rating else "N/A"

    # encontrar a descrição da empresa
    description_div = body.find('div', attrs={"data-testid": "less-text", "class": "css-9146s eu4oa1w0"})     # em alguns casos é more_text, alterar
    if description_div:
        paragraphs = description_div.find_all('p')
        description = " ".join(p.text for p in paragraphs)
    else:
        description = "Informações indisponíveis."
    
    html_data = {
        "overall_rating": overall_rating_1,
        "description": description,        
    }
    return html_data

# função para juntar todas as informações
@app.command()
def informations2(
    job_id: int, 
    export_csv: Optional[str] = typer.Option(None, help="Exporta os dados para um arquivo CSV"),
):
    api_data = get_api_content(job_id)
    if api_data is None:
        print(f"Job com ID {job_id} não encontrado na API.")
        return
    soup = get_html2(job_id)
    html_content = get_html_content2(soup)

    data = {**api_data, **html_content}
    print(json.dumps(data, indent=4))
    
    # exportar dados para csv (opcional)
    if export_csv:
        export_to_csv(data, export_csv)

if __name__ == "__main__":
    app()
