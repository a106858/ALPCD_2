import re
import requests
import typer
import json
from datetime import datetime
import csv

app = typer.Typer()

URL = "https://api.itjobs.pt/job/list.json?api_key=09ad1042ebaf1704533805cd2fab64f1"
headers = {
    "User-Agent": ""
}

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
def listar_trabalhos(
    n: int = typer.Argument(10, help="Número de trabalhos para listar"),
    exportar_csv: bool = typer.Option(False, "--exportar-csv", help="Exporta os dados para um arquivo CSV")
):
    response = requests.get(URL, headers=headers)
    
    # Processa a resposta da API em formato JSON
    jobs = response.json().get("results", [])
    
    # Ordena os trabalhos pela data de publicação de forma decrescente (mais recentes primeiro)
    jobs_sorted = sorted(jobs, key=lambda job: datetime.strptime(job["publishedAt"], "%Y-%m-%d %H:%M:%S"), reverse=True)
    
    # Seleciona apenas os n trabalhos mais recentes
    jobs_most_recent = jobs_sorted[:n]
    
    # Exibe a lista de trabalhos no terminal em formato JSON
    print(json.dumps(jobs_most_recent, ensure_ascii=False, indent=2))
    
    # Verifica se o usuário deseja exportar para CSV
    if exportar_csv:
        with open("trabalhos_recentes.csv", mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            # Escreve o cabeçalho no CSV
            writer.writerow(["Título", "Empresa", "Descrição", "Data de Publicação", "Salário", "Localização"])

            for job in jobs_most_recent:
                titulo = job.get("title", "N/A")
                empresa = job.get("company", {}).get("name", "N/A")
                
                descricao_html = job.get("body", "N/A")
                descricao = limpar_html(descricao_html)
                
                data_publicacao = job.get("publishedAt", "N/A")
                salario = job.get("wage", "N/A")
                
                # Concatena as localizações numa string
                localizacao = ", ".join(loc["name"] for loc in job.get("locations", []))

                # Escreve os dados no CSV
                writer.writerow([titulo, empresa, descricao, data_publicacao, salario, localizacao])
        
        print("Dados exportados para 'trabalhos_recentes.csv' com sucesso!")

# Ponto de entrada para a aplicação Typer
if __name__ == "__main__":
    app()
