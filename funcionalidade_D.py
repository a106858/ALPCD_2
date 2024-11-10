# Implementação da exportação CSV com a função limpar_html
import requests
import json
import re
import csv
from typing import Optional
import typer

# Início do código conforme solicitado
url = "https://api.itjobs.pt/job/list.json?api_key=09ad1042ebaf1704533805cd2fab64f1"
headers = {"User-Agent": ""}
response = requests.get(url, headers=headers)
data = response.json()  # Obtém os dados da resposta da API
jobs = data.get("results", [])  # Extrai a lista de resultados

app = typer.Typer()

# Limpar o body
def limpar_html(texto_html):
    texto_limpo = re.sub(r"<br\s*/?>", " ", texto_html)  # Substitui <br> por espaço
    texto_limpo = re.sub(r"</?p>", " ", texto_limpo)  # Substitui <p> por espaço
    texto_limpo = re.sub(r"</?strong>", "", texto_limpo)  # Remove <strong> e </strong>
    texto_limpo = re.sub(r"</?a[^>]*>", "", texto_limpo)  # Remove tags <a> (links)
    texto_limpo = re.sub(r"<[^>]+>", "", texto_limpo)  # Remove qualquer outra tag HTML restante
    texto_limpo = re.sub(r"\n\s*\n", " ", texto_limpo).strip()  # Substitui múltiplas quebras de linha por espaço
    return texto_limpo

@app.command()
def skills(
    skills: str = typer.Argument(..., help="Lista de skills separadas por vírgulas, por exemplo: python,django,sql"),
    export_csv: Optional[str] = typer.Option(None, help="Caminho para exportar o resultado em um arquivo CSV")
):
    """
    Mostra os trabalhos que requerem uma lista de skills específica e exporta para CSV se solicitado.
    """
    # Processa a lista de skills
    skill_list = [skill.strip() for skill in skills.split(',')]
    print(f"Skills fornecidas: {skill_list}")  # Mensagem de depuração

    # Filtra os trabalhos que contêm as skills especificadas no corpo da descrição
    filtered_jobs = []
    for job in jobs:
        job_description = job.get("body", "").lower()
        if all(re.search(rf'\b{skill.lower()}\b', job_description) for skill in skill_list):
            job_data = {
                "id": job.get("id"),
                "title": job.get("title"),
                "company": job.get("company", {}).get("name", ""),  # Evita erro caso não haja nome da empresa
                "description": job.get("body"),  # Usa 'body' para descrição do trabalho
                "publishedAt": job.get("publishedAt"),
                "wage": job.get("wage", ""),
                "locations": [location.get("name") for location in job.get("locations", [])],
            }
            filtered_jobs.append(job_data)

    # Exibe o resultado em JSON formatado
    if filtered_jobs:
        typer.echo(json.dumps(filtered_jobs, indent=2, ensure_ascii=False))
    else:
        print("Nenhum trabalho encontrado para as skills especificadas.")

    # Exporta para CSV, se o caminho for fornecido
    if export_csv:
        try:
            with open(export_csv, mode="w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["titulo", "empresa", "descricao", "data de publicacao", "salario", "localizacao"])
                for job in filtered_jobs:
                    # Aplica a função limpar_html na descrição antes de exportar para CSV
                    descricao_limpa = limpar_html(job["description"])
                    writer.writerow([
                        job["title"],
                        job["company"],
                        descricao_limpa,  # Descrição limpa
                        job["publishedAt"],
                        job["wage"],
                        "; ".join(job["locations"])  # Concatena várias localizações em uma única string
                    ])
            typer.echo(f"Resultados exportados para o arquivo CSV: {export_csv}")
        except IOError as e:
            typer.echo(f"Erro ao salvar o arquivo CSV: {e}")

if __name__ == "__main__":
    app()
