"""
llm_utils_ollama_cloud.py
─────────────────────────────────────────────────────────────────────────────
Variante de llm_utils_ollama.py utilisant **Ollama Cloud** (modèles hébergés
sur ollama.com, exécution déportée) au lieu d'un serveur Ollama local.

Avantage : aucune ressource locale n'est utilisée (RAM/CPU), accès à des
modèles bien plus gros (ex. qwen3-vl:235b-cloud) qu'il serait impossible de
faire tourner localement sur un CPU.
Inconvénient : nécessite une connexion internet et une clé API Ollama
(quota / facturation selon l'offre ollama.com).

Prérequis :
  1. Créer une clé API sur https://ollama.com (rubrique "API keys")
  2. La définir en variable d'environnement, par ex. dans un fichier .env :
       OLLAMA_API_KEY=votre_cle_api
     puis charger ce .env via `python-dotenv` (déjà fait dans le script
     principal avec `load_dotenv()`)
  3. Installer le client Python :
       pip install ollama python-dotenv

Interface IDENTIQUE à llm_utils.py / llm_utils_ollama.py :
  - charger_modele(model_id)               -> (model, processor)
  - appeler_modele(model, processor, ...)  -> str
  - generer(prompt, ...)                   -> str
  - extraire_json(raw_text)                -> str

=> Pour basculer tout le pipeline, remplacer dans chaque fichier :

    from llm_utils_ollama import charger_modele, appeler_modele, extraire_json, MODEL_ID

par :

    from llm_utils_ollama_cloud import charger_modele, appeler_modele, extraire_json, MODEL_ID

Ici, `model` (retourné par charger_modele) est le nom du modèle cloud (str),
et `processor` est l'instance `ollama.Client` configurée pour l'API cloud —
elle doit être passée telle quelle à appeler_modele().
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import base64
import io
import os
import logging
from typing import Optional

from ollama import Client
import ollama
from PIL import Image

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


# ──────────────────────────────────────────
# Constantes par défaut
# ──────────────────────────────────────────

# Seul modèle Qwen multimodal disponible sur Ollama Cloud à ce jour.
# Voir https://ollama.com/library pour la liste à jour des modèles "-cloud".
MODEL_ID = "gemma3:4b-cloud" # Gratuit quota limité
DEVICE   = "cloud"  # informatif uniquement : l'exécution est déportée sur ollama.com

OLLAMA_CLOUD_HOST = "https://ollama.com"


# ──────────────────────────────────────────
# Client Ollama Cloud (mis en cache)
# ──────────────────────────────────────────

_client_cache: dict[str, Client] = {}


def _get_client() -> Client:
    """
    Construit (ou récupère depuis le cache) un client Ollama pointant vers
    l'API cloud, authentifié via la clé API OLLAMA_API_KEY.
    """
    if "cloud" in _client_cache:
        return _client_cache["cloud"]

    api_key = os.environ.get("OLLAMA_API_KEY")
    if not api_key:
        raise RuntimeError(
            "La variable d'environnement OLLAMA_API_KEY n'est pas définie. "
            "Crée une clé API sur https://ollama.com (rubrique 'API keys') "
            "et ajoute-la dans ton fichier .env :\n"
            "    OLLAMA_API_KEY=votre_cle_api"
        )

    client = Client(
        host=OLLAMA_CLOUD_HOST,
        headers={"Authorization": f"Bearer {api_key}"},
    )
    _client_cache["cloud"] = client
    log.info("Client Ollama Cloud initialisé (host=%s).", OLLAMA_CLOUD_HOST)
    return client


# ──────────────────────────────────────────
# "Chargement" du modèle
# ──────────────────────────────────────────

def charger_modele(model_id: str = MODEL_ID, **_kwargs):
    """
    Prépare l'accès au modèle cloud `model_id`.

    Avec Ollama Cloud, il n'y a rien à télécharger ni à charger en mémoire
    localement : on vérifie simplement que le client est configuré (clé API
    présente) et on retourne (model_id, client).

    Paramètres
    ----------
    model_id : nom du modèle cloud (ex. "qwen3-vl:235b-cloud")
    **_kwargs: ignorés (compatibilité de signature)

    Retour
    ------
    tuple (model_id, client) — `client` est une instance ollama.Client
    à transmettre telle quelle à appeler_modele().
    """
    client = _get_client()
    return model_id, client


# ──────────────────────────────────────────
# Conversion d'images PIL -> base64
# ──────────────────────────────────────────

def _image_to_base64(image: Image.Image, format: str = "PNG") -> str:
    buffer = io.BytesIO()
    img = image
    if format.upper() == "JPEG" and img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.save(buffer, format=format)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


# ──────────────────────────────────────────
# Appel du modèle (texte + images optionnelles)
# ──────────────────────────────────────────

def appeler_modele(
    model,
    processor,
    prompt: str,
    images: Optional[list[Image.Image]] = None,
    system_prompt: Optional[str] = None,
    max_new_tokens: int = 1024,
    do_sample: bool = False,
    temperature: Optional[float] = None,
    num_ctx: Optional[int] = None,
) -> str:
    """
    Envoie un prompt (+ images optionnelles, + system prompt optionnel) au
    modèle via Ollama Cloud et retourne la réponse générée (texte uniquement).

    Paramètres
    ----------
    model     : nom du modèle cloud (str), retourné par charger_modele()
    processor : instance ollama.Client configurée pour le cloud,
                retournée par charger_modele()
    num_ctx   : optionnel. Les modèles cloud disposent généralement d'une
                fenêtre de contexte très large gérée côté serveur ; ce
                paramètre n'est transmis que s'il est explicitement fourni.

    Autres paramètres : identiques à llm_utils.appeler_modele().
    """
    model_id: str = model
    client: Client = processor

    messages: list[dict] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    user_message: dict = {"role": "user", "content": prompt}
    if images:
        user_message["images"] = [_image_to_base64(img) for img in images]

    messages.append(user_message)

    options: dict = {
        "num_predict": max_new_tokens,
        "temperature": (temperature if (do_sample and temperature is not None) else 0.0)
        if not do_sample else (temperature if temperature is not None else 0.7),
    }
    if num_ctx is not None:
        options["num_ctx"] = num_ctx

    response = client.chat(model=model_id, messages=messages, options=options)
    return response["message"]["content"].strip()


# ──────────────────────────────────────────
# Raccourci : charger + appeler en une fois
# ──────────────────────────────────────────

def generer(
    prompt: str,
    images: Optional[list[Image.Image]] = None,
    system_prompt: Optional[str] = None,
    model_id: str = MODEL_ID,
    max_new_tokens: int = 1024,
    **kwargs,
) -> str:
    model, processor = charger_modele(model_id)
    return appeler_modele(
        model, processor, prompt,
        images=images, system_prompt=system_prompt,
        max_new_tokens=max_new_tokens, **kwargs,
    )


# ──────────────────────────────────────────
# Aide JSON : extraction d'un objet JSON depuis une réponse libre
# ──────────────────────────────────────────

def extraire_json(raw_text: str) -> str:
    """Identique à llm_utils.extraire_json — extrait la sous-chaîne JSON."""
    debut = raw_text.find("{")
    fin   = raw_text.rfind("}") + 1
    if debut == -1 or fin == 0:
        raise ValueError(f"Aucun JSON trouvé dans la réponse :\n{raw_text}")
    return raw_text[debut:fin]


# ──────────────────────────────────────────
# CLI rapide pour test
# ──────────────────────────────────────────

if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv

    load_dotenv()

    question = " ".join(sys.argv[1:]) or "Présente-toi en une phrase."
    print(f"Prompt : {question}\n")
    reponse = generer(question, max_new_tokens=200)
    print(f"Réponse :\n{reponse}")