###########################-
# Sujet : PDF preprocessing (TOC classification)
# Auteur : julien-data-analyst
# Date : 2026-06-13 / 2026-06-21
# ###########################-
from __future__ import annotations

# Import librairies
import os
from packages.pdf_preprocessing import get_pdf_files, find_summary_pages, convert_pdf_page_to_image, convert_pdf_pages_to_images, filter_pages_without_text
from packages.gestion_modele_llm import charger_modele, generer, extraire_json, MODEL_ID, DEVICE, appeler_modele
from dataclasses import dataclass, field, asdict
from dotenv import load_dotenv
import logging
load_dotenv()
import json
from PIL import Image

# Configuration globale
CHEMIN_FICHIERS_PDF = os.getenv("CHEMIN_FICHIERS_PDF")
CHEMIN_FICHIERS_IMGS_SOMMAIRE = os.getenv("CHEMIN_FICHIERS_IMGS_SOMMAIRE")

#print(CHEMIN_FICHIERS_PDF)
structure_sommaire_fichiers = {} # Dictionnaire pour stocker la structure des sommaires par fichier PDF
list_summary_strings = ["Index des entreprises lauréates", "Index des thématiques"]  # Liste des chaînes de caractères à rechercher pour identifier les pages de sommaire

##########################################-
# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

#########################################-

########################################-
# LLM configuration
########################################-

@dataclass
class FormatSommaire:
    """Format du sommaire tel qu'inféré par le modèle."""
    style_global:     str                   # "table_des_matieres" | "liste_puces" | "liste_numerotee"
                                            # | "en_tete_page" | "paragraphe_libre" | "aucun"
    marqueur_debut:   str                   # texte qui ouvre le sommaire  ex. "Sommaire", "Table des matières"
    marqueur_fin:     str                   # texte ou motif qui clôt le sommaire
    nb_entrees:       int                   # nombre total d'entrées détectées dans l'extrait
    confiance:        float                 # score 0-1 fourni par le modèle
    a_numerotation: bool # si le sommaire à une numérotation ou non
    style_indentation: str # style d'indentation
    exemple_entree: str

#######################################-

# Aller chercher les fichiers PDF dans le répertoire spécifié
logging.info(f"Recherche des fichiers PDF dans le répertoire : {CHEMIN_FICHIERS_PDF}")
liste_fichiers_pdf = get_pdf_files(CHEMIN_FICHIERS_PDF)

# 1ère étape : identifier les pages contenant un sommaire dans chaque fichier PDF
logging.info(f"Identification des pages contenant un sommaire dans les fichiers PDF")
for pdf_file in liste_fichiers_pdf:
    summary_pages = find_summary_pages(pdf_file, list_summary_strings)
    summary_pages_filtered = filter_pages_without_text(pdf_file, summary_pages, "SOMMAIRE")
    print(f"Fichier : {pdf_file} - Pages contenant le sommaire des entreprises lauréates : {summary_pages_filtered}\n")
    logging.info(f"\nFichier : {pdf_file} - Pages contenant le sommaire des entreprises lauréates : {summary_pages_filtered}")
    structure_sommaire_fichiers[pdf_file] = {'summary_pages': summary_pages_filtered}
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
        images = convert_pdf_pages_to_images(pdf_file, summary_pages, output_path, dpi=500)

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

###############################
# Les prompts pour le LLM
###############################

SYSTEM_PROMPT = """\
Tu es un expert en analyse de documents structurés.
Tu dois identifier le FORMAT du sommaire présent dans les images fournies.
Réponds UNIQUEMENT avec un objet JSON valide, sans texte autour, sans balises Markdown.\
"""
 
USER_PROMPT_TEMPLATE = """\

Analyse la structure du sommaire visible dans les images et retourne uniquement un JSON valide respectant exactement ce schéma :

{
"style_global": "<une des valeurs autorisées>",
"marqueur_debut": "<texte qui introduit le sommaire>",
"marqueur_fin": "<texte qui marque la fin du sommaire>",
"exemple_entree": "<une ligne représentative recopiée telle qu'elle apparaît>",
"a_numerotation": <true | false>,
"style_indentation": "<aucune | espace | tiret | point>",
"nb_entrees": <entier>,
"confiance": <float entre 0 et 1>
}

Règles de classification pour "style_global" :

* "ENTREPRISE_PROJET_THEME_PAGE"
  Une ligne contient simultanément :
  Entreprise + Projet + Thématique + Numéro de page.

* "THEME_ENTREPRISE_PROJET_PAGE"
  Le sommaire est organisé par blocs de thématiques.
  Sous chaque thématique figurent plusieurs entreprises/projets avec leur page.

Pour déterminer "style_global", privilégier l'organisation visuelle du sommaire plutôt que le contenu textuel isolé d'une seule ligne.

Retourner uniquement le JSON.

"""

#############################################

###########################
# Le parsing du JSON renvoyé par le LLM
###########################
def _parse_format_sommaire(raw_json: str) -> FormatSommaire:
    """Extrait le JSON de la réponse et construit un FormatSommaire.
    
    Args:
        raw_json: texte brut renvoyé par le modèle (peut contenir du texte autour du JSON)

    Returns:
        FormatSommaire: instance représentant le format du sommaire détecté
    """
    print(f"Texte brute du LLM à parser en JSON : {raw_json}")
    data = json.loads(extraire_json(raw_json))
 
    return FormatSommaire(
        style_global=data.get("style_global", "aucun"),
        marqueur_debut=data.get("marqueur_debut", ""),
        exemple_entree=data.get("exemple_entree", ""),
        marqueur_fin=data.get("marqueur_fin", ""),
        nb_entrees=int(data.get("nb_entrees", 0)),
        confiance=float(data.get("confiance", 0.0)),
        a_numerotation=bool(data.get("a_numerotation", False)),
        style_indentation=data.get("style_indentation", "")
    )

# ──────────────────────────────────────────
# Fonction principale publique
# ──────────────────────────────────────────
def classifier_format_sommaire(
    image_paths: list[str],
    model_id: str = MODEL_ID,
) -> FormatSommaire:
    """
    Analyse un extrait de document et retourne le FormatSommaire détecté.

    Args:
        image_paths: liste de chemins vers les images des pages de sommaire
        model_id: identifiant du modèle à utiliser

    Returns:
        FormatSommaire
    """
    # Chargement des images depuis leur chemin sur disque
    images: list[Image.Image] = []
    for path in image_paths:
        try:
            img = Image.open(path)
            img.load()  # force la lecture immédiate (évite les erreurs différées)
            images.append(img)
        except (FileNotFoundError, OSError) as exc:
            logging.warning("Impossible de charger l'image %s : %s", path, exc)

    if not images:
        raise ValueError(
            "Aucune image valide n'a pu être chargée pour la classification du sommaire."
        )

    model, processor = charger_modele(model_id)

    user_prompt = USER_PROMPT_TEMPLATE
    logging.info(
        "Envoi du prompt de classification (format sommaire)… (%d image(s))",
        len(images),
    )

    raw = appeler_modele(
        model, processor, user_prompt,
        images=images, system_prompt=SYSTEM_PROMPT,
    )
    logging.debug("Réponse brute :\n%s", raw)

    format_sommaire = _parse_format_sommaire(raw)
    logging.info(
        "Format détecté : style=%s | %d entrées | confiance=%.2f",
        format_sommaire.style_global,
        format_sommaire.nb_entrees,
        format_sommaire.confiance,
    )
    return format_sommaire
 

# Application du LLM sur tous les sommaires pour savoir la structure sur chacun d'entre eux
for pdf_file in liste_fichiers_pdf:

    # Sortie du JSON de la structure du sommaire
    sortie_llm_json = classifier_format_sommaire(structure_sommaire_fichiers[pdf_file]['summary_images'])

    # Sauvegarde de la structure des sommaires dans un fichier JSON
    output_json_path = os.path.join(CHEMIN_FICHIERS_IMGS_SOMMAIRE, f"structure_sommaire_{pdf_file.split('/')[-1].split('.')[0]}.json")
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(asdict(sortie_llm_json), f, ensure_ascii=False, indent=4)
    logging.info(f"Structure des sommaires sauvegardée dans le fichier : {output_json_path}")