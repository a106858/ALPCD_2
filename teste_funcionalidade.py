import requests
from bs4 import BeautifulSoup

headers = {    
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Fire-fox/98.0', 
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,/;q=0.8',
        'Accept-Language':'en-US,en;q=0.5', 
        'Accept-Encoding': 'gzip, deflate', 
        'Connection': 'keep-alive', 
        'Upgrade-Insecure-Requests': '1', 
        'Sec-Fetch-Dest':'document', 
        'Sec-Fetch-Mode': 'navigate', 
        'Sec-Fetch-Site': 'none', 
        'Sec-Fetch-User': '?1', 
        'Cache-Control': 'max-age=0'}

def request_website(url):
    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            return soup
        else:
            print(f"Erro {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return None
    
soup = request_website(f'https://www.ambitionbox.com/jobs/application-developer-jobs-prf?rid=naukri_271224916613')
a=soup.find_all('a',class_="body-medium chip")
print(a)
urls=soup.find_all('div',class_="jobsInfoCardCont")