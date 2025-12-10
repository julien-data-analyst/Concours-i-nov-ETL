##############################-
# Sujet : Extraction du sommaire pour les concours de 1 à 6
# Date : 29/11/2025 - 30/11/2025
# Auteur : Julien RENOULT
#############################-

# Chargement des librairies
import pymupdf
import pandas as pd
import re 
import os

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

   