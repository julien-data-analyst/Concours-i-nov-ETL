###############################################-
# Sujet : création des différentes tables avec le script SQL
# Date : 27/12/2025
###############################################-

def create_bdd(cur, conn):
    """
    Function : create the SQL table necessary for the data insertion

    Args :
    - cur, conn : the connection to the Database PostGreSQL

    Return :
    - Tables created of the Inov Competition
    """


    # Création des différentes tables dans le script SQL
    sql_requests = open("./Load/CreateBDD/bdd_create.sql", "r").read().split(";")

    for command in sql_requests:
        command = command.strip()
        if command:
            cur.execute(command)
    conn.commit() # Pour valider les requêtes

if __name__=="__main__":
    # Importer les variables d'environnement
    import sys
    from dotenv import load_dotenv
    import os
    
    # caution: path[0] is reserved for script path (or '' in REPL)
    sys.path.insert(1, '/home/renoult-julien/Documents/concours_i_nov/Load/ConnexionBDD')
    import connexion as bdd_conn
    load_dotenv() 

    # Connexion à la bdd pour créer les différentes tables
    #print(os.getenv("DBNAME"), os.getenv("DBUSERNAME"), os.getenv("DBPASSWORD"))
    if os.getenv("DBEXTERNALURL") != "":
        conn, cur = bdd_conn.connexion_bdd(database_url=os.getenv("DBEXTERNALURL"))
    else:
        conn, cur = bdd_conn.connexion_bdd(os.getenv("DBNAME"), os.getenv("DBUSERNAME"), os.getenv("DBPASSWORD"))

    create_bdd(conn, cur)

    # Fermer les instances de connexion
    cur.close()
    conn.close()