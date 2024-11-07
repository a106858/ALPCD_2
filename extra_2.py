import requests
import typer
import json

url = "https://api.itjobs.pt/job/list.json?api_key=09ad1042ebaf1704533805cd2fab64f1"

headers = {
    "User-Agent": ""
}

response = requests.get(url, headers=headers)
data = response.json()

app = typer.Typer()

@app.command()
def remote_jobs(
    location_: str = typer.Argument(..., help="Localização da empresa"),
    contract_: str = typer.Argument(..., help="Tipo de contrato desejado"),
):

    location_ = location_.lower()
    contract_ = contract_.lower()

    # Variável para verificar se encontrou algum trabalho
    found = False

    # Iterando sobre as vagas na API
    for job in data["results"]:
        # Verificar se o trabalho permite remoto e se a localização e contrato estão nos critérios
        job_locations = [loc["name"].lower() for loc in job.get("locations", [])]
        job_contracts = [contract["name"].lower() for contract in job.get("contracts", [])]
        
        # Verificação adicional para allowRemote
        if job.get("allowRemote") == True and location_ in job_locations and contract_ in job_contracts:
            print(f"Trabalho remoto encontrado: {job['title']} na empresa {job['company']['name']}")
            found = True

    if not found:
        print("Nenhum trabalho remoto encontrado para os critérios especificados.")

if __name__ == "__main__":
    app()
