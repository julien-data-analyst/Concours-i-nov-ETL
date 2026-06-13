###########################-
# Sujet : PDF preprocessing
# Auteur : julien-data-analyst
# Date : 2026-06-13
# ###########################-

# Import librairies
import os
from packages.pdf_preprocessing import get_pdf_files, find_summary_pages, convert_pdf_page_to_image, convert_pdf_pages_to_images
from dotenv import load_dotenv
import logging
load_dotenv()

# Configuration globale
CHEMIN_FICHIERS_PDF = os.getenv("CHEMIN_FICHIERS_PDF")
CHEMIN_FICHIERS_IMGS_SOMMAIRE = os.getenv("CHEMIN_FICHIERS_IMGS_SOMMAIRE")

#print(CHEMIN_FICHIERS_PDF)
structure_sommaire_fichiers = {} # Dictionnaire pour stocker la structure des sommaires par fichier PDF
list_summary_strings = ["Index des entreprises lauréates"]  # Liste des chaînes de caractères à rechercher pour identifier les pages de sommaire

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Aller chercher les fichiers PDF dans le répertoire spécifié
logging.info(f"Recherche des fichiers PDF dans le répertoire : {CHEMIN_FICHIERS_PDF}")
liste_fichiers_pdf = get_pdf_files(CHEMIN_FICHIERS_PDF)

# 1ère étape : identifier les pages contenant un sommaire dans chaque fichier PDF
logging.info(f"Identification des pages contenant un sommaire dans les fichiers PDF")
for pdf_file in liste_fichiers_pdf:
    summary_pages = find_summary_pages(pdf_file, list_summary_strings)
    print(f"Fichier : {pdf_file} - Pages contenant un sommaire : {summary_pages}\n")
    logging.info(f"\nFichier : {pdf_file} - Pages contenant un sommaire : {summary_pages}")
    structure_sommaire_fichiers[pdf_file] = {'summary_pages': summary_pages}
logging.info(f"\nCapture de tous les sommaires terminées")

#print(structure_sommaire_fichiers) # Vérification du succès de l'opération

# 2ème étape : convertir les pages de sommaire en images
logging.info(f"Conversion des pages de sommaire en images")
for pdf_file, data in structure_sommaire_fichiers.items():
    # Créer le dossier pour la vague concernée si il n'existe pas déjà
    output_path = os.path.join(CHEMIN_FICHIERS_IMGS_SOMMAIRE, pdf_file.split("/")[-1].split("-")[-2])

    # Récupérer les pages de sommaire pour le fichier PDF actuel
    summary_pages = data['summary_pages']
    if summary_pages:

        # Convertir les pages de sommaire en images
        images = convert_pdf_pages_to_images(pdf_file, summary_pages, output_path)

        structure_sommaire_fichiers[pdf_file]['summary_images'] = images
        logging.info(f"\nFichier : {pdf_file} - Pages de sommaire converties en images : {images}")

    else:
        structure_sommaire_fichiers[pdf_file]['summary_images'] = []

logging.info(f"\nConversion des pages de sommaire en images terminée")

print(structure_sommaire_fichiers) # Vérification du succès de l'opération

# 3ème étape : classification des sommaires en deux catégories
# Objectif : après avoir identifié les pages contenant un sommaire, nous allons demander au LLM de les classer en deux catégories de sommaire
# "table globale" : tableau de sommaire classique contenant les quatre colonnes (Entreprise, projet, Thématique et page)
# "table par thème" : plusieurs tableaux en présentant en grand titre le thème et en dessous les projets associés à ce thème, avec la page correspondante et l'entreprise

SYSTEM_PROMPT = """\
Tu es un expert en analyse de documents structurés.
Tu dois identifier le FORMAT du sommaire présent dans le document fourni.
Tu ne dois PAS lister les entrées du sommaire, uniquement analyser sa mise en forme.
Réponds UNIQUEMENT avec un objet JSON valide, sans texte autour, sans balises Markdown.\
"""
 
USER_PROMPT_TEMPLATE = """\

Voici un extrait de ce document en images de son sommaire concernant les projets d'entreprises associés à une thématique.
Tu retrouveras dans ce sommaire normalement le nom de l'entreprise, le nom du projet et la thématique associée.

Attention, point important, le sommaire peut se faire sur plusieurs pages, il y aura plusieurs images renseignées pour cela.

Analyse la structure de mise en forme du sommaire et retourne un JSON respectant exactement ce schéma :
 
{{
  "style_global": "<table des matières avec comme colonnes : Entreprises/Projets/Thématique/Page | table des matières avec une séparation par thématique et comme colonnes : Entreprises/Projets/Pages>",
  "marqueur_debut": "<libellé exact ou motif qui introduit le sommaire, ex. 'Sommaire', '## Table des matières'>",
  "marqueur_fin": "<texte ou motif qui marque la fin du sommaire, ex. début de la prochaine section>",
  "niveaux": [
    {{
      "profondeur":        <entier, 1 = niveau racine>,
      "exemple_entree":    "<une ligne typique copiée depuis le document avec entreprise/projet/thématique/page | entreprise/projet/page>",
      "a_numerotation":    <true | false>,
      "style_indentation": "<espace | tiret | point | aucune>"
      ""
    }}
  ],
  "nb_entrees":       <entier — nombre total d'entrées dans le sommaire de cet extrait>,
  "confiance":        <float entre 0 et 1>,
  "remarques":        "<observations libres, peut être vide>"
}}
 
Document :
────────────────────────────────
{document_texte}
────────────────────────────────
"""
