import csv
import pandas as pd
from helium import *
from bs4 import BeautifulSoup
from newspaper import Article
import time
import urllib

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

names = []

us = pd.read_csv('twitter_US.csv', encoding='ISO-8859-1')
for index, row in us.iterrows():
    if (row['Name'] != ""):
      names.append(row['Name'])

eu = pd.read_csv('twitter_EU.csv', encoding='ISO-8859-1')
for index, row in eu.iterrows():
    if (row['ï»¿name'] != ""):
      names.append(row['ï»¿name'])

chrome_options = Options()
chrome_options.add_argument('--no-sandbox') 
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

for name in names:
  name = name.replace(",", "")
  name = name.replace(".", "")
  print(name)
  name_url = urllib.parse.quote(name)

  # check the number of all content
  url = 'https://guardian.ng/?s=' + name_url + '&page=1'
  driver.get(url)
  homeSoup = BeautifulSoup(driver.page_source, 'html.parser')
  div = homeSoup.find("div", {"class":"pagination"})
  pageLinks = div.find_all("a", {"class": "page-numbers"})
  if pageLinks == []:
    number = 1
  else: 
    number = min(230, int(pageLinks[-1].text))
  # text = div.text
  # if (text != ""):
  #   # print("text is "+ text)
  #   index = text.find('out of ') + 7
  #   text = text[index:]
  #   index = 0
  #   while (text[index].isdigit()):
  #       index += 1
  #   number = int(text[:index+1])
  #   print(number)
  #   if (number > 10000):
  #       number = 10000
  # else:
  #   # print("text is empty")
  #   continue

  links = []
  i = 1
  while (i <= number):
      start = str(i)
      print(i)
      url = 'https://guardian.ng/?s=' + name_url + '&page=' + start
      driver.get(url)
      driver.get(url)
      i += 1

      soup = BeautifulSoup(driver.page_source, 'html.parser')
      table = soup.find("div", {"class": "category-table"})
      rows = table.find_all("div", {"class": "row"})
      for row in rows:
          cells = row.find_all('div', {"class": "cell"})
          for cell in cells:
            link = cell.find('a', href=True)
            # print("https://"+link['href'][2:])
            links.append(link['href'])

  articles = []
  # print("initialize articles")
  for link in links:
      try:
          # print("try statement inside")
          a = Article(link)
          a.download()
          a.parse()
          a.nlp()
          article = {}
          article['title'] = a.title
          article['date'] = a.publish_date
          article['url'] = link
          article['text'] = a.text
          articles.append(article)
      except Exception:
          print("sleep")
          time.sleep(120)
          print("after sleep")
          continue
      

  keys = articles[0].keys()
  file_name = name + '_guardian.csv'
  with open(file_name, 'w') as output_file:
      dict_writer = csv.DictWriter(output_file, fieldnames=keys)
      dict_writer.writeheader()
      dict_writer.writerows(articles)

