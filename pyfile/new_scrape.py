# Import for processing XML
from bs4 import BeautifulSoup
import time

# Import for requesting HTML
import urllib
import urllib.request
from urllib.error import HTTPError

# Import for text processing
import io
import re

# Import for data processing and organization
import pandas as pd
import numpy as np

# Find all the categories
url = "http://export.arxiv.org/oai2?verb=ListSets"
u = urllib.request.urlopen(url, data = None)
f = io.TextIOWrapper(u,encoding='utf-8')
text = f.read()
soup = BeautifulSoup(text, 'xml')
all_cat = [sp.text for sp in soup.findAll("setSpec")]

# Export the categories to a txt files
f = open("all_cat_v01.txt", "w")
f.write(",".join(all_cat))
f.close()

def scrape(cat):

    '''
    Function to scrape all the paper from a category

    INPUT : category (String)
    OUTPUT: dataframe that contains doi, date, title, authors, category for each paper (pandas.DataFrame)
    '''

    # Initialization
    df = pd.DataFrame(columns=("doi", "date", "title", "authors", "category"))
    base_url = "http://export.arxiv.org/oai2?verb=ListRecords&"
    url = base_url + "set={}&metadataPrefix=arXiv".format(cat)

    # while loop in order to loop through all the resutls
    while True:
        # print url to keep track of the progress
        print(url)
        # accessing the url
        try:
            u = urllib.request.urlopen(url, data = None)
        except HTTPError as e:
            # Incase of some error that require us to wait
            if e.code == 503:
                to = int(e.hdrs.get("retry-after", 30))
                print("Got 503. Retrying after {0:d} seconds.".format(to))
                time.sleep(to)
                continue # Skip this loop, continue to the next one
            else:
                raise

        # read the request
        f = io.TextIOWrapper(u,encoding='utf-8')
        text = f.read()
        soup = BeautifulSoup(text, 'xml')

        # collect the data
        for record in soup.findAll("record"):
            try:
                doi = record.find("identifier").text
            except:
                doi = np.nan

            try:
                date = record.find("created").text
            except:
                date = np.nan

            try:
                title = record.find("title").text
            except:
                title = np.nan

            try:
                authors = ";".join([author.get_text(" ") for author in record.findAll("author")])
            except:
                authros = np.nan

            try:
                category = record.find("setSpec").text
            except:
                category = np.nan

            df = df.append({"doi":doi, "date":date, "title":title, "authors":authors, "category":category}, ignore_index=True)


        # resumptionToken help to find if there are more results
        token = soup.find("resumptionToken")
        if token is None or token.text is None:
            break
        else:
            url = base_url + "resumptionToken=%s"%(token.text)

    return(df)

# Initialize master_df that contains all the data points
master_df = pd.DataFrame(columns=("doi", "date", "title", "authors", "category"))
for i in all_cat:
    # Print out the current category for progress tracking
    print("----------------",i,"-------------------")
    df = scrape(i)
    # append the new data to master_df
    master_df = master_df.append(df, ignore_index = True)

# Export the data to a csv file
master_df.to_csv("data.csv")
