import psycopg2
# Importer les variables d'environnement
from dotenv import load_dotenv, dotenv_values 
import os
load_dotenv() 

def connexion_bdd(dbname, user, password, host="localhost", port=5432):
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
    conn, cur = connexion_bdd(os.getenv("DBNAME"), os.getenv("USERNAME"), os.getenv("PASSWORD"))
    print("Connexion réussie de la bdd")
    conn.close()
    cur.close()