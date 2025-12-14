#############################-
# Sujet : Nettoyage des détails sur les projets
# Date : 11/12/2025 - 12/12/2025
#############################-

# Chargement des librairies
import pandas as pd
import re
import numpy as np

# Chargement des données
dataset = pd.read_csv("Data/ToClean/concours_projet_1_12.csv",
            sep=";", encoding="utf-8")

print(dataset.dtypes)
print(dataset)

pattern = r'(\d[\d\s]*\s*[KM]?\s*€)'

# Création de la fonction permettant de gérer les montants avec . maps
def conversion_montant(montant):
    if not pd.isnull(montant):
        #print(montant)
        result_montant = 0
        pattern = r'\d'
        result_montant = int(''.join(re.findall(pattern, montant)))
        if "K" in montant:
            result_montant = result_montant * 1000
        elif "M" in montant:
            result_montant = result_montant * 1000000
        else:
            pass
    else:
        result_montant = np.nan

    return result_montant

def get_extract_realisation(row):
    #print(row)
    if row["REALISATION_ANNEE"]:
        
        liste_result = re.findall(r"\d{4}", row["REALISATION"])
        row["REALISATION_DEBUT"] = int(liste_result[0])
        row["REALISATION_FIN"] = int(liste_result[1])
        row["REALISATION_DUREE_MOIS"] = (row["REALISATION_FIN"] - row["REALISATION_DEBUT"]) * 12

    elif row["REALISATION_MOIS"]:
        row["REALISATION_DUREE_MOIS"] = re.findall(r"\d+", row["REALISATION"])[0]
        row["REALISATION_DEBUT"] = np.nan
        row["REALISATION_FIN"] = np.nan
    
    else:
        row["REALISATION_DUREE_MOIS"] = np.nan
        row["REALISATION_DEBUT"] = np.nan
        row["REALISATION_FIN"] = np.nan
    
    return row

def get_extract_ville(row):

    if row["VAGUE"] == 12 and not pd.isna(row["LOCALISATION"]):
        row["VILLE"] = row["LOCALISATION"].split("|")[0].strip()
    else:
        row["VILLE"] = np.nan
    
    return row

# Montant des projets + Aide des projets (extraire montant € avec le symbole K ou M)
for col in ["MONTANT_PROJET", "MONTANT_AIDE"]:

    ## Extraction Montant €
    dataset[col + "_EXTRAITE"] = dataset[col].str.extract(pattern) # pattern à utiliser pour extraire l'information

    ## Conversion en Integer (ça sera en Float car valeurs nulles présentes)
    dataset[col + "_EXTRAITE"] = dataset[col + "_EXTRAITE"].map(conversion_montant)

# Réalisation : Séparée entre deux colonnes (durée mois / durée année) (pattern extraction YYYY - YYYY et MM mois)
dataset["REALISATION_ANNEE"] = dataset["REALISATION"].str.contains(r"\d{4} - \d{4}", na=False)
dataset["REALISATION_MOIS"] = dataset["REALISATION"].str.contains(r"\d{2} mois", na=False)
dataset = dataset.apply(get_extract_realisation,axis=1)

# Localisation : Extraire région / département / ville
# Numéro de département
dataset["NUMERO_DEPARTEMENT"] = dataset["LOCALISATION"].str.findall(r"(\d{2})")

# Ville (seulement pour la vague 12 / les vagues 1 à 11 ne l'ont pas)
dataset = dataset.apply(get_extract_ville, axis=1)

# Traitement des textes obtenus dans Objectif_Projet et Activite_Entreprise
for cols in ["OBJECTIF_PROJET", "ACTIVITE_ENTREPRISE"]:
    dataset[cols] = dataset[cols].str.replace("\n", "", regex=False).str.strip()

dataset.drop(["REALISATION_ANNEE", "REALISATION_MOIS", "MONTANT_PROJET", "MONTANT_AIDE", "LOCALISATION", "REALISATION"], 
             axis=1,
             inplace=True)
#print(dataset[["OBJECTIF_PROJET", "ACTIVITE_ENTREPRISE", "MONTANT_PROJET_EXTRAITE", "MONTANT_AIDE_EXTRAITE"]].head(20))
#print(dataset[["MONTANT_PROJET_EXTRAITE", "MONTANT_AIDE_EXTRAITE"]].tail(20))

# Export en jsonl des données nettoyées
dataset.to_json(path_or_buf="Data/concours_projet.jsonl", orient="records", lines=True, force_ascii=False)