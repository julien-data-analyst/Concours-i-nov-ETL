import marimo

__generated_with = "0.18.3"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import pymupdf
    import re
    return mo, pd, pymupdf, re


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Extraction d'information sur un projet de chaque concours
    # (1-6, 7-10, 11-12)
    ## Auteur : Julien RENOULT
    ## Date : 08/12/2025
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Importation des données et lecture des fichiers PDF
    """)
    return


@app.cell
def _(pd):
    toc_contents = pd.read_json(path_or_buf="Data/concours_toc.jsonl", lines=True,encoding="utf-8",orient="records")
    concours_contents = pd.read_json(path_or_buf="Data/concours.jsonl", lines=True,encoding="utf-8",orient="records")
    return concours_contents, toc_contents


@app.cell
def _(toc_contents):
    toc_contents
    return


@app.cell
def _(concours_contents):
    concours_contents
    return


@app.cell
def _():
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
    return (chemins_pdf,)


@app.cell
def _(chemins_pdf, pymupdf, toc_contents):
    # Pour un projet de concours dans la vague 1 à 6
    doc_concours_1_6 = pymupdf.open(chemins_pdf[0])
    doc_concours_7_10 = pymupdf.open(chemins_pdf[6])
    doc_concours_11_12 = pymupdf.open(chemins_pdf[10])

    # prenons la première ligne comme exemple
    premier_projet = toc_contents.iloc[0]
    print(premier_projet)
    return (
        doc_concours_11_12,
        doc_concours_1_6,
        doc_concours_7_10,
        premier_projet,
    )


@app.cell
def _(premier_projet):
    int(premier_projet["PAGE"])
    return


@app.cell
def _(doc_concours_1_6, premier_projet):
    # Allons à la page correspondante de ce projet (n-1)
    page_projet = doc_concours_1_6[int(premier_projet["PAGE"])-1]
    return (page_projet,)


@app.cell
def _(page_projet):
    # Vérifier le contenu
    page_projet.get_text().encode('utf8').decode(encoding='utf8')
    return


@app.cell
def _(page_projet, premier_projet):
    # Recherchons le nom de l'entreprise
    occurences_entreprises = page_projet.search_for(str(premier_projet["ENTREPRISE"]))
    occurences_entreprises
    return (occurences_entreprises,)


@app.cell
def _(occurences_entreprises, page_projet):
    extracted_text = page_projet.get_textbox(occurences_entreprises[1])
    extracted_text
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Extraire les différentes informations d'un PDF en utilisant la méthode search_for()
    """)
    return


@app.cell
def _(pymupdf):
    def search_words_extract(searched_word, 
                             search_page,
                             x0_dec_result=0, x1_dec_result=0, 
                             y0_dec_result=0, y1_dec_result=0, 
                             result_elt = 0):
        """
        Function : research the word and send the string result which given by the "dec_result" coordinates.

        Args :
            - searched_word : a string researched word

            - search_page : a object type of "Page" to search the word for

            - x0_dec_result : a float number to shift at x0, 
                                if string "x1" then take the coordinates of the rect.x1 (default : 0)

            - x1_dec_result : a float number to shift at x1, 
                                if string "x0" then take the coordinates of the rect.x0 (default : 0)

            - y0_dec_result : a float number to shift at y0, 
                                if string "y1" then take the coordinates of the rect.y1 (default : 0)

            - y1_dec_result : a float number to shift at y1, 
                                if string "y0" then take the coordinates of the rect.y0 (default : 0)

            - result_elt : which element to take from the result (default : 0)

        Return :
            - result : a string result of the searching
        """

        # Get the occurence list
        occurence_search_word = search_page.search_for(searched_word)

        # If he doesn't find [], then return None
        if occurence_search_word == []:
            #print("Le mot '"+searched_word+"' n'a pas été trouvé")
            result = None
        else:
            # If he does find, take the first element by default
            rect_search_word = occurence_search_word[result_elt]

            # create the result zone
            if x0_dec_result == "x1":
                x0_res = rect_search_word.x1
            else:
                x0_res = rect_search_word.x0 + x0_dec_result

            if x1_dec_result == "x0":
                x1_res = rect_search_word.x0
            else:
                x1_res = rect_search_word.x1 + x1_dec_result

            if y0_dec_result == "y1":
                y0_res = rect_search_word.y1
            else:
                y0_res = rect_search_word.y0 + y0_dec_result

            if y1_dec_result == "y0":
                y1_res = rect_search_word.y0
            else:
                y1_res = rect_search_word.y1 + y1_dec_result

            zone_res = pymupdf.Rect(x0_res, y0_res, x1_res, y1_res)

            # Take the string result
            result = search_page.get_textbox(zone_res).strip()

        return result
    return (search_words_extract,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Pour la localisation
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pour les concours 1 à 6
    """)
    return


@app.cell
def _(page_projet):
    occurence_localisation = page_projet.search_for("LOCALISATION >")
    return (occurence_localisation,)


@app.cell
def _(occurence_localisation):
    occurence_localisation
    return


@app.cell
def _(occurence_localisation, page_projet):
    page_projet.get_textbox(occurence_localisation[0])
    return


@app.cell
def _(occurence_localisation):
    rect_localisation = occurence_localisation[0]
    return (rect_localisation,)


@app.cell
def _(pymupdf, rect_localisation):
    # Décaler le bloc de texte pour récupérer la valeur
    x0 = rect_localisation.x1 + 5
    y0 = rect_localisation.y0 - 2
    x1 = rect_localisation.x1 + 40
    y1 = rect_localisation.y1 + 2

    zone = pymupdf.Rect(x0, y0, x1, y1)
    return (zone,)


@app.cell
def _(zone):
    zone
    return


@app.cell
def _(page_projet, zone):
    page_projet.get_textbox(zone).strip()
    return


@app.cell
def _(page_projet, re, search_words_extract):
    # pattern to extract the localisations
    pattern = r'LOCALISATION\s*>\s*(.*?)(?=\s*R[ÉE]ALISATION\s*>|$)'

    string_research = search_words_extract("LOCALISATION >", 
                        page_projet,
                        0, 
                        50,
                        0,
                         20
                        )

    m = re.search(pattern, string_research, flags=re.DOTALL)

    if m :
        localisation = m.group(1).strip()
        print(localisation)
    return (pattern,)


@app.cell
def _(doc_concours_1_6):
    # Cas particuliers à régler quand il est sur plusieurs lignes
    page_projet_1_6_2 = doc_concours_1_6[46]
    return (page_projet_1_6_2,)


@app.cell
def _(page_projet_1_6_2, pattern, re, search_words_extract):
    string_research_2 = search_words_extract("LOCALISATION >", 
                        page_projet_1_6_2,
                        0, 
                        50,
                        0,
                         20
                        )

    m2 = re.search(pattern, string_research_2, flags=re.DOTALL)

    if m2 :
        localisation2 = m2.group(1).strip()
        print(localisation2)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pour les concours 7 à 10
    """)
    return


@app.cell
def _(toc_contents):
    exemple_proj_7_10 = toc_contents[toc_contents["VAGUE"] == 7].iloc[0]
    return (exemple_proj_7_10,)


@app.cell
def _(exemple_proj_7_10):
    exemple_proj_7_10
    return


@app.cell
def _(doc_concours_7_10, exemple_proj_7_10):
    page_projet_7_10 = doc_concours_7_10[int(exemple_proj_7_10["PAGE"]) - 1]
    return (page_projet_7_10,)


@app.cell
def _(page_projet_7_10):
    page_projet_7_10.get_text()
    return


@app.cell
def _(page_projet_7_10):
    rect_localisation_7_10 = page_projet_7_10.search_for("LOCALISATION")[0]
    return (rect_localisation_7_10,)


@app.cell
def _(rect_localisation_7_10):
    rect_localisation_7_10
    return


@app.cell
def _():
    # Définir la zone après droite
    return


@app.cell
def _(page_projet_7_10, rect_localisation_7_10):
    page_projet_7_10.get_textbox(rect_localisation_7_10).strip()
    return


@app.cell
def _(pymupdf, rect_localisation_7_10):
    # Décaler le bloc de texte pour récupérer la valeur
    x0_7_10 = rect_localisation_7_10.x1 + 5
    y0_7_10 = rect_localisation_7_10.y0 - 2
    x1_7_10 = rect_localisation_7_10.x1 + 40
    y1_7_10 = rect_localisation_7_10.y1 + 2

    zone_loc = pymupdf.Rect(x0_7_10, y0_7_10, x1_7_10, y1_7_10)
    return (zone_loc,)


@app.cell
def _(zone_loc):
    zone_loc
    return


@app.cell
def _(page_projet_7_10, zone_loc):
    page_projet_7_10.get_textbox(zone_loc)
    return


@app.cell
def _(page_projet_7_10, search_words_extract):
    search_words_extract("LOCALISATION", 
                        page_projet_7_10,
                        "x1", 
                        150,
                        -2,
                         2
                        )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pour les concours de 11 à 12
    """)
    return


@app.cell
def _(toc_contents):
    exemple_proj_11_12 = toc_contents[toc_contents["VAGUE"] == 11].iloc[0]
    return (exemple_proj_11_12,)


@app.cell
def _(exemple_proj_11_12):
    exemple_proj_11_12
    return


@app.cell
def _(doc_concours_11_12, exemple_proj_11_12):
    page_projet_11_12 = doc_concours_11_12[int(exemple_proj_11_12["PAGE"])-1]
    return (page_projet_11_12,)


@app.cell
def _(page_projet_11_12):
    page_projet_11_12.get_text()
    return


@app.cell
def _(page_projet_11_12):
    rect_localisation_11_12 = page_projet_11_12.search_for("|")[0]
    return (rect_localisation_11_12,)


@app.cell
def _(rect_localisation_11_12):
    rect_localisation_11_12
    return


@app.cell
def _(pymupdf, rect_localisation_11_12):
    # Décaler le bloc de texte pour récupérer la valeur
    x0_11_12 = rect_localisation_11_12.x0 - 15
    y0_11_12 = rect_localisation_11_12.y0 - 2
    x1_11_12 = rect_localisation_11_12.x1 + 160
    y1_11_12 = rect_localisation_11_12.y1 + 2

    zone_11_12 = pymupdf.Rect(x0_11_12, y0_11_12, x1_11_12, y1_11_12)
    return (zone_11_12,)


@app.cell
def _(page_projet_11_12, zone_11_12):
    page_projet_11_12.get_textbox(zone_11_12)
    return


@app.cell
def _(page_projet_11_12, search_words_extract):
    search_words_extract("|", 
                        page_projet_11_12,
                        -15, 
                        180,
                        -2,
                         2
                        )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Pour le montant du projet
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pour les concours de 1 à 6
    """)
    return


@app.cell
def _(page_projet, search_words_extract):
    search_words_extract("MONTANT DU PROJET >", 
                        page_projet,
                        "x1", 
                        40,
                        -2,
                         2
                        )
    return


@app.cell
def _(doc_concours_1_6):
    # Cas particulier si la chaîne se trouve en dessous
    page_projet_1_6 = doc_concours_1_6[51]
    return (page_projet_1_6,)


@app.cell
def _(page_projet_1_6, search_words_extract):
    search_words_extract("MONTANT DU PROJET >", 
                        page_projet_1_6,
                        0, 
                        80,
                        "y1",
                         10
                        )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pour les concours de 7 à 10
    """)
    return


@app.cell
def _(page_projet_7_10, search_words_extract):
    search_words_extract("Montant du projet", 
                        page_projet_7_10,
                        "x1", 
                        230,
                        0,
                         0
                        )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pour les concours 11 et 12
    """)
    return


@app.cell
def _(page_projet_11_12, search_words_extract):
    search_words_extract("MONTANT TOTAL DU PROJET", 
                        page_projet_11_12,
                        0, 
                        80,
                        "y1",
                         10
                        )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Pour l'aide du projet
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pour les concours de 1 à 6
    """)
    return


@app.cell
def _(page_projet, search_words_extract):
    search_words_extract("DONT AIDE PIA >", 
                         page_projet,
                         "x1", 
                        40,
                        -2,
                         2
                        )
    return


@app.cell
def _(page_projet_1_6, search_words_extract):
    search_words_extract("DONT AIDE PIA >", 
                         page_projet_1_6,
                         "x1", 
                        40,
                        -2,
                         2
                        )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pour le concours de 7 à 10
    """)
    return


@app.cell
def _(page_projet_7_10, search_words_extract):
    search_words_extract("Aide accordée", 
                         page_projet_7_10,
                         "x1", 
                        230,
                        0,
                         0
                        )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pour les concours de 11 et 12
    """)
    return


@app.cell
def _(page_projet_11_12, search_words_extract):
    search_words_extract("MONTANT AIDE", 
                        page_projet_11_12,
                        0, 
                        80,
                        "y1",
                         10
                        )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Durée du projet
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pour les concours de 1 à 6
    """)
    return


@app.cell
def _(page_projet, search_words_extract):
    search_words_extract("rÉalisation >", 
                        page_projet,
                        "x1", 
                        40,
                        0,
                         0
                        )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pour les concours de 7 à 10
    """)
    return


@app.cell
def _(page_projet_7_10, search_words_extract):
    search_words_extract("Réalisation", 
                        page_projet_7_10,
                        "x1", 
                        160,
                        0,
                         0
                        )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pour les concours de 11 et 12
    """)
    return


@app.cell
def _(page_projet_11_12, search_words_extract):
    search_words_extract("DurÉe du projet", 
                        page_projet_11_12,
                        0, 
                        100,
                        "y1",
                         4
                        )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Activité de l'entreprise
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pour les concours de 1 à 6

    Pour récupérer l'activité de l'entreprise, nous allons utiliser les titres "> Activité de l'entrperise" et "> Objectif du projet" pour délimiter le texte à récupérer.
    """)
    return


@app.cell
def _(page_projet_1_6_2):
    page_projet_1_6_2
    return


@app.cell
def _(page_projet_1_6_2):
    zone_activite = page_projet_1_6_2.search_for("> ACTIVITÉ DE L’ENTREPRISE")[0]
    return (zone_activite,)


@app.cell
def _(zone_activite):
    zone_activite
    return


@app.cell
def _(page_projet_1_6_2):
    zone_objectif = page_projet_1_6_2.search_for("> OBJECTIF DU PROJET")[0]
    return (zone_objectif,)


@app.cell
def _(zone_objectif):
    zone_objectif
    return


@app.cell
def _(page_projet_1_6_2, pymupdf, zone_activite, zone_objectif):
    x0_debut = zone_activite.x0
    y0_debut = zone_activite.y1
    x1_fin = page_projet_1_6_2.rect.x1
    y1_fin = zone_objectif.y0 - 2
    rect_activite = pymupdf.Rect(x0_debut, y0_debut, x1_fin, y1_fin)
    return (rect_activite,)


@app.cell
def _(page_projet_1_6_2, rect_activite):
    page_projet_1_6_2.get_textbox(rect_activite)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pour les concours de 7 à 10

    Même chose mise à part que la délimitation doit être entre le titre du projet (projets) et le contact presse en prenant le premier paragraphe (le deuxième représentant le projet). Si plus de dex paragraphes, les deux premières ensembles, les autres avec le projet.
    """)
    return


@app.cell
def _(exemple_proj_7_10):
    exemple_proj_7_10
    return


@app.cell
def _(page_projet_7_10):
    zone_contact_presse = page_projet_7_10.search_for("Contact presse")[0]
    zone_contact_presse
    return (zone_contact_presse,)


@app.cell
def _(page_projet_7_10):
    zone_aide_acc = page_projet_7_10.search_for("Aide accordée")[0]
    zone_aide_acc
    return (zone_aide_acc,)


@app.cell
def _(page_projet_7_10, pymupdf, zone_aide_acc, zone_contact_presse):
    x0_debut_2 = zone_contact_presse.x0
    y0_debut_2 = zone_aide_acc.y1 + 60
    x1_fin_2 = page_projet_7_10.rect.x1
    y1_fin_2 = zone_contact_presse.y0 - 2
    rect_activite_2 = pymupdf.Rect(x0_debut_2, y0_debut_2, x1_fin_2, y1_fin_2)
    return (rect_activite_2,)


@app.cell
def _(page_projet_7_10, rect_activite_2):
    page_projet_7_10.get_text(option="blocks", clip=rect_activite_2)
    return


@app.cell
def _(page_projet_7_10, rect_activite_2):
    page_projet_7_10.get_textbox(rect_activite_2)
    return


@app.cell
def _(doc_concours_7_10):
    page_projet_7_10_2 = doc_concours_7_10[24]
    return (page_projet_7_10_2,)


@app.cell
def _(page_projet_7_10_2):
    zone_contact_presse_2 = page_projet_7_10_2.search_for("Contact presse")[0]
    zone_contact_presse_2
    return (zone_contact_presse_2,)


@app.cell
def _(page_projet_7_10_2):
    zone_aide_acc_2 = page_projet_7_10_2.search_for("Aide accordée")[0]
    zone_aide_acc_2
    return (zone_aide_acc_2,)


@app.cell
def _(page_projet_7_10_2, pymupdf, zone_aide_acc_2, zone_contact_presse_2):
    x0_debut_3 = zone_contact_presse_2.x0
    y0_debut_3 = zone_aide_acc_2.y1 + 60
    x1_fin_3 = page_projet_7_10_2.rect.x1 - 60
    y1_fin_3 = zone_contact_presse_2.y0 - 2
    rect_activite_3 = pymupdf.Rect(x0_debut_3, y0_debut_3, x1_fin_3, y1_fin_3)
    return (rect_activite_3,)


@app.cell
def _(page_projet_7_10_2, rect_activite_3):
    page_projet_7_10_2.get_text(option="blocks", clip=rect_activite_3)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pour les concours de 11 et 12

    Même chose mise à part que c'est entre le titre 'Activité de l'entreprise' et la localisation '|'.
    """)
    return


@app.cell
def _(page_projet_11_12):
    zone_activite_11_12 = page_projet_11_12.search_for("ACTIVITÉ DE L’ENTREPRISE")[0]
    zone_activite_11_12
    return (zone_activite_11_12,)


@app.cell
def _(page_projet_11_12):
    zone_loc_11_12 = page_projet_11_12.search_for("|")[0]
    zone_loc_11_12
    return (zone_loc_11_12,)


@app.cell
def _(page_projet_11_12):
    zone_objectif_11_12 = page_projet_11_12.search_for("OBJECTIFS DU PROJET")[0]
    zone_objectif_11_12
    return (zone_objectif_11_12,)


@app.cell
def _(pymupdf, zone_activite_11_12, zone_loc_11_12, zone_objectif_11_12):
    x0_11_12_2 = zone_activite_11_12.x0
    y0_11_12_2 = zone_activite_11_12.y1
    x1_11_12_2 = zone_objectif_11_12.x0 - 1
    y1_11_12_2 = zone_loc_11_12.y0 - 2
    rect_activite_11_12 = pymupdf.Rect(x0=x0_11_12_2, y0=y0_11_12_2, x1=x1_11_12_2, y1=y1_11_12_2)
    return (rect_activite_11_12,)


@app.cell
def _(page_projet_11_12, rect_activite_11_12):
    page_projet_11_12.get_textbox(rect_activite_11_12)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Objectif du projet

    Définir la limite de 80% pour les notes de bas de page. (concours 1 à 6)
    Définir la limit de 60% (bottom). (concours 11 et 12)
    récupérer le deuxième paragraphe entre "Titre du projet" et "Contact Presse" (concours 7 à 10)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pour les concours de 1 à 6
    """)
    return


@app.cell
def _(zone_objectif):
    zone_objectif
    return


@app.cell
def _(page_projet_1_6_2):
    zone_contact_presse_1_6 = page_projet_1_6_2.search_for("CONTACT")[0]
    zone_contact_presse_1_6
    return (zone_contact_presse_1_6,)


@app.cell(hide_code=True)
def _(page_projet_1_6_2, pymupdf, zone_contact_presse_1_6, zone_objectif):
    # Utilisation du début de la zone objectif et de la fin avec contact presse
    x0_11_12_3 = zone_objectif.x0
    y0_11_12_3 = zone_objectif.y1
    x1_11_12_3 = page_projet_1_6_2.rect.x1 - 10
    y1_11_12_3 = zone_contact_presse_1_6.y0 + 5
    rect_objectif_1_6 = pymupdf.Rect(x0=x0_11_12_3, y0=y0_11_12_3, x1=x1_11_12_3, y1=y1_11_12_3)
    return (rect_objectif_1_6,)


@app.cell
def _(page_projet_1_6_2, rect_objectif_1_6):
    page_projet_1_6_2.get_textbox(rect_objectif_1_6)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pour les concours de 7 à 10
    """)
    return


@app.cell
def _(page_projet_7_10_2, rect_activite_3):
    page_projet_7_10_2.get_text(option="blocks", clip=rect_activite_3)[1][4] + " " + page_projet_7_10_2.get_text(option="blocks", clip=rect_activite_3)[2][4]
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pour les concours 11 et 12
    """)
    return


@app.cell
def _(page_projet_11_12):
    page_projet_11_12
    return


@app.cell
def _(zone_objectif_11_12):
    zone_objectif_11_12
    return


@app.cell
def _(page_projet_11_12):
    zone_duree_projet = page_projet_11_12.search_for("DURÉE DU PROJET")[0]
    zone_duree_projet
    return (zone_duree_projet,)


@app.cell
def _(page_projet_11_12, pymupdf, zone_duree_projet, zone_objectif_11_12):
    x0_11_12_4 = zone_objectif_11_12.x0
    y0_11_12_4 = zone_objectif_11_12.y1
    x1_11_12_4 = page_projet_11_12.rect.x1 - 5
    y1_11_12_4 = zone_duree_projet.y0 - 10
    rect_objectif_11_12 = pymupdf.Rect(x0_11_12_4, y0_11_12_4, x1_11_12_4, y1_11_12_4)
    return (rect_objectif_11_12,)


@app.cell
def _(page_projet_11_12, rect_objectif_11_12):
    page_projet_11_12.get_textbox(rect_objectif_11_12)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Création des fonctions pour récupérer des informations
    """)
    return


@app.cell
def _(page_projet, page_projet_1_6_2, pymupdf, re, search_words_extract):
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
        
        zone_contact_presse = page_projet.search_for("CONTACT")[0]

        ## Company activity
        # Utilisation du début de la zone d'activité et de la fin avec Objectif
        if zone_activite != []:
            x0_comp = zone_activite.x0
            y0_comp = zone_activite.y1
            x1_comp = page_projet_1_6_2.rect.x1
            y1_comp = zone_objectif.y0 - 2
            rect_activite = pymupdf.Rect(x0_comp, y0_comp, x1_comp, y1_comp)
            result_activite = page.get_textbox(rect_activite)
        else:
            result_activite = None
        
        ## Project goal
        # Utilisation du début de la zone objectif et de la fin avec contact presse
        x0_proj = zone_objectif.x0
        y0_proj = zone_objectif.y1
        x1_proj = page_projet.rect.x1 - 10
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

    return (extract_inf_project_1_6,)


@app.cell
def _(extract_inf_project_1_6, page_projet_1_6_2):
    extract_inf_project_1_6(page=page_projet_1_6_2)
    return


@app.cell
def _(chemins_pdf, pymupdf):
    # Pour un projet de concours dans la vague 1 à 6
    doc_concours_1_6_2 = pymupdf.open(chemins_pdf[1])
    return (doc_concours_1_6_2,)


@app.cell
def _(doc_concours_1_6_2):
    doc_concours_1_6_2[77].get_text()
    return


@app.cell
def _(doc_concours_1_6_2, extract_inf_project_1_6):
    extract_inf_project_1_6(doc_concours_1_6_2[77])
    return


@app.cell
def _(doc_concours_1_6, extract_inf_project_1_6):
    page_projet_1_6_3 = doc_concours_1_6[102]
    extract_inf_project_1_6(page_projet_1_6_3)
    return


@app.cell
def _(page_projet_7_10, pymupdf, search_words_extract):
    # Fonction permettant de récupérer les informations d'un projet dans les concours 7 à 10
    def extract_inf_project_7_10(page):
        """
        Function : extract the project information by the given page

        Args :
        - page : PDF page to use to extract the information of the project

        Return :
        a dict of results containing informations on the project
        """
        # Extract the geographic localisation
        result_loc = search_words_extract("LOCALISATION", 
                        page,
                        "x1", 
                        150,
                        -2,
                         2
                        )

        # Extract the amount of cost project
        result_amount_proj = search_words_extract("Montant du projet", 
                        page,
                        "x1", 
                        230,
                        0,
                         0
                        )

        # Extract the amount of allowance 
        result_allowance = search_words_extract("Aide accordée", 
                         page,
                         "x1", 
                        230,
                        0,
                         0
                        )

        # Extract the realisation years
        result_years = search_words_extract("Réalisation", 
                        page,
                        "x1", 
                        160,
                        0,
                         0
                        )

        # Extract the activity and project goal
        zone_contact_presse = page.search_for("Contact presse")[0]
        zone_aide_acc = page.search_for("Aide accordée")[0]

        x0_act = zone_contact_presse.x0
        y0_act = zone_aide_acc.y1 + 60
        x1_act = page_projet_7_10.rect.x1
        y1_act = zone_contact_presse.y0 - 2
        rect_activite = pymupdf.Rect(x0_act, y0_act, x1_act, y1_act)

        result_blocks = page.get_text(option="blocks", clip=rect_activite)

        #print(result_blocks)

        if len(result_blocks) == 2:
            result_activity = result_blocks[0][4]
            result_goal = result_blocks[1][4]
        elif len(result_blocks) > 2:
            result_activity = result_blocks[0][4]
        
            result_goal = ""
            for elt in result_blocks[1:]:
                result_goal += elt[4] + " "
        else:
            result_activity = None
            result_goal = result_blocks[0][4]
        
        return {
            "LOCALISATION" : result_loc,
            "MONTANT_PROJET" : result_amount_proj,
            "MONTANT_AIDE" : result_allowance,
            "REALISATION" : result_years,
            "ACTIVITE_ENTREPRISE" : result_activity,
            "OBJECTIF_PROJET" : result_goal
        }

    return (extract_inf_project_7_10,)


@app.cell
def _(doc_concours_7_10):
    doc_concours_7_10[70].get_text()
    return


@app.cell
def _(extract_inf_project_7_10, page_projet_7_10):
    extract_inf_project_7_10(page_projet_7_10)
    return


@app.cell
def _(pymupdf, search_words_extract):
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
    
    return (extract_inf_project_11_12,)


@app.cell
def _(doc_concours_11_12):
    page_projet_11_12_2 = doc_concours_11_12[34]
    return (page_projet_11_12_2,)


@app.cell
def _(extract_inf_project_11_12, page_projet_11_12_2):
    extract_inf_project_11_12(page=page_projet_11_12_2)
    return


@app.cell
def _(chemins_pdf, pymupdf):
    doc_concours_11_12_2 = pymupdf.open(chemins_pdf[11])
    page_projet_11_12_3 = doc_concours_11_12_2[48]
    return (page_projet_11_12_3,)


@app.cell
def _(page_projet_11_12_3):
    page_projet_11_12_3.get_text()
    return


@app.cell
def _(extract_inf_project_11_12, page_projet_11_12_3):
    extract_inf_project_11_12(page_projet_11_12_3)
    return


@app.cell
def _(page_projet_11_12_3, search_words_extract):
    # Extract the project cost
    search_words_extract("MONTANT TOTAL DU PROJET", 
                        page_projet_11_12_3,
                        0, 
                        15,
                        90,
                         100
                        )
    return


@app.cell
def _(page_projet_11_12_3, search_words_extract):
    # Extract the allowance for the project
    search_words_extract("MONTANT AIDE", 
                        page_projet_11_12_3,
                        0, 
                        15,
                        90,
                         100
                        )
    return


@app.cell
def _(page_projet_11_12_3, search_words_extract):
    # Extract the years of realisation
    search_words_extract("DurÉe du projet", 
                        page_projet_11_12_3,
                        0, 
                        15,
                        90,
                         100
                        )
    return


@app.cell
def _(
    chemins_pdf,
    extract_inf_project_11_12,
    extract_inf_project_1_6,
    extract_inf_project_7_10,
    pymupdf,
):
    # Extraire les informations sur tous les projets
    def extract_projets(df):

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
                funct_used = extract_inf_project_1_6
            elif lines[4] <= 10:
                funct_used = extract_inf_project_7_10
            else:
                funct_used = extract_inf_project_11_12

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
    return (extract_projets,)


@app.cell
def _(extract_projets, toc_contents):
    details_projets = extract_projets(toc_contents)
    return (details_projets,)


@app.cell
def _(details_projets, pd):
    details_projets_2 = pd.DataFrame(details_projets)
    return (details_projets_2,)


@app.cell
def _(details_projets_2):
    details_projets_2
    return


@app.cell
def _(details_projets_2, pd, toc_contents):
    toc_contents_project_details = pd.concat([toc_contents, details_projets_2], axis=1)
    return (toc_contents_project_details,)


@app.cell
def _(toc_contents_project_details):
    toc_contents_project_details
    return


if __name__ == "__main__":
    app.run()
