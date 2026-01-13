###############################################-
# Sujet : Insertion des données dans la bdd
# Date : 27/12/2025
###############################################-
import pandas as pd
import numpy as np
# some_file.py
import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/home/renoult-julien/Documents/concours_i_nov/Load/ConnexionBDD')
import connexion as bdd_conn
# Importer les variables d'environnement
from dotenv import load_dotenv, dotenv_values 
import os
load_dotenv() 

###################################################-
# 1ère partie : insertion des concours et éditeurs
###################################################-

# Lecture des données
concours_i_nov = pd.read_json(path_or_buf="Data/concours.jsonl", lines=True,
                        encoding="utf-8",orient="records",
                        dtype={"Parution" : "string"})
editeur = concours_i_nov[["Editeurs", "Editeurs_URL"]]
concours = concours_i_nov.drop(["Editeurs", "Editeurs_URL"], axis=1)
projets = pd.read_json(path_or_buf="Data/concours_projet_thematique.jsonl", lines=True,
                        encoding="utf-8",orient="records")
#print(concours)
#print(editeur)

# Ouverture de la bdd
conn, cur = bdd_conn.connexion_bdd(os.getenv("DBNAME"), os.getenv("DBUSERNAME"), os.getenv("DBPASSWORD"))

################
# Pour la table Publisher
################
# Vérifier s'il n'y a pas déjà des lignes insérées
cur.execute("SELECT * FROM publisher LIMIT 10;")
result = cur.fetchall()
#print(result)

if result == []:
    # Récupérer le nom des éditeurs uniques et leurs URL associées
    dict_editeur_url = {}

    # Parcourir ligne dans éditeur
    for lign in editeur.values:
        # Parcourir chaque éditeur du concour et ajouter ceux qui ne sont pas dans le dictionnaire
        #print(lign)
        #print(type(lign["Editeurs"]))
        id = 1
        for ind in range(len(lign[0])):
            if not lign[0][ind] in dict_editeur_url.keys():
                dict_editeur_url[lign[0][ind]] = [lign[1][ind], id]
                id += 1

    #print(dict_editeur_url)

    # Insérer dans la table éditeur
    for edit in dict_editeur_url:
        cur.execute("INSERT INTO Publisher (id, name, web_url) VALUES (%s, %s, %s);",
                    (dict_editeur_url[edit][1], edit, dict_editeur_url[edit][0]))
    # Vérifier résultat
    #cur.execute("SELECT * FROM Publisher;")
    #print(cur.fetchone())

################
################

################
# Pour la table Competition
################
# Vérifier s'il n'y a pas déjà des lignes insérées
cur.execute("SELECT * FROM competition LIMIT 10;")
result = cur.fetchall()
#print(result)

if result == []:
    # Insertion des concours
    # INSERT INTO Competition (vague, titre, web_url, pdf_url, description, presentation, parution)
    concours["Parution"] = pd.to_datetime(concours["Parution"], format="%m.%Y").dt.date

    # Parcourir chaque ligne et insérer les valeurs
    #print(concours.values)
    for elt in concours.values:
        cur.execute("INSERT INTO Competition (vague, titre, web_url, pdf_url, description, presentation, parution) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                        (elt[2], elt[0], elt[1], elt[6], elt[5], elt[3], elt[4]))
################
################

################
# Pour la table competition_publisher
################

# Vérifier s'il n'y a pas déjà des lignes insérées
cur.execute("SELECT * FROM competition_publisher LIMIT 10;")
result = cur.fetchall()

if result == []:
    competition_publisher = [] # liste de tuples

    # Get the ID for the competition and the publisher ids
    #print(concours_i_nov.dtypes)
    for lign in concours_i_nov[["Vague", "Editeurs"]].values:
        id_vague = lign[0]

        for ed in lign[1]:
            cur.execute("SELECT id FROM Publisher WHERE name=%s;",
                        (ed,))
            id_editeur = cur.fetchone()[0]

            cur.execute("INSERT INTO Competition_Publisher (id_pu, vague_comp) VALUES (%s, %s);",
                        (id_editeur, id_vague))
        
################
################

################
# Pour la table region
################
regions = projets["REGION"]
# Récupérer toutes les régions uniques qui existent
liste_regions = []
for value in regions.values:

    for elt in value:
        if not elt in liste_regions:
            liste_regions.append(elt)

# Vérifier s'il n'y a pas déjà des lignes insérées
cur.execute("SELECT * FROM Region LIMIT 1;")
result = cur.fetchall()

if result == []:

    for reg in liste_regions:
            cur.execute("INSERT INTO Region (name) VALUES (%s);",
                        (reg,))
################
################

################
# Pour la table company
################
# Grouper et concaténer l'activité de l'entreprise
entreprise_activite = projets[["ENTREPRISE", "ACTIVITE_ENTREPRISE"]].groupby("ENTREPRISE", as_index=False).agg({
    "ACTIVITE_ENTREPRISE" : lambda x: " \n ".join(x.dropna())
})

# Tout est unique, il ne reste plus qu'à insérer
# Vérifier s'il n'y a pas déjà des lignes insérées
cur.execute("SELECT * FROM Company LIMIT 1;")
result = cur.fetchall()

if result == []:

    for ent_act in entreprise_activite.values:
            cur.execute("INSERT INTO Company (name, activity) VALUES (%s, %s);",
                        (ent_act[0], ent_act[1]))
################
################

################
# Pour la table department
################
cur.execute("SELECT * FROM Department LIMIT 1;")
result = cur.fetchall()

if result == []:
     
    departement_region = projets[["REGION", "DEPARTEMENT", "NUMERO_DEPARTEMENT"]]
    #print(departement_region)

    # {REGION : [CLE_ETRANGERE, {DEPARTEMENT : NUMERO, 
    #                            etc                       }
    # ] }

    departement_region_keys = {
    }

    # Récupérer les différents départements et les relier avec la clé étrangère de la région
    for localisation in departement_region.values:
         
        for ind in range(len(localisation[0])):
              # Si la région n'a pas déjà été créé
              if not localisation[0][ind] in departement_region_keys:
                   # Récupérer sa clé étrangère
                   cur.execute("SELECT id FROM Region WHERE name=%s;", (localisation[0][ind],))
                   cle_etrangere = cur.fetchone()[0]
                   
                   # Ajouter dans le dictionnaire
                   departement_region_keys[localisation[0][ind]] = [cle_etrangere, {}]

              # Aller sur le département et l'ajouter dans le dictionnaire dans la liste correspondante à la région
              departement_region_keys[localisation[0][ind]][1][localisation[1][ind]] = localisation[2][ind]
    
    #print(departement_region_keys)

    # Insérer maintenant dans la BDD
    for region in departement_region_keys:
            # Récupérer clé étrangère
            cle_etrangere = departement_region_keys[region][0]

            # Parcourir les départements de cette région
            for dep in departement_region_keys[region][1]:
                cur.execute("INSERT INTO Department (name, dep_number, id_reg) VALUES (%s, %s, %s);",
                            (dep, departement_region_keys[region][1][dep], cle_etrangere))

################
################

################
# Pour la table theme
################
theme_theme_gen = projets[["THEMATIQUE", "THEMATIQUE_GENERALE"]].drop_duplicates(keep='first', ignore_index=True)

# Tout est unique, il ne reste plus qu'à insérer
# Vérifier s'il n'y a pas déjà des lignes insérées
cur.execute("SELECT * FROM Theme LIMIT 1;")
result = cur.fetchall()

if result == []:

    for theme_theme_gen_elt in theme_theme_gen.values:
            cur.execute("INSERT INTO Theme (theme, general_theme) VALUES (%s, %s);",
                        (theme_theme_gen_elt[0].strip(), theme_theme_gen_elt[1]))
################
################

################
# Pour la table project
################
cur.execute("SELECT * FROM Project LIMIT 1;")
result = cur.fetchall()

if result == []:
    cur.execute("SELECT id, theme FROM Theme;")
    id_them = pd.DataFrame(cur.fetchall(), columns=["id_theme", "THEMATIQUE"])
    #print(id_them)

    cur.execute("SELECT id, name FROM Company;")
    id_comp = pd.DataFrame(cur.fetchall(), columns=["id_company", "ENTREPRISE"])
    #print(id_comp)

    # Faire la jointure entre leurs valeurs avec le DataFrame pour récupérer les id des clés étrangères
    projets = pd.merge(projets, id_them, how="left", on="THEMATIQUE")
    projets = pd.merge(projets, id_comp, how='left', on="ENTREPRISE")

    projets = projets[["PROJET", "PAGE", "OBJECTIF_PROJET", "MONTANT_PROJET_EXTRAITE", "MONTANT_AIDE_EXTRAITE", 
                    "REALISATION_DEBUT", "REALISATION_FIN", "REALISATION_DUREE_MOIS", "VAGUE", "id_theme", "id_company"]]

    #print(projets)

    # Plus qu'à faire l'insertion dans la BDD
    for projet in projets.values:
        projet[3] = int(projet[3]) if pd.isna(projet[3]) == False else None
        projet[4] = int(projet[4]) if pd.isna(projet[4]) == False else None
        projet[5] = int(projet[5]) if pd.isna(projet[5]) == False else None
        projet[6] = int(projet[6]) if pd.isna(projet[6]) == False else None
        projet[7] = int(projet[7]) if pd.isna(projet[7]) == False else None
        #print(projet)
        cur.execute("INSERT INTO Project (name, pdf_page, description, project_amount, " \
        "project_allowance, beginning_year, ending_year, month_dury, vague, id_them, id_comp) VALUES (%s, %s, %s, %s, " \
        "%s, %s, %s, %s, %s, %s, %s);", projet)
     
################
################

################
# Pour la table location
################

################
################
conn.commit()

cur.close()
conn.close()
