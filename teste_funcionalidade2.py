import requests
from bs4 import BeautifulSoup

def list_skills(job_title: str):
    # Substitui espaços por hífens e converte para minúsculas
    formatted_job_title = job_title.lower().replace(' ', '-')
    
    # Cria o URL para a busca do trabalho
    url = f"https://www.ambitionbox.com/jobs/{formatted_job_title}-jobs-prf"
    print(f"Constructed URL: {url}")  # Debug: Print do URL

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,/;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0"
    }

    try:
        # Envia a requisição HTTP GET
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Levanta uma exceção em caso de erro HTTP

        # Faz o parsing do HTML
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Depuração: Imprimir as partes coletadas
        print("\nFetched HTML (prettified):")
        # print(soup.prettify())  # Caso queira ver todo o HTML

        # Seletores separados por vírgulas:
        skills_elements = soup.select('div.ab_checkbox, label, div.text-wrap, span.label')
        counts_elements = soup.select('div.ab_checkbox, label, div.text-wrap, span:nth-of-type(2)')

        # Depuração: Imprimir as partes coletadas
        print("\nFirst 10 'skills' and 'counts' (separated by commas):")
        
        # Limitar a 10 primeiros
        first_10_skills = skills_elements[:10]
        first_10_counts = counts_elements[:10]

        # Separando por vírgula e mostrando as skills
        skills = [skill.get_text(strip=True) for skill in first_10_skills]
        counts = [count.get_text(strip=True).strip('()') for count in first_10_counts]

        # Depuração: Mostrar as listas antes de processar
        print(f"Skills (raw): {skills}")
        print(f"Counts (raw): {counts}")

        # Tentar converter as contagens para inteiros e filtrar apenas as válidas
        valid_counts = []
        for count in counts:
            try:
                # Tenta converter para int
                valid_counts.append(int(count))
            except ValueError:
                # Se não for um número válido, ignora
                continue

        # Apenas as primeiras 10 skills e contagens válidas
        skills_data = list(zip(skills[:len(valid_counts)], valid_counts))

        # Mostrar os resultados processados
        print("\nExtracted skills and counts (first 10):")
        for skill, count in skills_data:
            print(f"Skill: {skill}, Count: {count}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Exemplo de uso
list_skills("data scientist")
