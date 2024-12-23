import re
import requests
from bs4 import BeautifulSoup
import typer
import json

app = typer.Typer()

# função para obter a lista de trabalho da api do itjobs.pt
def get_api():
    url = "https://api.itjobs.pt/job/list.json?api_key=09ad1042ebaf1704533805cd2fab64f1"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    return response.json()

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

# função para obter o conteúdo do trabalho em formato json através da api
def get_api_content(job_id):
    data = get_api()
    jobs = data.get("results", [])
    
    for job in jobs:
        if job["id"] == job_id:
            data = {
                "id": job.get("id", "N/A"),
                "title": job.get("title", "N/A"),
                "company": job.get("company", {}).get("name", "N/A"),
            }
            json_api_data = json.dumps(data, indent=4)
            return json_api_data
    return None

# função para obter o conteúdo da empresa em formato json através do html
def get_html_content(company_name):
    if not company_name:
        return None
    
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
    soup = BeautifulSoup(response.text, 'lxml')
    
    body = soup.find('body')

    # encontrar o overall rating
    overall_rating = body.find('span', class_="css-1jxf684 text-primary-text font-pn-700 text-[32px] leading-[32px]").text

    # encontrar a descrição da empresa
    description1 = body.find('div', dir="auto", class_="css-146c3p1 font-pn-400 text-sm text-neutral mb-2").text
    description2_here = body.find('div', class_="text-sm font-pn-400 [&_ul]:list-disc [&_ol]:list-[auto] [&_ul]:ml-5 [&_ol]:ml-5")
    description2 = description2_here.find('p').text
    description = description1 + " " + description2

    # encontrar os principais benefícios
    benefits_here = body.find_all('div', class_="css-175oi2r border relative rounded-md border-card-border bg-white p-4 flex flex-col gap-3 md:gap-4")
    work_policy_here = benefits_here[0]
    work_policy = work_policy_here.find_all('div', dir="auto", class_="css-146c3p1 font-pn-400 text-sm text-primary-text")
    work_policy_list = []
    for policy in work_policy:
        work_policy_list.append(policy.text)
    top_employees_benefits_here = benefits_here[1]
    top_employees_benefits = top_employees_benefits_here.find_all('div', class_="css-146c3p1 font-pn-400 text-sm text-primary-text")
    top_employees_benefits_list = []
    for top_benefits in top_employees_benefits:
        top_employees_benefits_list.append(top_benefits.text)
    benefits = f"work_policy: {', '.join(work_policy_list)}" + "; " + f"top_employees_benefits: {', '.join(top_employees_benefits_list)}"

    data = {
        "overall_rating": overall_rating,
        "description": description,
        "benefits": benefits
    }
    json_html_data = json.dumps(data, indent=4)
    return json_html_data

# função para juntar todas as informações
@app.command()
def informations(job_id: int):
    json_api_data = get_api_content(job_id)
    if json_api_data is None:
        print(f"Job com ID {job_id} não encontrado na API.")
        return
    company_name = find_company_name(job_id)
    if company_name is None:
        print(f"Empresa não encontrada para o job ID {job_id}.")
        return
    json_html_data = get_html_content(company_name)
    if json_html_data is None:
        print(f"Não foi possível obter dados do website para a empresa: {company_name}.")
        return
    
    json_data = json.loads(json_api_data)
    company_data = json.loads(json_html_data)
    
    json_data["overall_rating"] = company_data.get("overall_rating", "N/A")
    json_data["description"] = company_data.get("description", "N/A")
    json_data["benefits"] = company_data.get("benefits", "N/A")
    
    print(json.dumps(json_data, indent=4))

if __name__ == "__main__":
    app()
