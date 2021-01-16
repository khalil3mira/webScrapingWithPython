from selenium import webdriver
import time

import requests
from bs4 import BeautifulSoup
import pickle
import re
from IPython.display import clear_output

import pandas as pd

#Fetch all pages in google search results with the e-commerce jumia
search_query = input("Merci d'entré l'article a chercher: ")

if 'jumia' not in search_query:
    search_query += " jumia"

search_query = search_query.replace(' ', '+')  # structuring our search query for search url.

executable_path = r'./chromedriver.exe'
browser = webdriver.Chrome(executable_path=executable_path)

links = []

for i in range(1, 50):

    browser.get("https://www.google.com/search?q=" + search_query + "&start=" + str(i))
    matched_elements = browser.find_elements_by_xpath('//a[starts-with(@href, "https://www.jumia.")]')

    if matched_elements:
        matched_elements[0].click()

        # locate the span elements which exist under your desired div
        spans_to_iterate = browser.find_elements_by_xpath("//a[contains(@class,'core')]")
        # print(spans_to_iterate)
        link_list = []

        # iterate span elements to save the href attribute of a element
        for span in spans_to_iterate:
            # get the href element, where 'a' element is following sibling of span.
            link_text = span.get_attribute("href")
            link_list.append(link_text)
            links.append(link_list)
        try:
            if browser.find_element_by_xpath('.//a[@title="Suivant"]'):
                browser.find_element_by_xpath('.//a[@title="Suivant"]').click()
                time.sleep(5)
        except:
            continue
    else:
        break

browser.close()

#clean the results and make them unique
clean_links = []
for link in links:
    for l in link:
        if l not in clean_links and l != None:
            clean_links.append(l)

print('we found ' + str(len(clean_links)) + ' clean result')

# the function that will convert all urls to script
def url_to_transcript1(clean_link):
    percent=((clean_links.index(clean_link)+1)/len(clean_links))*100
    print(str('%.2f' %percent)+'%', end='')
    print('.', end='')
    response= requests.get(clean_link)
    print('.', end='')
    soup = BeautifulSoup(response.text,"html.parser")
    print('.', end='')
    name = soup.find_all('div', attrs={'class': '-fs0 -pls -prl'})
    details = soup.find_all('div', attrs={'class': 'markup -pam'})
    marque = soup.find_all('div', attrs={'class': '-fs14 -pvxs'})
    price = soup.find_all('span', attrs={'class': '-b -ltr -tal -fs24'})
    discount = soup.find_all('span', attrs={'class': 'tag _dsct _dyn -mls'})
    car = soup.find_all('div', attrs={'class': 'markup -pam'})
    descrptivetechnique = soup.find_all('ul', attrs={'class': '-pvs -mvxs -phm -lsn'})
    avis = soup.find_all('div', attrs={'class': 'stars _m -mvs'})
    print('.', end='')
    numcomments = soup.find_all('div', attrs={'class': 'cola -phm -df -d-co'})
    comments = soup.find_all('p', attrs={'class': '-pvs'})

    Name = []
    Deatils = []
    Marque = []
    Prix = []
    Discount = []
    Car = []
    Des = []
    Avis = []
    Numcmts = []
    Cmts = []
    for x in range(len(marque)):
        Name.append(name[x])
        Deatils.append(details[x])
        Marque.append(marque[x])
        Prix.append(price[x])
        Discount.append(discount[x])
        Car.append(car[x])
        Des.append(descrptivetechnique[x])
        # Avis.append(avis[x])
        Numcmts.append(numcomments[x])
        # Cmts.append(comments[x])
    print('.', end='')
    clear_output(wait=True)
    return Name, Deatils, Marque, Prix, Discount, Car, Des, Avis, Numcmts, Cmts

#apply on all the clean urls
jumia = [url_to_transcript1(u) for u in clean_links]

Name=[]
Deatils=[]
Marque=[]
Prix=[]
Discount=[]
Car=[]
Des=[]
Avis=[]
Numcmts=[]
Cmts=[]
for item in jumia:
    Name.append(item[0])
    Deatils=[].append(item[1])
    Marque.append(item[2])
    Prix.append(item[3])
    Discount.append(item[4])
    Car.append(item[5])
    Des.append(item[6])
    Avis.append(item[7])
    Numcmts.append(item[8])
    Cmts.append(item[9])


def clean_text(column):
    clean = []

    for x in range(len(column)):
        for item in column[x]:
            clean.append((item.text))
    return clean


def clean_text_a(column):
    clean = []

    for x in range(len(column)):
        for item in column[x]:
            clean.append((item.a.text))
    return clean


def clean_list_li(column):
    clean = []
    for x in range(len(column)):
        cart = ' '
        for item in column[x]:
            items = []
            items = item.find_all('li')
            for y in range(len(items)):
                cart += str(items[y].text) + ','
        clean.append(cart)
    return clean


def clean_coms(column):
    clean = []
    for x in range(len(column)):
        for item in column[x]:
            clean.append((item.text))
    return clean

# Add our data to dataframe then to csv and xlsx files
df = pd.DataFrame(pd.Series(clean_text_a(Marque)),columns=['Marque'])
df["Name"] = pd.Series(clean_text(Name))
df["Caractérstique"]=pd.Series(clean_list_li(Car))
df["Description Téchnique"]=pd.Series(clean_list_li(Des))
df["Réduction"]=pd.Series(clean_text(Discount))
df["Prix avec réduction"]=pd.Series(clean_text(Prix))
df["Commentaires"]=pd.Series(clean_coms(Numcmts))
df["lien"]=pd.Series(clean_link)

df.to_excel('jumia_'+search_query+'.xlsx', sheet_name='Sheet1')
df.to_csv ('jumia_'+search_query+'.csv', index = False, header=True)

