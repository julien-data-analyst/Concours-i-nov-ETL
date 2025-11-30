##############################-
# Sujet : Extraction du sommaire pour les concours de 7 à 10
# Date : 29/11/2025
# Auteur : Julien RENOULT
#############################-
import pymupdf
import pymupdf
import pandas as pd
import re 
import os

def extract_concours_inov_7_10(path_pdf="", export=False, path=""):

    """
    Fonction : Permet d'extraire le sommaire des fichiers concours de 7 à 10.
    Arguments :
        - path_pdf : Le chemin où sont stockées les différents PDF du concours
        - export : False renvoit la df, True renvoit un fichier CSV dont nous avons défini le chemin avec path
        - path : chemin du fichier CSV si on exporte les données
    """
    # Documents PDF à parcourir
    docs = [
            "i-nov---palmar-s-vague-7-19066.pdf",
            "i-nov---palmar-s-vague-8-19069.pdf",
            "i-nov---palmar-s-vague-9-28604.pdf",
            "i-nov---palmar-s-vague-10-28601.pdf"
            ]

    cols_dataframes = ["ENTREPRISE", "PROJET", "PAGE", "THEMATIQUE", "VAGUE"]
    donnees_collectees = []
    thematique_actuelle = "" # La thématique a ajouté dans la ligne de données
    pattern = r'^\s*NOM PROJET\s*$'
    pattern_them = r'\bThématique\b(?:\s*-\s*)?'
    pattern_proj = r'\bProjet\b'

    dict_pages_somm = {
        "7" : [11, 13],
        "8" : [21, 23],
        "9" : [17, 19],
        "10" : [17, 19]
    }

    for doc_open in docs:
        doc = pymupdf.open(os.path.join(path_pdf, doc_open)) # open a document
        match = re.search(r"-(\d+)-", doc_open) # get the vague number
        resultat_match = match.group(1) # Add the vague number to the var
        page_avant = dict_pages_somm[resultat_match][0] # Récupérer le numéro de page du début du sommaire
        page_apres = dict_pages_somm[resultat_match][1] # Récupérer le numéro de page de la fin du sommaire

        for page in doc[page_avant:page_apres]: # iterate the document pages
            
            debut_donnees = False 

            text = page.get_text(sort=True).encode("utf8").decode("utf8") # get plain text (is in UTF-8)
            liste_texte = text.split("\n") # split the text by "\n"

            # Séparation des éléments
            for ind in range(len(liste_texte)):
                liste_texte[ind] = liste_texte[ind].split("  ")
                liste_texte[ind] = [x for x in liste_texte[ind] if x != '']

            for ind in range(len(liste_texte)):

                if debut_donnees:

                    if len(liste_texte[ind]) == 2: # C'est la thématique
                        # Si la thématique à son autre partie dans l'elt suivant (une liste d'un seul élément), la concaténer
                        if len(liste_texte) != ind+1:
                            if len(liste_texte[ind+1]) == 1:
                                thematique_actuelle = re.sub(pattern_them, '', liste_texte[ind][0] + liste_texte[ind+1][0]) # Concaténation si c'est sur deux lignes
                            else:
                                thematique_actuelle = re.sub(pattern_them, '', liste_texte[ind][0])

                    elif len(liste_texte[ind]) == 3: # Ligne de données
                        # Modifier les éléments
                        liste_texte[ind][1] = re.sub(pattern_proj, '', liste_texte[ind][1])
                        
                        donnees_collectees.append(liste_texte[ind] + [thematique_actuelle, resultat_match])
                    
                    else:
                        pass


                
                for elt in liste_texte[ind]:
                    if re.match(pattern, elt): # Début extraction
                        #print(page)
                        debut_donnees = True
        # Close the PDF document
        doc.close()

        #print(liste_texte)
        #print(page)

    #print(donnees_collectees)

    # Transformation en DataFrame
    df = pd.DataFrame(donnees_collectees, columns=cols_dataframes)
    #print(df.dtypes)
    #print(df.head())
    #print(df.shape)

    if export:
        df.to_csv(path, sep=";", 
                header=True, index=False, encoding="utf-8")
    else:
        return df
    
