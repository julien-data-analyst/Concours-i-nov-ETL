##############################-
# Sujet : Extraction en détails des projets du concours i-nov
# Date : 11/12/2025
#############################-

# Chargement des librairies
if __name__=="__main__":
    import extract_data_inov_1_6 as inov16
    import extract_data_inov_7_10 as inov710
    import extract_data_inov_11_12 as inov1112
else:
    import Extract.PDF_scraping.extract_data_inov_1_6 as inov16
    import Extract.PDF_scraping.extract_data_inov_7_10 as inov710
    import Extract.PDF_scraping.extract_data_inov_11_12 as inov1112
import pandas as pd
import pymupdf

# Extraire les informations sur tous les projets
def extract_projets(df):

    chemins_pdf = [
    "Data/PDF_files/i-nov-palmar-s-vague-1-19087.pdf",
    "Data/PDF_files/i-nov---palmar-s-vague-2-19084.pdf",
    "Data/PDF_files/i-nov-palmar-s-vague-3-19081.pdf",
    "Data/PDF_files/i-nov---palmar-s-vague-4-19078.pdf",
    "Data/PDF_files/i-nov---palmar-s-vague-5-19075.pdf",
    "Data/PDF_files/i-nov---palmar-s-vague-6-19072.pdf",
    "Data/PDF_files/i-nov---palmar-s-vague-7-19066.pdf",
    "Data/PDF_files/i-nov---palmar-s-vague-8-19069.pdf",
    "Data/PDF_files/i-nov---palmar-s-vague-9-28604.pdf",
    "Data/PDF_files/i-nov---palmar-s-vague-10-28601.pdf",
    "Data/PDF_files/i-nov---palmar-s-vague-11-37360.pdf",
    "Data/PDF_files/i-nov---palmar-s-vague-12-37363.pdf"
    ]

    # for each lines, track the data we can have
    dict_donnees = {
        "LOCALISATION" : [],
        "MONTANT_PROJET" : [],
        "MONTANT_AIDE" : [],
        "REALISATION" : [],
        "ACTIVITE_ENTREPRISE" : [],
        "OBJECTIF_PROJET" : []
    }

    for lines in df.values:
        #print(lines)
        chemin = chemins_pdf[lines[4]-1]
        if lines[4] <= 6:
            funct_used = inov16.extract_inf_project_1_6
        elif lines[4] <= 10:
            funct_used = inov710.extract_inf_project_7_10
        else:
            funct_used = inov1112.extract_inf_project_11_12

        if lines[0] != "astran":
            doc_open = pymupdf.open(filename=chemin)
            if lines[0] == "alphaiota":
                page_open = doc_open[lines[3] - 2]
            else:
                page_open = doc_open[lines[3] - 1]

            result_dict = funct_used(page_open)

            # if moba, then modify values
            if lines[0] == "moba":
                result_dict["MONTANT_PROJET"] = "1 303 134 €"
                result_dict["MONTANT_AIDE"] = "586 410 €"
                result_dict["REALISATION"] = "24 mois"

            for key in dict_donnees.keys():
                dict_donnees[key].append(result_dict[key])
            doc_open.close()
        else:
            for key in dict_donnees.keys():
                dict_donnees[key].append(None)


    return dict_donnees

if __name__=="__main__":
    toc_contents = pd.read_json(path_or_buf="Data/concours_toc.jsonl", lines=True,encoding="utf-8",orient="records")
    toc_project_contents = pd.DataFrame(extract_projets(toc_contents))
    toc_project_contents = pd.concat([toc_contents, toc_project_contents], axis=1)

    #print(toc_project_contents)
    toc_project_contents.to_csv("Data/ToClean/concours_projet_1_12.csv", sep=";", index=False)

