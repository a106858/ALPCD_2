import requests
import typer
import json

url = "https://api.itjobs.pt/job/list.json?api_key=09ad1042ebaf1704533805cd2fab64f1"

headers = {
    "User-Agent":""
}

response = requests.get(url, headers=headers)
data = response.json()

# Inicializa o Typer
app = typer.Typer()

@app.command()
def buscar_empresa(
    nome_da_empresa: str,
    localizacao_desejada: str,
    limite_resultados: int = typer.Argument(1, help="Número máximo de resultados a exibir"),
):
   
    # Remove espaços e transforma para minúsculas
    nome_da_empresa = nome_da_empresa.lower()
    localizacao_desejada = localizacao_desejada.lower()

    # Lista para armazenar todas as informações relacionadas à empresa
    empresas_relacionadas = []

    # Procura a empresa pelo nome e obtém o `companyId`
    company_id = None
    for item in data["results"]:
        # Remove espaços e converte para minúsculas o nome da empresa no JSON
        nome_da_empresa_json = (item["company"]["name"]).lower()
        
        # Compara o nome formatado do JSON com o nome fornecido pelo usuário
        if nome_da_empresa_json == nome_da_empresa:
            company_id = item["company"]["id"]
            
            # Verifica se há "Full-time" em `types` e se a localização desejada existe em `locations`
            has_full_time = any(t["name"] == "Full-time" for t in item.get("types", []))
            has_location = any(l["name"].lower() == localizacao_desejada for l in item.get("locations", []))
            
            # Se encontrar "Full-time" e a localização desejada, adiciona à lista
            if has_full_time and has_location:
                empresas_relacionadas.append(item)

    # Se encontrar o `companyId`, busca todas as empresas com o mesmo ID, "Full-time" e localização
    if company_id:
        for item in data["results"]:
            if item["company"]["id"] == company_id:
                # Verifica se há "Full-time" em `types` e se a localização corresponde
                has_full_time = any(t["name"] == "Full-time" for t in item.get("types", []))
                has_location = any(l["name"].lower() == localizacao_desejada for l in item.get("locations", []))
                
                # Se encontrar "Full-time" e a localização desejada, adiciona
                if has_full_time and has_location and item not in empresas_relacionadas:
                    empresas_relacionadas.append(item)
        
        # Aplica o limite de resultados
        empresas_relacionadas = empresas_relacionadas[:limite_resultados]

        # Exibe os resultados em formato JSON
        if empresas_relacionadas:
            print(json.dumps(empresas_relacionadas, indent=4, ensure_ascii=False))
        else:
            print(f"Nenhuma empresa com 'Full-time' e localização '{localizacao_desejada}' encontrada para '{nome_da_empresa}'.")
    else:
        print(f"Empresa '{nome_da_empresa}' não encontrada.")

# Executa o Typer
if __name__ == "__main__":
    app()