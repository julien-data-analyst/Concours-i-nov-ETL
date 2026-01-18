#########################-
# Sujet : Exécuter l'ETL mise en place
# Date : 18/01/2026
#########################-

# Importer les scripts nécessaires à l'exécution
from Extract.PDF_scraping.full_extract_pdf_toc import extract_toc
from Transform.TOC.clean_toc import clean_toc
from Extract.PDF_scraping.full_extract_pdf_project_details import extract_projets
from Transform.Projets.clean_projects_details import clean_project
from Transform.Projets.add_dep_region_name import  add_dep_region_name
from Transform.Projets.add_years_project import add_years_project
from Transform.Projets.add_them_gen import add_them_gen
from Load.CreateBDD.create_bdd import create_bdd
from Load.InsertBDD.insert_bdd import insert_bdd
import pandas as pd

# 1ère étape : exécuter le script d'extraction web
print("\n---- Etape 1 : Extraction des données sur le site du gouvernement ----")
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from Extract.Web_scraping.concoursScrapy.concoursScrapy.spiders.concours_i_nov_spiders import ConcoursINovSpider

process = CrawlerProcess(get_project_settings())
process.crawl(ConcoursINovSpider)
process.start()
print("\n---- Etape 1 finie ----")

# 2ème étape : exécuter les scripts d'extraction pdf
print("\n---- Etape 2 : Extraction des données PDF sur les projets ----")
extract_toc()
clean_toc()
toc_contents = pd.read_json(path_or_buf="Data/concours_toc.jsonl", lines=True,encoding="utf-8",orient="records")
toc_project_contents = pd.DataFrame(extract_projets(toc_contents))
toc_project_contents = pd.concat([toc_contents, toc_project_contents], axis=1)
toc_project_contents.to_csv("Data/ToClean/concours_projet_1_12.csv", sep=";", index=False)
print("\n---- Etape 2 finie ----")

# 3ème étape : processus de nettoyage des données
print("\n---- Etape 3 : Nettoyage des données extraites ----")
clean_project()
add_dep_region_name()
add_years_project()
add_them_gen()
print("\n ---- Etape 3 finie ----")

# 4ème étape : création BDD + insertion BDD
print("\n---- Etape 4 : Création BDD + Insertion dans la BDD ----")
# Connexion à la bdd pour créer les différentes tables
#print(os.getenv("DBNAME"), os.getenv("DBUSERNAME"), os.getenv("DBPASSWORD"))
import os
import Load.ConnexionBDD.connexion as bdd_conn
from dotenv import load_dotenv

load_dotenv()

# Connexion à la bdd
if os.getenv("DBEXTERNALURL") != "":
    conn, cur = bdd_conn.connexion_bdd(database_url=os.getenv("DBEXTERNALURL"))
else:
    conn, cur = bdd_conn.connexion_bdd(os.getenv("DBNAME"), os.getenv("DBUSERNAME"), os.getenv("DBPASSWORD"))

create_bdd(cur, conn)
insert_bdd(cur, conn)

# Fermer les instances de connexions
cur.close()
conn.close()
print("\n ---- Etape 4 finie ----")