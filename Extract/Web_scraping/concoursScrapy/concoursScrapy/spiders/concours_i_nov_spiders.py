import scrapy


class ConcoursINovSpider(scrapy.Spider):
    name = "concoursinov"

    start_urls = ["https://www.enseignementsup-recherche.gouv.fr/fr/rechercher-une-publication/collection_title/accueil-collection.i-nov-laureats-du-concours-d-innovation?page=1"]
        
    custom_settings = {
        "FEEDS": {
            "../../../../Data/concours.jsonl": {
                "format": "jsonlines",
                "encoding": "utf8",
                "overwrite": True,
            }
        }
    }

    # Appel de la page principal
    def parse(self, response):

        # Récupérer les différentes brochures des concours
        liste_concours = response.xpath('//div[contains(@class, "views-infinite-scroll-content-wrapper")]//article[@class="publication-research-article"]')

        # Récupérer les différentes infomations dans des listes

        for edition in liste_concours:
            
            ################################
            # URL de la page du concours
            # On génère le deuxième URL
            ################################
            link_concours = edition.\
                xpath('.//a/@href').\
                    get()
            link_concours_response = response.urljoin(link_concours)

            # Gardons les données récupérées dans un dictionnaire
            item = {
            ## Titre
            "Titre" : edition.\
                xpath('.//a/text()').\
                    re("[^\n]+")[0],

            ## Lien de la page web concernant ce concours
            "WEB_URL" : link_concours_response,

            ## Numéro de la vague
            "Vague" : int(edition.\
                xpath('.//div[@class="publication-research-article__editing"]//div/text()').\
                    re("\d+")[0]),

            ## Description de l'édition
            "Description" : edition.\
                xpath('.//div[@class="section-chapo"]/text()').\
                    re("[^\r+]+")[0]
            }

            # On transmet les informations dans le prochain callback avec l'URL générée
            yield scrapy.Request(
                url=link_concours_response, # L'URL générée dynamiquement
                callback=self.parse_concours, # La méthode de parse à utiliser
                meta={"item" : item} # les métadonnées à envoyer (s'il en a)
            )

    # callback suivant (récupérer des informations supplémentaires)
    def parse_concours(self, response):
        
        # Récupérer les données déjà récupérées
        item = response.meta["item"]

        # Récupérer des informations supplémentaires
        item["Editeurs_URL"] = [response.urljoin(elt) for elt in response.xpath('//div[contains(@class, "publication-edit__content")]//a/@href').getall()]
        item["Editeurs"] = response.xpath('//div[contains(@class, "publication-edit__content")]//a/text()').getall()
        item["Parution"] = response.xpath('//time/text()').get()
        item["Presentation"] = ' '.join(response.xpath('//div[contains(@class, "block-field-blocknodepublicationfield-presentation")]//p/text()').getall())
        item["PDF_URL"] = response.urljoin(response.xpath('//a[@class="file-link"]/@href').get())

        yield item