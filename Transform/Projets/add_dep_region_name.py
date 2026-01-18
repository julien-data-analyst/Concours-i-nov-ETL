import pandas as pd

def add_dep_region_name():
    departements_regions = pd.read_json("./Data/departements-region.json")
    departements_regions['num_dep'] = departements_regions['num_dep'].astype("str")
    projets = pd.read_json(path_or_buf="Data/concours_projet.jsonl", lines=True,encoding="utf-8",orient="records")

    #print(projets)
    #print(departements_regions)

    def get_reg_dep_name(row):

        row["DEPARTEMENT"] = []
        row["REGION"] = []

        if type(row["NUMERO_DEPARTEMENT"]) == list :
            #print(row)
            # The list of department of the project
            list_dep = row["NUMERO_DEPARTEMENT"]


            for num_dep in list_dep:
                ligne_concernee = departements_regions[departements_regions["num_dep"] == num_dep]
                if len(ligne_concernee["dep_name"].values) > 0:
                    row["DEPARTEMENT"].append(ligne_concernee["dep_name"].values[0])
                    row["REGION"].append(ligne_concernee["region_name"].values[0])
                
        else:
            row["NUMERO_DEPARTEMENT"] = []

        return row

    projets = projets.apply(get_reg_dep_name, axis=1)

    # Exporter le nouveau Dataframe
    projets.to_json(path_or_buf="Data/concours_projet_dep_reg.jsonl", orient="records", lines=True, force_ascii=False)