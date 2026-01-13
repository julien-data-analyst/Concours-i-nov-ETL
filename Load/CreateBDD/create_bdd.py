###############################################-
# Sujet : création des différentes tables avec le script SQL
# Date : 27/12/2025
###############################################-

# Chargement des librairies
# some_file.py
import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/home/renoult-julien/Documents/concours_i_nov/Load/ConnexionBDD')
import connexion as bdd_conn

# Importer les variables d'environnement
from dotenv import load_dotenv, dotenv_values 
import os
load_dotenv() 

# Connexion à la bdd pour créer les différentes tables
#print(os.getenv("DBNAME"), os.getenv("DBUSERNAME"), os.getenv("DBPASSWORD"))
conn, cur = bdd_conn.connexion_bdd(os.getenv("DBNAME"), os.getenv("DBUSERNAME"), os.getenv("DBPASSWORD"))

# Création des différentes tables dans le script SQL
sql_requests = open("./Load/CreateBDD/bdd_create.sql", "r").read().split(";")

for command in sql_requests:
    command = command.strip()
    if command:
        cur.execute(command)
conn.commit() # Pour valider les requêtes

# Pour vérifier si ça a marché
#cur.execute("SELECT * FROM Publisher;")
#print(cur.fetchall())

# Fermer les instances de connexion
cur.close()
conn.close()