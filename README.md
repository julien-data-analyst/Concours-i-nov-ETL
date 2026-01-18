# Concours-I-Nov ETL :

This repositories serve as a ETL to extract Data from PDF files on a website. 
These data are based of the french i-nov competition which we can find on the [enseignementsup-recherche.gouv.fr](https://www.enseignementsup-recherche.gouv.fr/fr/rechercher-une-publication/collection_title/accueil-collection.i-nov-laureats-du-concours-d-innovation?page=1).

To create this ETL, I used the Python language with different librairies like :
- [pymupdf](https://pymupdf.readthedocs.io/en/latest/) : to extract data from the PDF
- [pandas](https://pandas.pydata.org/) : to clean and prepare extracted data
- [scrapy](https://www.scrapy.org/) : to extract data from the website

This goal project was to discover the use of pymupdf and scrapy to the data extraction. It was very interesting to use these libraries and going through the documentation.

# How to use this ETL

In this part, i will show you how to use this ETL and what you need to install to do it.

## Project prerequisites 

- [Python](https://www.python.org/downloads/) (version 3.12.3)
- [PostgreSQL](https://www.postgresql.org/)

After installing the Python and cloned the project, we're gonna create a virtual environment which will be useful to install the necessary librairies.

```
$ python3 -m venv "envConcoursinovWebApp"
$ source /home/.../envConcoursETL/bin/activate
$ pip install -r requirements. txt
```

After that, you need to create a **.env** containing these different environment variables :

```
# By using this
DBNAME=""
DBUSERNAME=""
DBPASSWORD=""

# Or by using this
DBEXTERNALURL = ""
```

**Important note : don't forget to create the PostgreSQL Database to use this ETL, this cannot work without it.**

## To run the ETL

It's very simple, all you need to do is to make this command and the ETL will take care of everything.

```
$ python main.py
```

And now the ETL will be running, it will take sometimes to extract from the website and the PDFs so don't be surprised.

# How it was built

Like you can see, four principal folder was created :
- Data : which contain the extracted and cleaned data
- Extract : contains the Scrapy script and the pymupdf script to extract the Data
- Transform : transform and clean the extracted data 
- Load : load the data into a PostGreSQL

This structure permits to easily concentrate on one task at the time, the longuest of course was to extract the PDF data because the PDF layout changed every 3 or 4 contests. The transform was quite easy after I determined what kind of data i needed.

Of course, this project isn't perfect and I'm planning to make it better.
For the moment, I want to explore the extracted data with a website i'm going to create. So, if you want to checkout this app project, go to the following [link](https://github.com/julien-data-analyst/concours-inov-web-app).