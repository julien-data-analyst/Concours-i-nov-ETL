##############################-
# Sujet : Extraction du sommaire pour les concours de 11 à 12
# Date : 29/11/2025
# Auteur : Julien RENOULT
#############################-

# Chargement des librairies
import pymupdf
import pymupdf
import pandas as pd
import re 
import os 

def extract_concours_inov_11_12(path_pdf="", export=False, path=""):

    """
    Fonction : Permet d'extraire le sommaire des fichiers concours de 11 à 12.
    Arguments :
        - path_pdf : Le chemin où sont stockées les différents PDF du concours
        - export : False renvoit la df, True renvoit un fichier CSV dont nous avons défini le chemin avec path
        - path : chemin du fichier CSV si on exporte les données
    """

    # Documents PDF à parcourir
    docs = [
            "i-nov---palmar-s-vague-11-37360.pdf",
            "i-nov---palmar-s-vague-12-37363.pdf"
            ]

    cols_dataframes = ["ENTREPRISE", "PROJET", "THEMATIQUE", "PAGE", "VAGUE"]
    donnees_collectees = []
    thematique_actuelle = "" # La thématique a ajouté dans la ligne de données
    pattern = r'^\s*LAURÉATES\s*$'
    pattern_them = r'\bThématique\b(?:\s*-\s*)?'
    pattern_ext_proj = r'^P?ROJET\s+(.+?)\s+\d+\s*$' # nom_projet = m.group(1)
    pattern_numero_page = r'(\d+)\s*$'

    for doc_open in docs:
        doc = pymupdf.open(os.path.join(path_pdf, doc_open)) # open a document
        match = re.search(r"-(\d+)-", doc_open) # get the vague number
        resultat_match = match.group(1) # Add the vague number to the var

        for page in doc[15:17]: # iterate the document pages
                
            debut_donnees = False # word = r'^\s*LAURÉATES\s*$'

            text = page.get_text(sort=True).encode("utf8").decode("utf8") # get plain text (is in UTF-8)
            liste_texte = text.split("\n") # split the text by "\n"
            liste_texte = [x for x in liste_texte if x != ""]
            liste_texte = [x.split(" - ") for x in liste_texte]

            #print(liste_texte)
            #print(page)

            for elt in liste_texte:

                if len(elt) == 1:
                    thematique_actuelle = re.sub(pattern_them, '', elt[0])

                elif len(elt) == 2:
                    if "PATHOMIX" in elt[1]:
                        projet = "PATHOMIX"
                        num_page = 52
                        entreprise = "TRIBUN HEALTH"
                    elif "EPIWISE" in elt[1]:
                        projet = "EPIWISE"
                        num_page = 38
                        entreprise = "GEOMATYS"
                    else:
                        #print(elt)
                        projet = re.match(pattern_ext_proj, elt[1]).group(1) # Récupérer le nom du projet
                        num_page = re.search(pattern_numero_page, elt[1]).group(1) # Récupérer le numéro de page
                        entreprise = elt[0]
                    
                    donnees_collectees.append([entreprise, projet, thematique_actuelle, num_page, resultat_match])
                else:
                    pass
                
                # Début extraction
                for chaine in elt:
                    if re.match(pattern, chaine): # Début extraction
                        debut_donnees = True
        # Close the PDF document
        doc.close()

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
