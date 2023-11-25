import re
import csv

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from time import sleep
from random import randint

def extract_array(array):
    temp_list = []
    for v in array:
        temp_list.append(v.get_text())
    return temp_list

def extract_struct(array1, array2):
    temp_list = []
    for k, v in zip(array1, array2):
        temp_list.append({k.get_text(): v.get_text()})
    return temp_list

offer = {
    "link": "",
    "name": "",
    "salary_ranges": [],
    "employment_types": [],
    "company": "",
    "location": [],
    "type_of_work": "",
    "experience": "",
    "operating_mode": "",
    "skills": {},
    "description":""
}
list_of_offers = []

edgedriver_path = r"C:\code\edgedriver\msedgedriver.exe"
service = Service(edgedriver_path)
driver = webdriver.Edge(service=service)
wait = WebDriverWait(driver, 10)

url = "https://justjoin.it/?keyword=data+engineer"
driver.get(url)
sleep(randint(3, 5))

#todo: fix scrolling

# soup = BeautifulSoup(driver.page_source, 'html.parser')
# links = soup.find_all("a",href=re.compile("^/offers/.*"))

# List to store extracted links
set_of_links = set()
n = 1  # Initial value for n
scroll_distance = 360  # Scroll down by 360 pixels each time

new_count = 0
old_count = 0

while True:
    old_count = new_count
    xpath = f'//*[@id="__next"]/div[2]/div[2]/div/div[2]/div/div/div[3]/div/div[2]/div[{n}]/div/div/a'
    new_count = len(set_of_links)
    # Find elements based on the current XPath
    link_elements = driver.find_elements(By.XPATH, xpath)

    if link_elements:  # If elements are found
        prev_link_elements = link_elements
        links = [link.get_attribute("href") for link in link_elements]
        print(links)
        for link in links:
            set_of_links.add(link)
        n += 1  # Move to the next value of n
    else:  # No more elements found for the current n
        driver.execute_script("arguments[0].scrollIntoView();", prev_link_elements[len(prev_link_elements)-1])
        n = 1
        sleep(randint(3, 5))
        
        if old_count == new_count:  # If the scroll position remains the same, it reached the bottom
            #make sure that the last links are loaded - otherwise they could sometimes fail to
            links = [link.get_attribute("href") for link in link_elements]
            print(links)
            for link in links:
                set_of_links.add(link)
            print("Reached the end of the page.")
            break  # Break the loop

# for link in links:
#     set_of_links.add(link.get_attribute('text'))

driver.quit()

print(set_of_links)
print(len(set_of_links))