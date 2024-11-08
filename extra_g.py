import requests
from collections import defaultdict

URL = "https://api.itjobs.pt/job/list.json?api_key=09ad1042ebaf1704533805cd2fab64f1"
headers = {"User-Agent": ""}

def obter_trabalhos():
    response = requests.get(URL, headers=headers)
    return response.json().get("results", [])

def organizar_trabalhos_por_localidade(trabalhos):
    
    dados_estruturados = defaultdict(lambda: defaultdict(list))

    for job in trabalhos:
        titulo = job.get("title", "N/A")
        empresa = job.get("company", {}).get("name", "N/A")
        
        # Obter todas as localidades associadas ao trabalho
        localizacoes = [loc["name"] for loc in job.get("locations", [])]
        
        # Estrutura de dados: Localidade -> Empresa -> Lista de Títulos dos Trabalhos
        for localizacao in localizacoes:
            dados_estruturados[localizacao][empresa].append(titulo)
    
    return dados_estruturados

def exibir_trabalhos_no_terminal(dados_estruturados):
    
    for localizacao, empresas in dados_estruturados.items():
        print(f"\nLocalização: {localizacao}")
        for empresa, titulos in empresas.items():
            print(f"            Empresa: {empresa}")
            for titulo in titulos:
                print(f"                    Trabalho: {titulo}")

if __name__ == "__main__":
    trabalhos = obter_trabalhos()
    dados_estruturados = organizar_trabalhos_por_localidade(trabalhos)
    exibir_trabalhos_no_terminal(dados_estruturados)
