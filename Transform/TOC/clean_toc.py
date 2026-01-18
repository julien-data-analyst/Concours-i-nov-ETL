#############################-
# Sujet : Nettoyage des données concours sur le sommaire
# Date : 06/12/2025
#############################-
# Chargement des librairies
import pandas as pd

def clean_toc():
   

    # Chargement des données
    dataset = pd.read_csv("Data/ToClean/concours_inov_1_12_toc.csv",
                sep=";", encoding="utf-8")

    #print(dataset.dtypes)
    #print(dataset)

    # Nettoyage chaîne de cractères
    colonnes_chr = [col for col in dataset.columns if dataset[col].dtype == "object"]
    #print(colonnes_chr)

    ## Enlevers les espaces en trop
    for col in colonnes_chr:
        dataset[col] = dataset[col].str.strip().str.lower()
        if col == "PAGE":
            dataset[col] = dataset[col].astype("int32")

    #print(dataset.head(20))
    #print(dataset.tail(20))

    # Export en jsonl des données nettoyées
    dataset.to_json(path_or_buf="Data/concours_toc.jsonl", orient="records", lines=True, force_ascii=False)