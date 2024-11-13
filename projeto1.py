import re
import requests
import json
import csv
import typer
from datetime import datetime
from collections import defaultdict
from typing import Optional
from fpdf import FPDF

app = typer.Typer()

URL = "https://api.itjobs.pt/job/list.json?api_key=09ad1042ebaf1704533805cd2fab64f1"
headers = {"User-Agent": ""}

# Função para limpar o HTML da descrição
def limpar_html(texto_html):
    texto_limpo = re.sub(r"<br\s*/?>", " ", texto_html)  # Substitui <br> por espaço
    texto_limpo = re.sub(r"</?p>", " ", texto_limpo)  # Substitui <p> por espaço
    texto_limpo = re.sub(r"</?strong>", "", texto_limpo)  # Remove <strong> e </strong>
    texto_limpo = re.sub(r"</?a[^>]*>", "", texto_limpo)  # Remove tags <a> (links)
    texto_limpo = re.sub(r"<[^>]+>", "", texto_limpo)  # Remove qualquer outra tag HTML restante
    texto_limpo = re.sub(r"\n\s*\n", " ", texto_limpo).strip()  # Substitui múltiplas quebras de linha por espaço
    return texto_limpo

# Função de exportação para CSV
def export_to_csv(data, export_csv: Optional[str]):
    if export_csv:
        try:
            with open(export_csv, mode="w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                
                # Definir cabeçalho para CSV com nomes dos campos
                header = ["ID", "Título", "Empresa", "Descrição", "Data de Publicação", "Salário", "Localização"]
                writer.writerow(header)
                
                # Escrever cada linha, tratando campos ausentes
                for item in data:
                    row = [
                        item.get("id", "N/A"),
                        item.get("title", "N/A"),
                        item.get("company", "N/A"),
                        item.get("description", "N/A"),
                        item.get("publishedAt", "N/A"),
                        item.get("wage", "N/A"),
                        item.get("locations", "N/A"),
                    ]
                    writer.writerow(row)
            print(f"Resultados exportados para o arquivo CSV: {export_csv}")
            
        except IOError as e:
            print(f"Erro ao salvar o arquivo CSV: {e}")

def extract_wage(job_data):
    # Tenta pegar o valor direto do campo 'wage'
    wage = job_data.get("wage")
    if wage:
        return f"Salário encontrado no campo específico: {wage}"

    # Se wage for nulo, tenta encontrar um valor no campo 'body' usando expressões regulares
    body_text = job_data.get("body", "")
    salary_patterns = re.findall(r"(\€|\$|USD|EUR)?\s?\d+\s?(€|\$|USD|EUR)?", body_text, re.IGNORECASE)

    # Filtra e retorna apenas valores válidos (não vazios)
    valid_salaries = [f"{pattern[0]}{pattern[1]}" if pattern[0] else f"{pattern[1]}" for pattern in salary_patterns if pattern[0] or pattern[1]]

    if valid_salaries:
        return f"Salário(s) encontrado(s) no campo 'body': {', '.join(valid_salaries)}"
    else:
        return "Salário não encontrado em nenhum campo."

def organizar_trabalhos_por_localidade():
    response = requests.get(URL, headers=headers)
    trabalhos = response.json().get("results", [])
    
    dados_estruturados = defaultdict(lambda: defaultdict(list))
    for job in trabalhos:
        titulo = job.get("title", "N/A")
        empresa = job.get("company", {}).get("name", "N/A")
        
        # Obter todas as localidades associadas ao trabalho
        localizacoes = [loc["name"] for loc in job.get("locations", [])]
        
        # Estrutura de dados: Localidade -> Empresa -> Lista de Títulos dos Trabalhos
        for localizacao in localizacoes:
            dados_estruturados[localizacao][empresa].append({
                "titulo": titulo,
                "email": job.get("company", {}).get("email", "N/A"),
                "url": job.get("company", {}).get("url", "N/A"),
            })
    
    return dados_estruturados

def exibir_trabalhos_no_terminal(dados_estruturados):
    for localizacao, empresas in dados_estruturados.items():
        print(f"\nLocalização: {localizacao}")
        for empresa, titulos in empresas.items():
            print(f"            Empresa: {empresa}")
            for trabalho in titulos:
                print(f"                    Trabalho: {trabalho['titulo']}")

# Função para exportar os dados para PDF
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

# Função para listar n trabalhos mais recentes
@app.command()
def listar_trabalhos(
    n: int = typer.Argument(10, help="Número de trabalhos para listar"),
    export_csv: Optional[str] = typer.Option(None, help="Exporta os dados para um arquivo CSV")
):
    response = requests.get(URL, headers=headers)
    jobs = response.json().get("results", [])
    
    jobs_sorted = sorted(jobs, key=lambda job: datetime.strptime(job["publishedAt"], "%Y-%m-%d %H:%M:%S"), reverse=True)
    
    # Seleciona os n trabalhos mais recentes
    jobs_most_recent = jobs_sorted[:n]
    print(json.dumps(jobs_most_recent, ensure_ascii=False, indent=2))
    
    n_recent_jobs = []
    for job in jobs_most_recent:
        job_data = {
                "id": job.get("id", "N/A"),
                "title": job.get("title", "N/A"),
                "company": job.get("company", {}).get("name", "N/A"),
                "description": limpar_html(job.get("body", "N/A")),
                "publishedAt": job.get("publishedAt", "N/A"),
                "wage": job.get("wage", "N/A"),
                "locations": "; ".join([location.get("name", "N/A") for location in job.get("locations", [])]),
        }
        n_recent_jobs.append(job_data)
    
    # Exporta para CSV se solicitado
    export_to_csv(n_recent_jobs, export_csv)

# Função para listar todos os trabalhos do tipo full-time, publicados por uma determinada empresa, numa determinada localidade
@app.command()
def full_time_jobs(
    company_name: str = typer.Argument(..., help="Nome da empresa desejada"),
    location: str = typer.Argument(..., help="Localização da empresa"),
    limit: int = typer.Argument(1, help="Número máximo de resultados a exibir"),
    export_csv: Optional[str] = typer.Option(None, help="Exporta os dados para um arquivo CSV")
):
    response = requests.get(URL, headers=headers)
    data = response.json()
    
    company_name = company_name.lower()
    location = location.lower()

    companies_result = []

    for item in data["results"]:
        company_name_json = (item["company"]["name"]).lower()
        
        # Verifica se o nome da empresa corresponde
        if company_name_json == company_name:
            # Verifica se há "Full-time" em `types` e se a localização desejada existe em `locations`
            full_time = any(t["name"] == "Full-time" for t in item.get("types", []))
            location_match = any(l["name"].lower() == location for l in item.get("locations", []))
            
            if full_time and location_match:
                companies_result.append({
                    "id": item["id"],
                    "title": item["title"],
                    "company": item.get("company", {}),
                    "description": limpar_html(item["body"]),
                    "publishedAt": item.get("publishedAt"),
                    "wage": item.get("wage"),
                    "locations": item.get("locations", []),
                })
    
    # Aplica o limite de resultados desejado
    companies_result = companies_result[:limit]

    # Exibe os resultados em formato JSON ou uma mensagem de erro se nenhum resultado for encontrado
    if companies_result:
        print(json.dumps(companies_result, indent=4, ensure_ascii=False))
        
        # Exporta para CSV se solicitado
        if export_csv:
            
            full_time_jobs_companies = []
            for job in companies_result:
                job_data = {
                        "id": job.get("id", "N/A"),
                        "title": job.get("title", "N/A"),
                        "company": job.get("company", {}).get("name", "N/A"),
                        "description": limpar_html(job.get("body", "N/A")),
                        "publishedAt": job.get("publishedAt", "N/A"),
                        "wage": job.get("wage", "N/A"),
                        "locations": "; ".join([location.get("name", "N/A") for location in job.get("locations", [])]),
                }
                full_time_jobs_companies.append(job_data)
            
            export_to_csv(full_time_jobs_companies, export_csv)
    else:
        print(f"Não existe nenhum trabalho do tipo 'Full-time' com localização '{location}', encontrado para '{company_name}'.")

# Função para extrair a informação relativa ao salário oferecido por um determinado job id
@app.command()
def get_salary(job_id: int):
    response = requests.get(URL, headers=headers)
    jobs = response.json().get("results", [])
        
    job_data = next((job for job in jobs if job["id"] == job_id), None)
    
    if job_data:
        wage_info = extract_wage(job_data)
        typer.echo(wage_info)
    else:
        typer.echo(f"Job ID {job_id} não encontrado.")
        raise typer.Exit()

# Função para mostrar quais os trabalhos que requerem uma determinada lista de skills
@app.command()
def skills(
    skills: str = typer.Argument(..., help="Lista de skills separadas por vírgulas, por exemplo: python,django,sql"),
    export_csv: Optional[str] = typer.Option(None, help="Exporta os dados para um arquivo CSV")
):
    # Solicita os dados da API
    response = requests.get(URL, headers=headers)
    data = response.json()
    jobs = data.get("results", [])
    
    # Processa a lista de skills
    skill_list = [skill.strip() for skill in skills.split(',')]
    
    # Filtra os trabalhos que contêm as skills especificadas no corpo da descrição
    filtered_jobs = []
    for job in jobs:
        job_description = job.get("body", "").lower()
        if all(re.search(rf'\b{skill.lower()}\b', job_description) for skill in skill_list):
            # Adiciona os dados do trabalho ao filtro com valores padrão
            job_data = {
                "id": job.get("id", "N/A"),
                "title": job.get("title", "N/A"),
                "company": job.get("company", {}).get("name", "N/A"),
                "description": limpar_html(job.get("body", "N/A")),
                "publishedAt": job.get("publishedAt", "N/A"),
                "wage": job.get("wage", "N/A"),
                "locations": "; ".join([location.get("name", "N/A") for location in job.get("locations", [])]),
            }
            filtered_jobs.append(job_data)

    # Exibe apenas os IDs no terminal
    if filtered_jobs:
        job_ids = [job["id"] for job in filtered_jobs]
        for job_id in job_ids:
            typer.echo(f"Job ID: {job_id}")
        
        # Exporta para CSV se solicitado
        if export_csv:
            export_to_csv(filtered_jobs, export_csv)
    else:
        print("Nenhum trabalho encontrado para as skills especificadas.")

# Função para listar localidades com respetivas empresas e respetivos trabalhos
@app.command()
def trabalhos_por_localidade():
    dados_estruturados = organizar_trabalhos_por_localidade()
    exibir_trabalhos_no_terminal(dados_estruturados)
    export_to_pdf(dados_estruturados)
    
# Função para mostrar os trabalhos que permitem trabalho remoto num determinado distrito
@app.command()
def remote_jobs(
    location_: str = typer.Argument(..., help="Localização da empresa"),
    contract_: str = typer.Argument(..., help="Tipo de contrato desejado"),
):
    
    response = requests.get(URL, headers=headers)
    data = response.json()

    location_ = location_.lower()
    contract_ = contract_.lower()

    # Variável para verificar se encontrou algum trabalho
    found = False

    for job in data["results"]:
        # Verificar se permite trabalho remoto e se a localização e contrato estão nos critérios
        job_locations = [loc["name"].lower() for loc in job.get("locations", [])]
        job_contracts = [contract["name"].lower() for contract in job.get("contracts", [])]
        
        if job.get("allowRemote") == True and location_ in job_locations and contract_ in job_contracts:
            print(f"Trabalho remoto encontrado: {job['title']} na empresa {job['company']['name']}")
            found = True

    if not found:
        print("Nenhum trabalho remoto encontrado para os critérios especificados.")

if __name__ == "__main__":
    app()
