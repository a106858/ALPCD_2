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


if __name__ == "__main__":
    app()