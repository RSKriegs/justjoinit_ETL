import re
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from bs4 import BeautifulSoup
from time import sleep
from random import randint

edgedriver_path = r"C:\code\edgedriver\msedgedriver.exe"
service = Service(edgedriver_path)
driver = webdriver.Edge(service=service)
 
# url = "https://justjoin.it/?keyword=data+engineer"
# driver.get(url)
# sleep(randint(3, 5))

# soup = BeautifulSoup(driver.page_source, 'html.parser')
# driver.quit()
 
# base_url = "https://justjoin.it"
# links = soup.find_all("a",href=re.compile("^/offers/.*"))

# top10 = set()
# for link in links:
#     top10.add(base_url+link["href"])
# for link in list(top10)[0:1]:
#     # navigate to page
#     # make soup
#     # get text from all paragraphs
#     service = Service(edgedriver_path)
#     driver = webdriver.Edge(service=service)
#     driver.get(link)
#     sleep(randint(2, 4))
#     soup = BeautifulSoup(driver.page_source, 'html.parser')
#     paragraphs = soup.find_all("div")
#     text = ""
#     for p in paragraphs:
#         text += p.get_text() + " "
#     print(text)
#     driver.quit()

driver.get("https://justjoin.it/offers/miquido-ai-ml-expert-wroclaw")
# sleep(randint(2, 4))
soup = BeautifulSoup(driver.page_source, 'html.parser')
paragraphs = soup.find_all("span", class_=re.compile("^css-1ar0l68.*"))
text = ""
for p in paragraphs:
    text += p.get_text() + ","
print(text)
driver.quit()

