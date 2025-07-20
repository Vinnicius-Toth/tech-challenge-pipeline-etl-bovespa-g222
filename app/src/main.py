from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import time
import csv

# Quadrimestre - Carteira teórica do IBovespa válida para o quadrimestre Mai. a Ago. 2025
url = "https://sistemaswebb3-listados.b3.com.br/indexPage/theorical/IBOV?language=pt-br"

# Diário - Carteira Teórica do IBovespa válida para 21/07/25
# url = "https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBOV?language=pt-br"

service = Service()  # Use o caminho do chromedriver se necessário
driver = webdriver.Chrome(service=service)
driver.get(url)
time.sleep(3)  # Aguarde o carregamento inicial

# Seleciona o máximo de itens (120) no select
select_element = driver.find_element(By.ID, "selectPage")
select = Select(select_element)
select.select_by_visible_text("120")
time.sleep(3)  # Aguarde a página atualizar

html = driver.page_source
driver.quit()

soup = BeautifulSoup(html, "html.parser")
tabela = soup.find("table", class_="table table-responsive-sm table-responsive-md")

import os
# ...existing code...

if tabela:
    cabecalhos = [th.get_text(strip=True) for th in tabela.find("thead").find_all("th")]
    linhas = tabela.find("tbody").find_all("tr")
    dados = []
    for linha in linhas:
        colunas = linha.find_all("td")
        if colunas:
            dados.append([coluna.get_text(strip=True) for coluna in colunas])
    # Garante que o diretório de saída existe
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "IBOV_dados.csv")
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(cabecalhos)
        writer.writerows(dados)
    print(f"Dados salvos em {output_path}")
else:
    print("Tabela não encontrada.")