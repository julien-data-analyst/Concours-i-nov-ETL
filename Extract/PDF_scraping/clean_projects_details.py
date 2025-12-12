#############################-
# Sujet : Nettoyage des détails sur les projets
# Date : 11/12/2025 - 12/12/2025
#############################-

# Chargement des librairies
import pandas as pd

# Chargement des données
dataset = pd.read_csv("Data/ToClean/concours_projet_1_12.csv",
            sep=";", encoding="utf-8")

print(dataset.dtypes)
print(dataset)

pattern = r'(\d[\d\s]*\s*[KM]?\s*€)'
# Montant des projets + Aide des projets (extraire montant € avec le symbole K ou M)
for col in ["MONTANT_PROJET", "MONTANT_AIDE"]:

    ## Extraction Montant €
    dataset[col + "_EXTRAITE"] = dataset[col].str.extract(pattern) # pattern à utiliser pour extraire l'information

    ## Conversion en Montant
    #

# Réalisation : Séparée entre deux colonnes (durée mois / durée année) (pattern extraction YYYY - YYYY et MM mois)
#

# Localisation : Extraire région / département / ville
#

# Traitement des textes obtenus dans Objectif_Projet et Activite_Entreprise
for cols in dataset.columns[len(dataset.columns)-2:]:
    dataset[cols] = dataset[cols].str.replace("\n", "")

print(dataset[["OBJECTIF_PROJET", "ACTIVITE_ENTREPRISE", "MONTANT_PROJET_EXTRAITE", "MONTANT_AIDE_EXTRAITE"]].head(20))
print(dataset[["MONTANT_PROJET_EXTRAITE", "MONTANT_AIDE_EXTRAITE"]].tail(20))

# Export en jsonl des données nettoyées
dataset.to_json(path_or_buf="Data/concours_projet.jsonl", orient="records", lines=True, force_ascii=False)