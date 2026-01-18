import psycopg2
# Importer les variables d'environnement
from dotenv import load_dotenv, dotenv_values 
import os
load_dotenv() 

def connexion_bdd(dbname="", user="", password="", host="localhost", port=5432, database_url=""):

    if database_url != "":
        # Connect to your postgres DB on a website (Render for example)
        conn = psycopg2.connect(
            dsn=database_url,
            sslmode="require"
        )
    else:
        # Connect to your postgres DB
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )

    # Open a cursor to perform database operations
    cur = conn.cursor()

    return conn, cur


if __name__=="__main__":
    conn, cur = connexion_bdd(database_url=os.getenv("DBEXTERNALURL"))
    print("Connexion réussie de la bdd")
    conn.close()
    cur.close()