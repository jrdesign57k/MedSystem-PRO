import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

def obter_conexao():
    try:
        conexao = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        if conexao.is_connected():
            return conexao
    except Error as e:
        print(f"Erro ao conectar: {e}")
        return None