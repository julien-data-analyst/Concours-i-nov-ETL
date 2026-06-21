###########################-
# Sujet : PDF preprocessing (TOC classification)
# Auteur : julien-data-analyst
# Date : 2026-06-13 / 2026-06-21
# ###########################-
from __future__ import annotations

# Import librairies
import os
from packages.pdf_preprocessing import get_pdf_files
from packages.gestion_modele_llm import charger_modele, extraire_json, MODEL_ID, appeler_modele
from dataclasses import dataclass, asdict
from dotenv import load_dotenv
import logging
load_dotenv()
import json
from PIL import Image

# Configuration globale
CHEMIN_FICHIERS_IMGS_SOMMAIRE = os.getenv("CHEMIN_FICHIERS_IMGS_SOMMAIRE")
CHEMIN_ENTREES_SORTIES = os.getenv("CHEMIN_EXTRACTION_JSON_SOMMAIRES")

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
class ValeurSommaire:
    """Valeur d'une ligne de sommaire inféré par le modèle."""
    entreprise:     str                  # Nom de l'entreprise
    projet:   str                   # Nom du projet
    thematique:     str                   # thématique concernée
    page:       int                   # Numéro de page concerné par ce projet

@dataclass
class GlobalSommaire:
    """Valeurs concernant le sommmaire"""
    nb_entrees: int
    style_global: str
    projets: list[ValeurSommaire]
    confiance: float
    remarque: str

#######################################-

# Aller chercher les fichiers PDF dans le répertoire spécifié
logging.info(f"Recherche des images de sommaires dans le répertoire : {CHEMIN_FICHIERS_IMGS_SOMMAIRE}")


###############################
# Les prompts pour le LLM
###############################

SYSTEM_PROMPT = """\
Tu es un expert en analyse de documents structurés.
Tu dois identifier le FORMAT du sommaire présent dans les images fournies.
Réponds UNIQUEMENT avec un objet JSON valide, sans texte autour, sans balises Markdown.\
"""

PROMPT_SOMMAIRE = """\
À partir des images suivantes, extrais le sommaire ou table des matières.
Base-toi beaucoup plus sur l'aspect visuel de l'image.

Retourne uniquement un JSON contenant ce schéma pour chaque ligne :
{
    "nb_entrees" : <le nombre de projets dans ce sommaire en int>,
    "style_global" : <texte qui est soit "table simple" ou "table séparée">,
    "projets" : <liste contenant les JSON des différents projets>,
    "confiance": <float entre 0 et 1>,
    "remarque": <texte sur le contenu ou la structure>
}

Pour chaque entrée de la liste "projets" :
{
    "entreprise" : <le nom de l'entreprise qui se trouve dans la première colonne>,
    "projet" : <le nom du projet qui se trouve dans la deuxième colonne>,
    "thematique" : <la thématique concernée>,
    "page" : <dernière colonne du sommaire représentant le numéro de page concernant ce projet>
}

Règles de recherche pour "thematique" :

* Soit elle se trouve dans la ligne concernée en étant la troisième colonne

* Soit les projets sont séparés par thématique, il faudra donc récupérer l'information à partir des sous-titres écrits pour chacun des groupes

"""


###########################
# Le parsing du JSON renvoyé par le LLM
###########################
def _parse_format_sommaire(raw_json: str) -> GlobalSommaire:
    """Extrait le JSON de la réponse et construit un ValeurSommaire.
    
    Args:
        raw_json: texte brut renvoyé par le modèle (peut contenir du texte autour du JSON)

    Returns:
        ValeurSommaire: instance représentant le format du sommaire détecté
    """
    print(f"Texte brute du LLM à parser en JSON : {raw_json}")
    data = json.loads(extraire_json(raw_json))
 
    return ValeurSommaire(
        style_global=data.get("style_global", "aucun"),
        nb_entrees=int(data.get("nb_entrees", 0)),
        confiance=float(data.get("confiance", 0.0)),
        projets=json.load(data.get("projets", [])),
        remarque=data.get("remarque", "")
    )

# ──────────────────────────────────────────
# Fonction principale publique
# ──────────────────────────────────────────
def extraire_sommaire(
    image_paths: list[str],
    model_id: str = MODEL_ID,
) -> GlobalSommaire:
    """
    Analyse le sommaire et retourne un JSON au format GlobalSommaire

    Args:
        image_paths: liste de chemins vers les images des pages de sommaire
        model_id: identifiant du modèle à utiliser

    Returns:
        GlobalSommaire
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

    user_prompt = PROMPT_SOMMAIRE
    logging.info(
        "Envoi du prompt de classification (format sommaire)… (%d image(s))",
        len(images),
    )

    raw = appeler_modele(
        model, processor, user_prompt,
        max_new_tokens=128000,
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
for vague in range(1, 13):
    # Récupérer les fichiers images dans le répertoire 
    liste_imgs = get_pdf_files(CHEMIN_FICHIERS_IMGS_SOMMAIRE+"/"+str(vague), ".png")
    print(liste_imgs)
    # Sortie du JSON de la structure du sommaire
    sortie_llm_json = extraire_sommaire(liste_imgs)

    # Sauvegarde de la structure des sommaires dans un fichier JSON
    output_json_path = os.path.join(CHEMIN_FICHIERS_IMGS_SOMMAIRE, f"extraction_sommaire_{vague}.json")
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(asdict(sortie_llm_json), f, ensure_ascii=False, indent=4)
    logging.info(f"Extraction des sommaires sauvegardée dans le fichier : {output_json_path}")