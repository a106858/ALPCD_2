import typer
import re
import requests
import json
import csv
from datetime import datetime
from collections import defaultdict
from typing import Optional
from fpdf import FPDF
from bs4 import BeautifulSoup
import webbrowser
from collections import Counter


app = typer.Typer()


# função para obter a lista de trabalho da api do itjobs.pt
def get_api():
    url = "https://api.itjobs.pt/job/list.json?api_key=09ad1042ebaf1704533805cd2fab64f1"
    headers = {"User-Agent": "Mozilla/5.0"}
    all_results = []
    page = 1
    total_results = 0

    while True:
        response = requests.get(f"{url}&page={page}", headers=headers)
        
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


"""TP1"""

# função para limpar o html da descrição
def limpar_html(texto_html):
    texto_limpo = re.sub(r"<br\s*/?>", " ", texto_html)  # substitui <br> por espaço
    texto_limpo = re.sub(r"</?p>", " ", texto_limpo)  # substitui <p> por espaço
    texto_limpo = re.sub(r"</?strong>", "", texto_limpo)  # remove <strong> e </strong>
    texto_limpo = re.sub(r"</?a[^>]*>", "", texto_limpo)  # remove tags <a> (links)
    texto_limpo = re.sub(r"<[^>]+>", "", texto_limpo)  # remove qualquer outra tag HTML restante
    texto_limpo = re.sub(r"\n\s*\n", " ", texto_limpo).strip()  # substitui múltiplas quebras de linha por espaço
    return texto_limpo

# função de exportação para csv
def export_to_csv1(data, export_csv: Optional[str]):
    if export_csv:
        try:
            with open(export_csv, mode="w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                # Cabeçalho para CSV
                writer.writerow(["Título", "Empresa", "Descrição", "Data de Publicação", "Salário", "Localização"])
                for item in data:
                    titulo = item.get("title", "N/A")
                    empresa = item.get("company", {}).get("name", "N/A")
                    descricao = limpar_html(item.get("body", "N/A"))
                    data_publicacao = item.get("publishedAt", "N/A")
                    salario = item.get("wage", "N/A")
                    localizacao = "; ".join([loc["name"] for loc in item.get("locations", [])])
                    
                    writer.writerow([titulo, empresa, descricao, data_publicacao, salario, localizacao])
            print(f"Resultados exportados para o arquivo CSV: {export_csv}")
            
        except IOError as e:
            print(f"Erro ao salvar o arquivo CSV: {e}")

# função para listar n trabalhos mais recentes
@app.command()
def listar_trabalhos(
    n: int = typer.Argument(10, help="Número de trabalhos para listar"),
    export_csv: Optional[str] = typer.Option(None, help="Exporta os dados para um arquivo CSV")
):
    data = get_api()
    jobs = data.get("results", [])
    
    jobs_sorted = sorted(jobs, key=lambda job: datetime.strptime(job["publishedAt"], "%Y-%m-%d %H:%M:%S"), reverse=True)
    
    # seleciona os n trabalhos mais recentes
    jobs_most_recent = jobs_sorted[:n]
    print(json.dumps(jobs_most_recent, ensure_ascii=False, indent=2))
    
    # exporta para csv se solicitado
    export_to_csv1(jobs_most_recent, export_csv)

# função para listar todos os trabalhos do tipo full-time, publicados por uma determinada empresa, numa determinada localidade
@app.command()
def full_time_jobs(
    company_name: str = typer.Argument(..., help="Nome da empresa desejada"),
    location: str = typer.Argument(..., help="Localização da empresa"),
    limit: int = typer.Argument(1, help="Número máximo de resultados a exibir"),
    export_csv: Optional[str] = typer.Option(None, help="Exporta os dados para um arquivo CSV")
):
    data = get_api()
    jobs = data.get("results", [])
    
    company_name = company_name.lower()
    location = location.lower()

    companies_result = []

    for item in jobs:
        company_name_json = (item["company"]["name"]).lower()
        
        # verifica se o nome da empresa corresponde
        if company_name_json == company_name:
            # verifica se há "Full-time" em `types` e se a localização desejada existe em `locations`
            full_time = any(t["name"] == "Full-time" for t in item.get("types", []))
            location_match = any(l["name"].lower() == location for l in item.get("locations", []))
            
            if full_time and location_match:
                companies_result.append({
                    "id": item["id"],
                    "title": item["title"],
                    "company": item.get("company", {}),
                    "body": limpar_html(item["body"]),
                    "publishedAt": item.get("publishedAt"),
                    "wage": item.get("wage"),
                    "locations": item.get("locations", []),
                })
    
    # aplica o limite de resultados desejado
    companies_result = companies_result[:limit]

    if companies_result:
        print(json.dumps(companies_result, indent=4, ensure_ascii=False))
        
        # exporta para csv se solicitado
        if export_csv:
            export_to_csv1(companies_result, export_csv)
    else:
        print(f"Não existe nenhum trabalho do tipo 'Full-time' com localização '{location}', encontrado para '{company_name}'.")

# função para mostrar os trabalhos que permitem trabalho remoto num determinado distrito
@app.command()
def remote_jobs(
    location_: str = typer.Argument(..., help="Localização da empresa"),
    contract_: str = typer.Argument(..., help="Tipo de contrato desejado"),
):
    data = get_api()
    jobs = data.get("results", [])

    location_ = location_.lower()
    contract_ = contract_.lower()

    # variável para verificar se encontrou algum trabalho
    found = False

    for job in jobs:
        # verificar se permite trabalho remoto e se a localização e contrato estão nos critérios
        job_locations = [loc["name"].lower() for loc in job.get("locations", [])]
        job_contracts = [contract["name"].lower() for contract in job.get("contracts", [])]
        
        if job.get("allowRemote") == True and location_ in job_locations and contract_ in job_contracts:
            print(f"Trabalho remoto encontrado: {job['title']} na empresa {job['company']['name']}")
            found = True

    if not found:
        print("Nenhum trabalho remoto encontrado para os critérios especificados.")

# função para extrair o valor do salário
def extract_wage(job_data):
    # tenta pegar o valor direto do campo 'wage'
    wage = job_data.get("wage")
    if wage:
        return f"Salário encontrado no campo específico: {wage}"

    # se wage for nulo, tenta encontrar um valor no campo 'body' usando expressões regulares
    body_text = job_data.get("body", "")
    salary_patterns = re.findall(r"(\€|\$|USD|EUR)?\s?\d+\s?(€|\$|USD|EUR)?", body_text, re.IGNORECASE)

    # filtra e retorna apenas valores válidos (não vazios)
    valid_salaries = [f"{pattern[0]}{pattern[1]}" if pattern[0] else f"{pattern[1]}" for pattern in salary_patterns if pattern[0] or pattern[1]]

    if valid_salaries:
        return f"Salário(s) encontrado(s) no campo 'body': {', '.join(valid_salaries)}"
    else:
        return "Salário não encontrado em nenhum campo."

# função para extrair a informação relativa ao salário oferecido por um determinado job id
@app.command()
def get_salary(job_id: int):
    data = get_api()
    jobs = data.get("results", [])
        
    job_data = next((job for job in jobs if job["id"] == job_id), None)
    
    if job_data:
        wage_info = extract_wage(job_data)
        typer.echo(wage_info)
    else:
        typer.echo(f"Job ID {job_id} não encontrado.")
        raise typer.Exit()

# função para mostrar quais os trabalhos que requerem uma determinada lista de skills
@app.command()
def skills(
    skills: str = typer.Argument(..., help="Lista de skills separadas por vírgulas, por exemplo: python,django,sql"),
    export_csv: Optional[str] = typer.Option(None, help="Exporta os dados para um arquivo CSV")
):
    data = get_api()
    jobs = data.get("results", [])
    
    skill_list = [skill.strip() for skill in skills.split(',')]
    
    # filtra os trabalhos que contêm as skills especificadas no corpo da descrição
    filtered_jobs = []
    for job in jobs:
        job_description = job.get("body", "").lower()
        if all(re.search(rf'\b{skill.lower()}\b', job_description) for skill in skill_list):
            job_data = {
                "id": job.get("id"),
                "title": job.get("title"),
                "company": job.get("company", {}).get("name", ""),
                "description": job.get("body"),
                "publishedAt": job.get("publishedAt"),
                "wage": job.get("wage", ""),
                "locations": [location.get("name") for location in job.get("locations", [])],
            }
            filtered_jobs.append(job_data)

    # exibe apenas os ids no terminal
    if filtered_jobs:
        job_ids = [job["id"] for job in filtered_jobs]
        for job_id in job_ids:
            typer.echo(f"Job ID: {job_id}")
        
        # exporta para csv se solicitado
        if export_csv:
            export_to_csv1(filtered_jobs, export_csv)
    else:
        print("Nenhum trabalho encontrado para as skills especificadas.")

# função para organizar os trabalhos por localidade
def organizar_trabalhos_por_localidade():
    data = get_api()
    jobs = data.get("results", [])
    
    dados_estruturados = defaultdict(lambda: defaultdict(list))
    for job in jobs:
        titulo = job.get("title", "N/A")
        empresa = job.get("company", {}).get("name", "N/A")
        
        # obter todas as localidades associadas ao trabalho
        localizacoes = [loc["name"] for loc in job.get("locations", [])]
        
        # estrutura de dados: localidade -> empresa -> lista de títulos dos trabalhos
        for localizacao in localizacoes:
            dados_estruturados[localizacao][empresa].append({
                "titulo": titulo,
                "email": job.get("company", {}).get("email", "N/A"),
                "url": job.get("company", {}).get("url", "N/A"),
            })
    
    return dados_estruturados

# função para exibir trabalhos no terminal
def exibir_trabalhos_no_terminal(dados_estruturados):
    for localizacao, empresas in dados_estruturados.items():
        print(f"\nLocalização: {localizacao}")
        for empresa, titulos in empresas.items():
            print(f"            Empresa: {empresa}")
            for trabalho in titulos:
                print(f"                    Trabalho: {trabalho['titulo']}")

# função para exportar os dados para pdf
def export_to_pdf(dados_estruturados, nome_arquivo="trabalhos_por_localidade.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", size=12)

    pdf.cell(200, 10, txt="Trabalhos Organizados por Localidade", ln=True, align="C")
    
    for localizacao, empresas in dados_estruturados.items():
        pdf.ln(10)
        
        pdf.set_font("Arial", size=11)
        pdf.cell(0, 10, txt=f"Localização: {localizacao}", ln=True)
        
        for empresa, titulos in empresas.items():
            pdf.set_font("Arial", size=11)
            pdf.cell(23)
            pdf.cell(0, 8, txt=f"Empresa: {empresa}", ln=True)
            
            for trabalho in titulos:
                pdf.set_font("Arial", size=10)
                pdf.cell(40)
                pdf.cell(0, 6, txt=f"Trabalho: {trabalho['titulo']}", ln=True)
            
            for trabalho in titulos:
                pdf.set_font("Arial", size=10)
                pdf.cell(40)
                pdf.cell(0, 6, txt=f"email: {trabalho['email']}", ln=True)
                pdf.cell(40)
                pdf.cell(0, 6, txt=f"url: {trabalho['url']}", ln=True)
    
    pdf.output(nome_arquivo)
    print(f"Dados exportados para '{nome_arquivo}' com sucesso!")

# função para listar localidades com respetivas empresas e respetivos trabalhos
@app.command()
def trabalhos_por_localidade():
    dados_estruturados = organizar_trabalhos_por_localidade()
    exibir_trabalhos_no_terminal(dados_estruturados)
    export_to_pdf(dados_estruturados)


"""TP2"""

# função de exportação para csv
def export_to_csv2(data, export_csv: Optional[str]):
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
        export_to_csv2(data, export_csv)
    
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
def statistics(job_title: str = typer.Argument(None, help="Mostrar as vagas de um tipo de trabalho")):
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
        export_to_csv2(result, export_csv)

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
    description_div = body.find('div', attrs={"data-testid": "less-text", "class": "css-9146s eu4oa1w0"})
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
        export_to_csv2(data, export_csv)


if __name__ == "__main__":
    app()
