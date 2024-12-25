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
        "Cookie": "CTK=1ifs3bt14ic1m800; RF="TFTzyBUJoNpus07_5JKTqtdSks_gPWcG8OnfNxaNtiMtS1PAh0PSRQfA_JJKKyrdk7Ll4SScfPs="; CSRF=SWP6TrFXrNoHMIdV4iimyy2MO8w5RfB9; INDEED_CSRF_TOKEN=Hn3NuKcn1Niyw1azBJMSHrKsbB9xFADs; indeed_rcc=LV:CTK; OptanonAlertBoxClosed=2024-12-24T10:28:57.905Z; CMP_VISITED=1; cmppmeta="eNoBSAC3/5XbTmwUA9aGt5P1H0MeKyqaDR0WvGipolvSvZcDimzHFE5E9wT4W/Hg3Z7Zs2SZ+9tx0yrybUp04FwxQ9BbSHy3PLi+LnfuAO8DJAE="; SURF=GhK8zb8MsmUwVx6isqVomvbK11dNWgxw; cmp-jobsCta=hidden; g_state={"i_p":1735150839541,"i_l":2}; SOCK="_GzsakoHEuDjYA2yIjBgpuexXts="; SHOE="DwU0Z7B6UAY1_IQpuCN-ZpmHlaESMNwo0SKf3EWKss1kGjEopBdu62K_clQpmbhzNQRM3N9tFppUF4jvFx7eWw9PFsOU5LSLrZK98Alb6vrNBlm399eXCu7vo1xOrelTqEDInAWtkUqy6aDQa7pOZrHSmSs="; ENC_CSRF=apjHhFgtz3ZAtKw5qWai39pxBMZai4g5; FPID=FPID2.2.vjUcu58NWr0YJepN%2BEln%2BEvcIJDndl%2FtYW7MiB7doRc%3D.1735128472; _cfuvid=4PuQvXxGx1r7SFBg0qCljpBr1S5LdtHYKbcxEkUm7XM-1735129458821-0.0.1.1-604800000; NOMOB=1; LC="co=PT"; SHARED_INDEED_CSRF_TOKEN=Hn3NuKcn1Niyw1azBJMSHrKsbB9xFADs; LV="LA=1735146047:LV=1735140882:CV=1735146047:TS=1735036105"; PREF="TM=1735146047184:L=porto"; MICRO_CONTENT_CSRF_TOKEN=LJiMdQpqSJQEFXzFl800KYbuFZSYrMWe; RQ="q=data+scientist&l=porto&ts=1735146165424&sc=0kf%3Afcckey%28487b2ef9a61ad1f9%29%3B:q=pandora&l=&ts=1735142546302&pts=1735132492091&sc=0kf%3Afcckey%28324256ddd6f3b668%29%3B:q=pandora&l=London&ts=1735142517877:q=python+developer&l=London&ts=1735140898381"; JSESSIONID=1A9C76BACAE692B55CA546E86D5266EC; bvcmpgn=pt-indeed-com; __cf_bm=KpAvSdmGIH_auUhe60dx8fDNd9VrrXCflMTQmWPwT8E-1735160847-1.0.1.1-epBFkqMng3EysuQHB9V.pM1OODbH5zdZujNJhh7H2YFeFONSZLTStFmv.Hb0TkNbH7RdN80WRaCbebH7SpQVFA; PPID=eyJraWQiOiI3MGFhN2RlZS0xNzRjLTRiNWEtOTU1YS0xZThjY2I2ZDZlNTQiLCJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJzdWIiOiIzYmI1YWZkNmExNWU4Njk4IiwibGFzdF9hdXRoX3RpbWUiOjE3MzUxMjg0NzA5MTEsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJhdXRoIjoiZ29vZ2xlIiwiY3JlYXRlZCI6MTczNTEyODQ3MDAwMCwiaXNzIjoiaHR0cHM6Ly9zZWN1cmUuaW5kZWVkLmNvbSIsImxhc3RfYXV0aF9sZXZlbCI6IlNUUk9ORyIsImxvZ190cyI6MTczNTEyODQ3MDkxMSwiYXVkIjoiYzFhYjhmMDRmIiwicmVtX21lIjp0cnVlLCJleHAiOjE3MzUxNjMxNDIsImlhdCI6MTczNTE2MTM0MiwiZW1haWwiOiJmcmFuY2lzY2FkZXNhbWFjaGFkb0BnbWFpbC5jb20ifQ.nicZZFs-bjIEQ9pcily2Nw0cHuVPm9R-YE2dDZ0uHtDZoSRAx2aKsdHzHaoHwiA1Sx81xePxOclFY_eBdUK3Kw; OptanonConsent=isGpcEnabled=0&datestamp=Wed+Dec+25+2024+21%3A15%3A43+GMT%2B0000+(Hora+padr%C3%A3o+da+Europa+Ocidental)&version=202409.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=4313964e-2f4c-432f-896b-0877c6aea401&interactionCount=2&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A0%2CC0003%3A0%2CC0004%3A0%2CC0007%3A0&AwaitingReconsent=false&intType=2&geolocation=%3B; indeed_rcc="cmppmeta:LV"; cf_clearance=MI4Mjas.G5NovITE0jJv5O1Gh1nKkEgmcUdl6GtKEBg-1735161343-1.2.1.1-MfzZDW48F3a0nOXDoETqJfL7pvSvJRhs5T1ompTCUF3naZ9JoRwSmlkgQJ6MxYFKFNc6Ji9tC8WWAn0qnu45q8O_lcJCRCa1ChNljL62DQp_45zR4WNcp88OZeEQxl1uwJ8HlkvbrXmVMF46s1x9i.n_13BHcS.MgzK2llY.zkBOaPKorRc61Y8jK4VReammzjmJPmooXn7YCDJscxF3hRQ7uzUat7L0KVsetp7GlAXXUNJodij5lqlF0CLDllXv2GTSwApxs6rzNLh.FfAkaUpG6rD8fn.G8Er_bsXmn_QTm4IVxuNeKx3A1a27CSBvZv58.NblP7nyxbraFILMtXUUW9QfA2ldVF8grfYPMNnKP6amA6IHy0MIOMyy7poA93WXAZ2frQbG7wgrpUN.9Q"

    }

    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}") #tem de dar 200 para conseguir aceder ao site

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
