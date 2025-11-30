Concours i-nov (collecte et préparation des données) :

Dans le cadre de ce projet, nous avons mené la création d'un script Python de type ETL pour extraire, transformer et charger les données dans une BDD PostGreSQL.
La problématique est que nous devons collecter ces données sur des fichiers PDF en prenant le lien ci-dessous :
https://www.enseignementsup-recherche.gouv.fr/fr/rechercher-une-publication/collection_title/accueil-collection.i-nov-laureats-du-concours-d-innovation?page=1

1ère partie : téléchargement des fichiers PDF :

Chaque block de ces palmarès permet de récupérer le lien correspondant pour accéder au fichier PDF :
main[id = "main-content"].div[id = "block-heu-esr-theme-content"].div[class=block-extra-field-blockconfig-pagessearch-publicationsearch-page-publication].div[class="views-infinite-scroll-content-wrapper"]

récupérer dans chacune de ces div class wrapper :
le titre contenu dans la balise <a>
le lien en question (à mettre début : https://www.enseignementsup-recherche.gouv.fr/)
le numéro de la vague : div[class=publication-research-article__additional]
la petite description : div[class=section-chapo]

Pour récupérer ces informations dans des listes :
titre : liste_concours.xpath('.//a/text()').getall()
lien : liste_concours.xpath('.//a/@href').getall()
numéro de la vague : liste_concours.xpath('.//div[@class="publication-research-article__editing"]/div/text()').getall()
description : liste_concours.xpath('.//div[@class="section-chapo"]/text()').getall()

Aller dans chacun de ces liens et récupérer ces informations :
date de parution : <time>
récupérer la présentation : div[class="block-field-blocknodepublicationfield-presentation"]
récupérer le lien du fichier : a[class = "file-link"]

Lire les fichiers PDF depuis leurs liens et récupérer :
- les données de la page "index des entreprises lauréates" sur chaque projet avec la thématique concernée
- Récupérer les informations précises de chacun de ces projets dans le PDF
    - Localisation
    - Réalisation 
    - Montant du projet
    - Aide accordée / Aide PIA
    - Contact presse / Contact
    - Logo de l'entreprise (à voir si on peut le récupérer)
    - Nom de l'entreprise
    - Titre du projet
    - Description du projet / Objectif du projet

Application :
1er script Python : collecte des données webs (Scraping Web)
2ème script Python : collecte des données sur les PDF (projets / Scraping PDF)
3ème script Python : Transformation et nettoyage des données (séparation / conversion type / etc)
4ème script Python : Création du BDD et insertion des données sous PostGreSQL

Dossier Data : données brutes / données nettoyées
Dossier Scraping Web : le scraping web
    package : script aidant au script principal
    script_principal : scraping web et téléchargement des PDF
Dossier Scraping PDF : le scraping PDF
    package
    script_principal
Dossier Transformation et nettoyage : Préparation de toutes les données pour qu'elles soient possibles de les insérer
Dossier BDD PostGreSQL : Création et insertion des données dans la BDD (Modèle Conceptuel / Relationnel)


Librairies Python pour ce projet :
- uv pour le gestionnaire de librairies
- Scrapy pour le web scraping (découvrir)
- PyMuPDF pour PDF scraping (découvrir)
- Pandas pour du transformation et nettoyage de données
- psycopg pour la BDD PostgreSQL (découvrir)

Retour :
- concours_i_nov : Dataframe contenant les informations sur les concours en générales (Web)
- projets_laureates : DataFrame contenant les différents projets sélectionnées de tous les concours (PDF)
