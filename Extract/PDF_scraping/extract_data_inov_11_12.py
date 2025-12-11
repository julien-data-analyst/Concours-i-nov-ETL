##############################-
# Sujet : Extraction du sommaire pour les concours de 11 à 12
# Date : 29/11/2025 - 11/12/2025
#############################-

# Chargement des librairies
import pymupdf
import pymupdf
import pandas as pd
import re 
import os 
from words_pdf import search_words_extract

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

# Fonction permettant de récupérer les informations d'un projet dans les concours 11 et 12
def extract_inf_project_11_12(page):
    """
    Function : extract the project information by the given page

    Args :
    - page : PDF page to use to extract the information of the project

    Return :
    a dict of results containing informations on the project
    """
    # Extract the localisation
    result_loc = search_words_extract("|", 
                    page,
                    -160, 
                    180,
                    -2,
                     2
                    )

    # Extract the project cost
    result_cost = search_words_extract("MONTANT TOTAL DU PROJET", 
                    page,
                    0, 
                    80,
                    "y1",
                     10
                    )

    # Extract the allowance for the project
    result_allowance = search_words_extract("MONTANT AIDE", 
                    page,
                    0, 
                    80,
                    "y1",
                     10
                    )

    # Extract the realisation years / month extract
    result_dury = search_words_extract("DurÉe du projet", 
                    page,
                    0, 
                    100,
                    "y1",
                     4
                    )

    # Get the different zones for the paragraph extraction
    zone_activite = page.search_for("ACTIVITÉ DE L’ENTREPRISE")[0]
    zone_loc = page.search_for("|")[0]
    zone_objectif = page.search_for("OBJECTIFS DU PROJET")[0]
    zone_duree_projet = page.search_for("DURÉE DU PROJET")[0]

    # for the activity of the company
    x0_11_12 = zone_activite.x0
    y0_11_12 = zone_activite.y1
    x1_11_12 = zone_objectif.x0 - 1
    y1_11_12 = zone_loc.y0 - 2
    rect_activite_11_12 = pymupdf.Rect(x0=x0_11_12, y0=y0_11_12, x1=x1_11_12, y1=y1_11_12)
    result_activity = page.get_textbox(rect_activite_11_12)

    # for the project goal
    x0_11_12_2 = zone_objectif.x0
    y0_11_12_2 = zone_objectif.y1
    x1_11_12_2 = page.rect.x1 - 5
    y1_11_12_2 = zone_duree_projet.y0 - 10
    rect_objectif_11_12 = pymupdf.Rect(x0_11_12_2, y0_11_12_2, x1_11_12_2, y1_11_12_2)
    result_goal = page.get_textbox(rect_objectif_11_12)


    # Return the results
    return {
        "LOCALISATION" : result_loc,
        "MONTANT_PROJET" : result_cost,
        "MONTANT_AIDE" : result_allowance,
        "REALISATION" : result_dury,
        "ACTIVITE_ENTREPRISE" : result_activity,
        "OBJECTIF_PROJET" : result_goal        
    }