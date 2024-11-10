import typer
import requests
import json
import re
import csv
from typing import Optional

url = "https://api.itjobs.pt/job/list.json?api_key=09ad1042ebaf1704533805cd2fab64f1"
headers = {"User-Agent": ""}
response = requests.get(url, headers=headers)
data = response.json()


app = typer.Typer()

def limpar_html(texto_html):
    texto_limpo = re.sub(r"<br\s*/?>", " ", texto_html)  # Substitui <br> por espaço
    texto_limpo = re.sub(r"</?p>", " ", texto_limpo)  # Substitui <p> por espaço
    texto_limpo = re.sub(r"</?strong>", "", texto_limpo)  # Remove <strong> e </strong>
    texto_limpo = re.sub(r"</?a[^>]*>", "", texto_limpo)  # Remove tags <a> (links)
    texto_limpo = re.sub(r"<[^>]+>", "", texto_limpo)  # Remove qualquer outra tag HTML restante
    texto_limpo = re.sub(r"\n\s*\n", " ", texto_limpo).strip()  # Substitui múltiplas quebras de linha por espaço
    return texto_limpo

def export_to_csv(data, export_csv: Optional[str]):
    
    if export_csv:
        try:
            # Salva o CSV diretamente no caminho fornecido
            with open(export_csv, mode="w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                # Cabeçalho para CSV
                writer.writerow(["id", "titulo", "empresa", "descricao", "data de publicacao", "salario", "localizacao"])
                for item in data:
                    writer.writerow([
                        item["id"],
                        item["title"],
                        item["company"]["name"] if item["company"] else "",
                        limpar_html(item["body"]),
                        item["publishedAt"],
                        item.get("wage", ""),
                        "; ".join([loc["name"] for loc in item.get("locations", [])]),
                    ])
            print(f"Resultados exportados para o arquivo CSV: {export_csv}")
        except IOError as e:
            print(f"Erro ao salvar o arquivo CSV: {e}")

################# Alínea (b) #################

@app.command()
def full_time_jobs(
    company_name: str = typer.Argument(..., help="Nome da empresa desejada"),
    location: str = typer.Argument(..., help="Localização da empresa"),
    limit: int = typer.Argument(1, help="Número máximo de resultados a exibir"),
    export_csv: Optional[str] = typer.Option(None, help="Caminho para exportar o resultado em um arquivo CSV")
):
    company_name = company_name.lower()
    location = location.lower()

    companies_result = []

    # percorre todos os resultados da API para encontrar correspondências
    for item in data["results"]:
        company_name_json = (item["company"]["name"]).lower()
        
        # verifica se o nome da empresa corresponde
        if company_name_json == company_name:
            # verifica se há "Full-time" em `types` e se a localização desejada existe em `locations`
            full_time = any(t["name"] == "Full-time" for t in item.get("types", []))
            location_match = any(l["name"].lower() == location for l in item.get("locations", []))
            
            # se encontrar "Full-time" e a localização desejada, adiciona à lista
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

    # exibe os resultados em formato JSON ou uma mensagem de erro se nenhum resultado for encontrado
    if companies_result:
        print(json.dumps(companies_result, indent=4, ensure_ascii=False))
    else:
        print(f"Não existe nenhum trabalho do tipo 'Full-time' com localização '{location}', encontrada para '{company_name}'.")

    export_to_csv(companies_result, export_csv)

if __name__ == "__main__":
    app()
