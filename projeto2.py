import re
import requests
from bs4 import BeautifulSoup
import typer
import json

app = typer.Typer()

# função para obter a lista de trabalho da api do itjobs.pt
def get_api():
    all_results = []
    url = "https://api.itjobs.pt/job/list.json?api_key=09ad1042ebaf1704533805cd2fab64f1"
    page = 1

    while page <= 10:  # Limite de 10 páginas
        response = requests.get(f"{url}&page={page}", headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            print(f"Erro ao acessar a API: {response.status_code}")
            break

        data = response.json()
        results = data.get("results", [])
        if not results:
            break

        all_results.extend(results)
        page += 1

        if len(results) < data.get("limit", 50):  # Finaliza se menos resultados que o limite
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
def get_html2(job_id):
    company_name = find_company_name(job_id)
    if company_name is None:
        print(f"Empresa não encontrada para o job ID {job_id}.")
        return
    
    company_name = re.sub(r'\s+', '-', company_name)
    
    url = f"https://pt.indeed.com/cmp/{company_name}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "pt-PT,pt;q=0.9,pt-BR;q=0.8,en;q=0.7,en-US;q=0.6,en-GB;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0" 
    }

    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"URL: {response.url}")
    print(f"Content Preview: {response.text[:500]}")  # Mostra os primeiros 500 caracteres do HTML

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
def informations2(job_id: int):
    api_data = get_api_content(job_id)
    if api_data is None:
        print(f"Job com ID {job_id} não encontrado na API.")
        return
    soup = get_html2(job_id)
    html_content = get_html_content2(soup)

    data = {**api_data, **html_content}

    print(json.dumps(data, indent=4))

if __name__ == "__main__":
    app()
