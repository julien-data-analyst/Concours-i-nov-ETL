import pandas as pd
projets = pd.read_json(path_or_buf="Data/concours_projet_realisation.jsonl", lines=True,encoding="utf-8",orient="records")

# Créer une colonne thématique général (santé, numérique, environnement, énergie, agriculture, french fab)

## Nettoyage des thématiques obtenues
projets["THEMATIQUE"] = projets["THEMATIQUE"].\
    str.replace("–", "-").\
        str.replace(": ", "").\
        str.replace("deep tech", "deeptech").\
        str.replace("sécurité cybersécurité", "sécurité et cybersécurité").\
        str.replace("santé bioproduction", "santé - bioproduction").\
        str.replace("energies", "énergies").\
        str.replace("economie", "économie")

def create_them_gen(thematique):
    dict_them_gen = {
    "numérique" : ["numérique", 
                   "sécurité et cybersécurité", # Fusionner avec l'autre
                   "numérique deeptech",
                   'numérique deeptech - applications jop paris 2024',
                   'cybersécurité',
                   'transformer les industries culturelles et créatives grâce au numérique',
                   ],

    "french fab" : ["french fab", 
                    'french fab industrie du futur',
                    'french fab - matériaux innovants',
                    'french fab - industrie 4.0'
                    ],
    
    "santé" : ['santé', 
               'santé - bioproduction',
                'santé - chirurgie du futur',
                'santé situations d’urgences',
                'santé - santé mentale et diagnostics rapides et nomades',
                'santé - diagnostic, dépistage et surveillance des pathologies',
                'santé - dispositifs médicaux innovants',
                'santé - outils de modélisation  simulation numériquepour le développement de biomédicaments',
                'expositions chroniques et risques sanitaires'
               ],
    
    "environnement" : [
        'transport et mobilité durable',
        'écosystèmes terrestres, aquatiques et marins',
        'performance environnementale des bâtiments',
        'adaptation des territoires au changement climatique et  métrologie des expositions environnementales',
        'transports, mobilités, villes et bâtiments durables',
        'société inclusive et solidaire',
        'eau et biodiversité',
        'ville en transition',
        'mobilité durable et intelligente',
        'performance environnementale et énergétique des bâtiments',
    ],

    "écologie" : ['transition écologique applications jop paris 2024',
                  'réduction de l’empreinte écologique du numérique',
                  'enjeux de la transition écologique dans l’industrie et l’agriculture',
                    'adaptation au changement climatique',
                    'adaptation des territoires au changement climatique atténuation de ses effets,prévention des risques et métrologie des expositions environnementales',
                    "réduction de l'empreinte environnementale" 
                  ],

    "agriculture" : [
        'agriculture innovante',
        'agriculture, industrie et sylviculture éco-efficientes',
        'alimentation intelligente',
        'alimentation durable pour la santé',
        'industrie et agriculture éco-efficientes',
        'protéines et ferments du futur',
        'adaptation de l’agriculture au changement climatique et gestion des aléas'
    ],

    "énergie" : [
        'énergies renouvelables, stockage et systèmes énergétiques',
        'efficacité en énergie et en ressources',
        'hydrogène',
        'énergies renouvelables, stockage et systèmes énergétiques dont hydrogène',
        'énergies, ressources et milieux naturels' #
    ],

    "économie circulaire" : [
        'économie circulaire',
        'économie circulaire (y compris recyclage des métaux critiques)'
    ],

    "espace" : ['espace']
}
    result = ""
    for them_gen in dict_them_gen:
        if thematique in dict_them_gen[them_gen]:
            result = them_gen
    
    return result


## Ajout de la colonne thématique générale

#print(projets["THEMATIQUE"].unique())
projets["THEMATIQUE_GENERALE"] = projets["THEMATIQUE"].map(create_them_gen)
#print(projets["THEMATIQUE_GENERALE"].value_counts(dropna=False))

## Export jsonl 
projets.to_json(path_or_buf="Data/concours_projet_thematique.jsonl", orient="records", lines=True, force_ascii=False)