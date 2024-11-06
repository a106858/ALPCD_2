import requests
import typer
import json
from datetime import datetime

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

# Ponto de entrada para a aplicação Typer
if __name__ == "__main__":
    app()
