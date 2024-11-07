import requests
import typer
import json
import csv

url = "https://api.itjobs.pt/job/list.json?api_key=09ad1042ebaf1704533805cd2fab64f1"

headers = {
    "User-Agent": ""
}

response = requests.get(url, headers=headers)
data = response.json()

app = typer.Typer()

@app.command()
def full_time_jobs(
    company_name: str = typer.Argument(..., help="Nome da empresa desejada"),
    location: str = typer.Argument(..., help="Localização da empresa"),
    limit: int = typer.Argument(1, help="Número máximo de resultados a exibir"),
):
    company_name = company_name.lower()
    location = location.lower()

    companies_result = []

    # percorre todos os resultados da API para encontrar correspondências
    for item in data["results"]:
        # nome da empresa no JSON em minúsculas para comparação
        company_name_json = (item["company"]["name"]).lower()
        
        # verifica se o nome da empresa corresponde
        if company_name_json == company_name:
            # verifica se há "Full-time" em `types` e se a localização desejada existe em `locations`
            full_time = any(t["name"] == "Full-time" for t in item.get("types", []))
            location_match = any(l["name"].lower() == location for l in item.get("locations", []))
            
            # se encontrar "Full-time" e a localização desejada, adiciona à lista
            if full_time and location_match:
                companies_result.append(item)
    
    # aplica o limite de resultados desejado
    companies_result = companies_result[:limit]

    # exibe os resultados em formato JSON ou uma mensagem de erro se nenhum resultado for encontrado
    if companies_result:
        print(json.dumps(companies_result, indent=4, ensure_ascii=False))
    else:
        print(f"Não existe nenhum trabalho do tipo 'Full-time' com localização '{location}', encontrada para '{company_name}'.")

if __name__ == "__main__":
    app()