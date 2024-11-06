import requests
import typer
import json
from datetime import datetime
import csv

# Inicializa Typer para a CLI
app = typer.Typer()

# URL completa com a chave de API embutida
URL = "https://api.itjobs.pt/job/list.json?api_key=09ad1042ebaf1704533805cd2fab64f1"

headers={
    "User-Agent":""
}

@app.command()

def listar_trabalhos(n: int = typer.Argument(10, help="Número de trabalhos para listar")):
    """
    Lista os N trabalhos mais recentes publicados pela itjobs.pt.
    """
    # Faz a requisição GET para a API
    response = requests.get(URL,headers=headers)
        
    # Processa a resposta da API em formato JSON
    jobs = response.json().get("results", [])
        
    # Ordena os trabalhos pela data de publicação de forma decrescente (mais recentes primeiro)
    jobs_sorted = sorted(jobs, key=lambda job: datetime.strptime(job["publishedAt"], "%Y-%m-%d %H:%M:%S"), reverse=True)
        
    # Seleciona apenas os N trabalhos mais recentes
    jobs_most_recent = jobs_sorted[:n]
    
    # Exibe a lista de trabalhos no terminal em formato JSON
    print(json.dumps(jobs_most_recent, ensure_ascii=False, indent=2))
    
    # Exporta automaticamente para CSV
    with open("trabalhos.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Escreve o cabeçalho no CSV
        writer.writerow(["Título", "Empresa", "Descrição", "Data de Publicação", "Salário", "Localização"])

        for job in jobs_most_recent:
            titulo = job.get("title", "N/A")
            empresa = job.get("company", {}).get("name", "N/A")
            descricao = job.get("body", "N/A")
            data_publicacao = job.get("publishedAt", "N/A")
            salario = job.get("wage", "N/A")
            
            # Concatena as localizações em uma string
            localizacao = ", ".join(loc["name"] for loc in job.get("locations", []))

            # Escreve os dados da vaga no CSV
            writer.writerow([titulo, empresa, descricao, data_publicacao, salario, localizacao])
    
    print("Dados exportados automaticamente para 'trabalhos.csv' com sucesso!")

# Ponto de entrada para a aplicação Typer
if __name__ == "__main__":
    app()
