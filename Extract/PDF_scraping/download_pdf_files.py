##############################-
# Sujet : Téléchargement des fichiers PDF
# Date : 30/11/2025
#############################-

# Chargement de la librairie pour télécharger les fichiers PDF
import requests
import os

def download_pdf_web(url_pdf: str, path: str) -> str:
    """
    Télécharge un PDF depuis une URL et l'enregistre dans un dossier donné.

    Args:
        url_pdf (str): URL du fichier PDF à télécharger.
        path (str): Chemin du dossier où enregistrer le PDF.

    Returns:
        str: Chemin complet du fichier PDF téléchargé.
    """

    # Création du dossier si besoin
    if path and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

    # Récupération du nom du fichier depuis l'URL
    filename = os.path.basename(url_pdf)
    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"

    # Chemin complet du fichier final
    full_path = os.path.join(path, filename)

    # Requête HTTP
    response = requests.get(url_pdf, stream=True)
    response.raise_for_status()  # Erreur si téléchargement impossible

    # Écriture du fichier en streaming
    with open(full_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    return full_path

if __name__=="__main__":
    url = "https://www.enseignementsup-recherche.gouv.fr/sites/default/files/2022-07/i-nov---palmar-s-vague-8-19069.pdf"
    dossier = "./Data/PDF_files"

    chemin_pdf = download_pdf_web(url, dossier)
    print("PDF téléchargé : ", chemin_pdf)