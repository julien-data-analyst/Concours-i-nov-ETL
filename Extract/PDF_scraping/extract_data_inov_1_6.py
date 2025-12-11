##############################-
# Sujet : Extraction du sommaire pour les concours de 1 à 6
# Date : 29/11/2025 - 11/12/2025
#############################-

# Chargement des librairies
import pymupdf
import pandas as pd
import re 
import os
from words_pdf import search_words_extract

def extract_concours_inov_1_6(path_pdf="", export=False, path=""):

    """
    Fonction : Permet d'extraire le sommaire des fichiers concours de 1 à 6.
    Arguments :
        - path_pdf : Le chemin où sont stockées les différents PDF du concours
        - export : False renvoit la df, True renvoit un fichier CSV dont nous avons défini le chemin avec path
        - path : chemin du fichier CSV si on exporte les données
    """
    # Documents PDF à parcourir
    docs = [
            "i-nov-palmar-s-vague-1-19087.pdf",
            "i-nov---palmar-s-vague-2-19084.pdf",
            "i-nov-palmar-s-vague-3-19081.pdf",
            "i-nov---palmar-s-vague-4-19078.pdf",
            "i-nov---palmar-s-vague-5-19075.pdf",
            "i-nov---palmar-s-vague-6-19072.pdf"
            ]
    cols_dataframes = ["ENTREPRISE", "PROJET", "THEMATIQUE", "PAGE", "VAGUE"]
    donnees_collectees = []

    for doc_open in docs :
        doc = pymupdf.open(os.path.join(path_pdf, doc_open)) # open a document
        match = re.search(r"-(\d+)-", doc_open) # get the vague number
        resultat_match = match.group(1) # Add the vague number to the var

        # Parcourir le sommaire et récupérer les informations
        for page in doc[3:5]: # iterate the document pages

            # Initialize the vars 
            text = page.get_text().encode("utf8") # get plain text (is in UTF-8)
            liste_texte = text.split(bytes("\n", "utf8")) # split the text by "\n"
            comm_page = False # Var to use to detect the word "PAGE"
            word_trait_part = [bytes("BOIS LIGNOROC", "utf8"), 
                            bytes("Geovelo", "utf8"), 
                            bytes("France", "utf8"),
                            bytes("nents", "utf8"),
                            bytes("métrologie des expositions environnementales", "utf8"),
                            bytes("PULSE 3D", "utf8"),
                            bytes("CONCU", "utf-8")
                            ]
            page_word = bytes("PAGE", "utf8") # The word to detect
            liste_ligne = []

            # Parcourir et extraire les informations nécessaires
            for elt in liste_texte :

                # Si on a commencé l'extraction
                if comm_page :
                    if not bytes("index des entreprises", "utf8") in elt.lower():
                        if resultat_match == "2" and bytes("ISCT - International Supply Chain Trackers", "utf8") in elt:
                            projet = bytes("ISCT - International Supply Chain Trackers", 'utf8')
                            thematique = bytes("Espace", "utf8")
                            liste_ligne.append(projet)
                            liste_ligne.append(thematique)

                        elif resultat_match == "3" and bytes("ZOO TECHNIC", "utf8") in elt:
                            entreprise = bytes("ZOO TECHNIC Group Elastoteck", "utf8")
                            projet = bytes("ZooTechnic", "utf8")
                            liste_ligne.append(entreprise)
                            liste_ligne.append(projet)

                        elif resultat_match == "6" and bytes("METAVERSE TECHNOLOGIES", "utf8") in elt:
                            entreprise = bytes("METAVERSE TECHNOLOGIES", "utf8")
                            projet = bytes("France PULSE 3D", "utf8")
                            liste_ligne.append(entreprise)
                            liste_ligne.append(projet)

                        elif resultat_match == "1" and bytes("Mascara Nouvelles Technologies", "utf8") in elt:
                            entreprise = bytes("Mascara Nouvelles Technologies", "utf8")
                            projet = bytes("ECO DESSALEMENT SOLAIRE", "utf8")
                            liste_ligne.append(entreprise)
                            liste_ligne.append(projet)

                        elif resultat_match == "6" and bytes("COMBO", "utf8") in elt:
                            entreprise = bytes("Vesta Construction Technologies", "utf8")
                            projet = bytes("COMBO", "utf8")
                            liste_ligne.append(entreprise)
                            liste_ligne.append(projet)

                        elif elt in word_trait_part:
                                #print(liste_ligne)
                                # Fusionner avec l'élément d'avant
                                liste_ligne[len(liste_ligne)-1] += bytes(" ", "utf8") + elt
                        else:
                            # Récupérer l'élément
                            liste_ligne.append(elt)

                    # Si on a récupéré quatre éléments, on a récupéré une ligne
                    if len(liste_ligne) == 4:

                        # Décodage utf-8 pour avoir les accents
                        for ind in range (len(liste_ligne)):
                            liste_ligne[ind] = liste_ligne[ind].decode("utf-8")
                        
                        # Ajouter la ligne de données
                        donnees_collectees.append(liste_ligne + [resultat_match])
                        liste_ligne = []

                # Si l'élément est égale au word 
                if elt == page_word :
                    comm_page = True
        # Close the PDF document
        doc.close()

    # Transformation en DataFrame
    df = pd.DataFrame(donnees_collectees, columns=cols_dataframes)
    #print(df.dtypes)
    #print(df.head())
    #print(df.shape)

    # We can export to CSV
    if export:
        df.to_csv(path, sep=";", 
                header=True, index=False, encoding="utf-8")
    else:
        return df


# Fonction permettant de récupérer les informations d'un projet dans les concours 1 à 6
def extract_inf_project_1_6(page):
    """
    Function : extract the project information by the given page

    Args :
    - page : PDF page to use to extract the information of the project

    Return :
    a dict of results containing informations on the project
    """
    # Extract the localisation
    # pattern to extract the localisations
    pattern_research_loc = r'LOCALISATION\s*>\s*(.*?)(?=\s*R[ÉE]ALISATION\s*>|$)'

    string_research_loc = search_words_extract("LOCALISATION >", 
                        page,
                        0, 
                        80,
                        0,
                         100
                        )
    if not string_research_loc is None:
        resultat_search = re.search(pattern_research_loc, string_research_loc, flags=re.DOTALL)

        if resultat_search :
            localisation_search = resultat_search.group(1).strip()
            localisation_search = localisation_search.replace(">", "")
        else:
            localisation_search = ""
    else:
        localisation_search = None

    # Extract the project amount

    # First try
    result_montant = search_words_extract("MONTANT DU PROJET", 
                    page,
                    "x1", 
                    40,
                    0,
                     0
                    )

    # Second try if empty
    if result_montant == "" or result_montant == ">":
        result_montant = search_words_extract("MONTANT DU PROJET", 
                    page,
                    0, 
                    80,
                    "y1",
                     10
                    )

    if result_montant is not None:
        # nettoyage (">")
        result_montant = result_montant.replace(">", "")

    # Extract the allowance amount
    result_aide = search_words_extract("DONT AIDE PIA", 
                     page,
                     "x1", 
                    40,
                    0,
                     0
                    )

    # Second try if empty
    if result_aide == "" or result_aide == ">":
        result_aide = search_words_extract("DONT AIDE PIA", 
                    page,
                    0, 
                    80,
                    "y1",
                     10
                    )
    # nettoyage (">")
    if result_aide is not None:
        result_aide = result_aide.replace(">", "")

    # Extract the realisation years
    result_years = search_words_extract("rÉalisation", 
                    page,
                    "x1", 
                    70,
                    0,
                     0
                    )
    if result_years == "" or result_years == ">":
        result_years = search_words_extract("rÉalisation", 
                    page,
                    0, 
                    80,
                    "y1",
                     10
                    )

    if result_years == "" or result_years is None:
        result_years = None
    else:
        # nettoyage (">")
        result_years = result_years.replace(">", "")
        if result_years == "":
            result_years = None

    # Extract the company activity and project goal
    zone_activite = page.search_for("> ACTIVITÉ DE L’ENTREPRISE")
    if zone_activite == []:
        zone_activite = page.search_for("> ACTIVITÉDE L’ENTREPRISE")

        if zone_activite != []:
            zone_activite = zone_activite[0]
    else:
        zone_activite = zone_activite[0]

    zone_objectif = page.search_for("> OBJECTIF DU PROJET")
    if zone_objectif == []:
        zone_objectif = page.search_for("> OBJECTIFDU PROJET")[0]
    else:
        zone_objectif = zone_objectif[0]

    zone_contact_presse = pymupdf.Rect(49.05120086669922, 614.7211303710938, 80.85121154785156, 626.7510986328125)

    ## Company activity
    # Utilisation du début de la zone d'activité et de la fin avec Objectif
    if zone_activite != []:
        x0_comp = zone_activite.x0
        y0_comp = zone_activite.y1
        x1_comp = page.rect.x1
        y1_comp = zone_objectif.y0 - 2
        rect_activite = pymupdf.Rect(x0_comp, y0_comp, x1_comp, y1_comp)
        result_activite = page.get_textbox(rect_activite)
    else:
        result_activite = None

    ## Project goal
    # Utilisation du début de la zone objectif et de la fin avec contact presse
    x0_proj = zone_objectif.x0
    y0_proj = zone_objectif.y1
    x1_proj = page.rect.x1 - 10
    y1_proj = zone_contact_presse.y0 + 5
    rect_objectif = pymupdf.Rect(x0=x0_proj, y0=y0_proj, x1=x1_proj, y1=y1_proj)

    result_objectif = page.get_textbox(rect_objectif)


    return {
            "LOCALISATION" : localisation_search, 
            "MONTANT_PROJET" : result_montant, 
            "MONTANT_AIDE" : result_aide, 
            "REALISATION" : result_years, 
            "ACTIVITE_ENTREPRISE" : result_activite, 
            "OBJECTIF_PROJET" : result_objectif
           }