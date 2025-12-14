import pandas as pd
import math

projets = pd.read_json(path_or_buf="Data/concours_projet_dep_reg.jsonl", lines=True,encoding="utf-8",orient="records")
concours = pd.read_json(path_or_buf="Data/concours.jsonl", lines=True,encoding="utf-8",orient="records")

# Filtrage sur ceux qui ont des années de réalisations nulles
projets_without_years = projets[(projets["REALISATION_DEBUT"].isna()) & (projets["REALISATION_FIN"].isna()) & (~projets["REALISATION_DUREE_MOIS"].isna())]

concours["Parution"] = concours["Parution"].astype("str")

def calculer_realisation_annee(row):

    vague = row["VAGUE"]
    concours_row = concours[concours["Vague"] == vague]
    annee_parution = int(concours_row["Parution"].values[0].split(".")[1])

    row["REALISATION_DEBUT"] = annee_parution
    row["REALISATION_FIN"] = annee_parution + (int(math.ceil(row["REALISATION_DUREE_MOIS"] / 12)))

    return row

projets_without_years = projets_without_years.apply(calculer_realisation_annee, axis=1)
projets[(projets["REALISATION_DEBUT"].isna()) & (projets["REALISATION_FIN"].isna()) & (~projets["REALISATION_DUREE_MOIS"].isna())] = projets_without_years

# Exporter le nouveau Dataframe
projets.to_json(path_or_buf="Data/concours_projet_realisation.jsonl", orient="records", lines=True, force_ascii=False)
