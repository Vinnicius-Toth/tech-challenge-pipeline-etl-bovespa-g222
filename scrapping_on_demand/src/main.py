from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import boto3
import pytz
import pandas as pd
import time, os
import logging
from io import StringIO
from datetime import datetime


class Logs:
    def __init__(self, name="glue_job"):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        self.logger = logging.getLogger(name)

    def info(self, msg):
        self.logger.info(msg)

    def error(self, msg):
        self.logger.error(msg)
        raise Exception(msg)
    

def get_file_name():
    tz = pytz.timezone('America/Sao_Paulo')
    today_str = datetime.now(tz).strftime("%Y%m%d")

    return f"{today_str}_raw_file.csv"

def extract_selenium_scrapping(ingestion_type):
    try:
        if ingestion_type == 'daily':
            url = "https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBOV?language=pt-br"
        elif ingestion_type == 'quarter':
            url = "https://sistemaswebb3-listados.b3.com.br/indexPage/theorical/IBOV?language=pt-br"
        
        log.info(f"Start extract with scrapping - {url}")

        service = Service()  
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
        table = soup.find("table", class_="table table-responsive-sm table-responsive-md")

        log.info(f"Extract with scrapping in Ibovespa was suceffuly - {url}")
        return table
    
    except Exception as e:
        log.error(f"Error while scrapping in Ibovespa - {e}")

def extract_table_data(table, ingestion_type):
    """
    Extrai a tabela HTML para DataFrame e adiciona coluna tipo_ingestao
    """
    try:
        log.info(f"Format table in csv file - {ingestion_type}")
        header = [th.get_text(strip=True) for th in table.find("thead").find_all("th")]
        rows = table.find("tbody").find_all("tr")
        data = []
        for row in rows:
            cols = row.find_all("td")
            if cols:
                data.append([col.get_text(strip=True) for col in cols])
        df = pd.DataFrame(data, columns=header)
        df["ingestion_type"] = ingestion_type
        return df
    
    except Exception as e:
        log.error(f"Error while format table in csv file - {e}")

def save_dataframe_to_s3(df, bucket, path_s3):
    try:
    
        load_dotenv() 
        aws_access_key = os.getenv("aws_access_key_id")
        aws_secret_key = os.getenv("aws_secret_access_key")
        aws_session_token = os.getenv("aws_session_token")

        s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            aws_session_token=aws_session_token
        )

        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)

        s3.put_object(
            Bucket=bucket,
            Key=path_s3,
            Body=csv_buffer.getvalue()
        )
        log.info(f"Csv file save was sucessfuly - {bucket}/{path_s3}")

    except Exception as e:
        log.error(f"Error while save csv file in Bucket S3 - {e}")

def process_tables_and_upload(bucket_name, path_s3):
    """
    Execute ingestion ETL in raw path
    """

    ## Extract
    table_daily = extract_selenium_scrapping("daily")
    table_quarter = extract_selenium_scrapping("quarter")
    
    ## Transform
    df_daily = extract_table_data(table_daily, "daily")
    df_quarter = extract_table_data(table_quarter, "quarter")
    df_final = pd.concat([df_daily, df_quarter], ignore_index=True)

    ## Load
    save_dataframe_to_s3(df_final, bucket_name, path_s3)


if __name__ == '__main__':
    # Parameters
    bucket_s3 = 'bucket-techchallenge-ingestao-bovespa-g222'
    path_s3 = get_file_name()
    
    # Log config
    global log
    log = Logs()

    # Start Ingestion
    process_tables_and_upload(bucket_s3, path_s3)