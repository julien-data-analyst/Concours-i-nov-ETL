###########################-
# Sujet : PDF preprocessing
# Auteur : julien-data-analyst
# Date : 2026-06-13
# ###########################-
import os # For path operations
import fitz  # PyMuPDF
import logging # For logs operations
import re

# Fonction de nettoyage de texte simple
def normalize(text):
    text = text.lower()
    text = re.sub(r"\s+", " ", text)  # remplace multiples espaces / \n
    return text.strip()


# Configuration du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Fonctions de prétraitement des fichiers PDF

# Fonction pour répérer les pages où on a le texte recherché
def find_pages_with_text(pdf_path, search_text):
    """
    Recherche les pages d'un fichier PDF contenant un texte spécifique.

    Args:
        pdf_path (str): Chemin vers le fichier PDF.
        search_text (str): Texte à rechercher dans le PDF.

    Returns:
        list: Liste des numéros de pages contenant le texte recherché.
    """
    pages_with_text = []
    with fitz.open(pdf_path) as pdf:
        for page_number in range(len(pdf)):
            page = pdf[page_number]
            text = normalize(page.get_text())
            if normalize(search_text) in text:
                pages_with_text.append(page_number + 1)  # +1 pour numéroter les pages à partir de 1
    return pages_with_text

# Aller chercher les fihciers PDF dans le répertoire spécifié
def get_pdf_files(directory, extension=".pdf"):
    """
    Récupère tous les fichiers PDF dans un répertoire donné.

    Args:
        directory (str): Chemin vers le répertoire.

    Returns:
        list: Liste des chemins complets des fichiers PDF.
    """
    pdf_files = []
    
    for root, dirs, files in os.walk(directory):
        #print(files)
        for file in files:
            if file.lower().endswith(extension):
                pdf_files.append(os.path.join(root, file))
    return pdf_files

# Objectif : ici, nous allons trouver les pages contenant un sommaire dans nos différents fichiers PDF
def find_summary_pages(pdf_path, list_strings=["Index des entreprises lauréates"]):
    """
    Recherche les pages d'un fichier PDF contenant un sommaire.

    Args:
        pdf_path (str): Chemin vers le fichier PDF.

    Returns:
        list: Liste des numéros de pages contenant un sommaire.
    """
    summary_pages = []
    
    #print(pdf_path)
    for summary_keyword in list_strings:
        pages = find_pages_with_text(pdf_path, summary_keyword)
        summary_pages.extend(pages)
    
    if summary_pages==[]:
        warning_msg = f"Aucune page de sommaire trouvée dans le fichier : {pdf_path}"
        print(warning_msg)
        logging.warning(warning_msg)

    # Supprimer les doublons et trier les pages
    summary_pages = sorted(set(summary_pages))
    
    return summary_pages

def convert_pdf_page_to_image(pdf_path, page_number, output_image_path, dpi=300):
    """
    Convertit une page spécifique d'un fichier PDF en image.

    Args:
        pdf_path (str): Chemin vers le fichier PDF.
        page_number (int): Numéro de la page à convertir (1-indexed).
        output_image_path (str): Chemin de sortie pour l'image générée.
    """
    with fitz.open(pdf_path) as pdf:
        if 1 <= page_number <= len(pdf):
            page = pdf[page_number - 1]  # Ajuster pour l'indexation 0
            pix = page.get_pixmap(dpi=dpi)  # Résolution de 300 DPI
            pix.save(output_image_path)
            logging.info(f"Page {page_number} du PDF convertie en image : {output_image_path}")

            return output_image_path
            
        else:
            logging.error(f"Numéro de page invalide : {page_number}. Le PDF contient {len(pdf)} pages.")

def convert_pdf_pages_to_images(pdf_path, page_numbers, output_dir, dpi=300):
    """
    Convertit plusieurs pages spécifiques d'un fichier PDF en images. 
    Il les sauvegardes en supprimant ce qu'il existait déjà dans le dossier de sortie.

    Args:
        pdf_path (str): Chemin vers le fichier PDF.
        page_numbers (list): Liste des numéros de pages à convertir (1-indexed).
        output_dir (str): Répertoire de sortie pour les images générées.
    """

    if os.path.exists(output_dir):
        # Supprimer le dossier existant et son contenu
        for root, dirs, files in os.walk(output_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(output_dir)

    os.makedirs(output_dir, exist_ok=True)

    images = []

    with fitz.open(pdf_path) as pdf:
        for page_number in page_numbers:
            if 1 <= page_number <= len(pdf):
                page = pdf[page_number - 1]  # Ajuster pour l'indexation 0
                pix = page.get_pixmap(dpi=dpi)  # Résolution de 300 DPI
                output_image_path = os.path.join(output_dir, f"page_{page_number}.png")
                pix.save(output_image_path)
                images.append(output_image_path)
                logging.info(f"\nPage {page_number} du PDF convertie en image : {output_image_path}")
            else:
                logging.error(f"\nNuméro de page invalide : {page_number}. Le PDF contient {len(pdf)} pages.")

    return images

def filter_pages_without_text(pdf_path, page_numbers, search_text):
    """
    Retourne les pages de page_numbers qui ne contiennent PAS search_text.

    Args:
        pdf_path (str): Chemin du PDF.
        page_numbers (list[int]): Liste des pages à vérifier (1-indexées).
        search_text (str): Texte à rechercher.

    Returns:
        list[int]: Liste des pages ne contenant pas le texte.
    """
    filtered_pages = []

    with fitz.open(pdf_path) as pdf:
        normalized_search = normalize(search_text)

        for page_number in page_numbers:
            if 1 <= page_number <= len(pdf):
                page = pdf[page_number - 1]
                text = normalize(page.get_text())

                if normalized_search not in text:
                    filtered_pages.append(page_number)
            else:
                logging.warning(
                    f"Numéro de page invalide : {page_number}. "
                    f"Le PDF contient {len(pdf)} pages."
                )

    return filtered_pages