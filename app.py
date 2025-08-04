from dotenv import load_dotenv
import os
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.utilities import SQLDatabase
from langchain_community.vectorstores import Chroma


load_dotenv()
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
db_port = os.getenv("DB_PORT")
def create_db_connection():
    return SQLDatabase.from_uri(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
    
db=create_db_connection()
print(db.dialect)
print(db.get_usable_table_names())
print(db.table_info)
