import requests
from collections import defaultdict
from fpdf import FPDF

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
            dados_estruturados[localizacao][empresa].append({
                "titulo": titulo,
                "email": job.get("company", {}).get("email", "N/A"),
                "url": job.get("company", {}).get("url", "N/A"),
            })
    return dados_estruturados

def exibir_trabalhos_no_terminal(dados_estruturados):
    for localizacao, empresas in dados_estruturados.items():
        print(f"\nLocalização: {localizacao}")
        for empresa, titulos in empresas.items():
            print(f"            Empresa: {empresa}")
            for trabalho in titulos:
                print(f"                    Trabalho: {trabalho['titulo']}")

def exportar_para_pdf(dados_estruturados, nome_arquivo="trabalhos_por_localidade.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", size=12)

    pdf.cell(200, 10, txt="Trabalhos Organizados por Localidade", ln=True, align="C")
    
    for localizacao, empresas in dados_estruturados.items():
        pdf.ln(10)
        
        pdf.set_font("Arial", size=11)
        pdf.cell(0, 10, txt=f"Localização: {localizacao}", ln=True)
        
        for empresa, titulos in empresas.items():
            pdf.set_font("Arial", size=11)
            pdf.cell(2)
            pdf.cell(0, 8, txt=f"                     Empresa: {empresa}", ln=True)
            
            for trabalho in titulos:
                pdf.set_font("Arial", size=10)
                pdf.cell(6)
                pdf.cell(0, 6, txt=f"                                        Trabalho: {trabalho['titulo']}", ln=True)
            
            for trabalho in titulos:
                pdf.set_font("Arial", size=10)
                pdf.cell(6)
                pdf.cell(0, 6, txt=f"                                        email: {trabalho['email']}", ln=True)
                pdf.cell(6)
                pdf.cell(0, 6, txt=f"                                        url: {trabalho['url']}", ln=True)
    
    pdf.output(nome_arquivo)
    print(f"Dados exportados para '{nome_arquivo}' com sucesso!")

if __name__ == "__main__":
    trabalhos = obter_trabalhos()
    dados_estruturados = organizar_trabalhos_por_localidade(trabalhos)
    exibir_trabalhos_no_terminal(dados_estruturados)
    exportar_para_pdf(dados_estruturados)
