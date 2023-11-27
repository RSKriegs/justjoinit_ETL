#TODO
#1. make offer a class and create instances - should be a quick fix
#2. fix 'Skills' bracket issue - for some reason it just doesn't detect the proper xPath at all
#3. fix 'Location' bracket issue - doesn't perform as expected for multiple locations
#4. fix salaries - sometimes they do not get scrapped
#5. Cleanup/modularization/maybe some optimizations
#6. Deduplications
#7. merge json files
#8. Any other bug fixes

import json

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from time import sleep
from random import randint

class Offer:

    def __init__(self, link):
        self.link = link
        self.name               = None
        self.company            = None
        self.category           = None
        self.location           = None
        self.employment_types   = None
        self.experience         = None
        self.operating_mode     = None
        self.description        = None
        self.type_of_work       = None
        self.salary_lower       = None
        self.salary_upper       = None
        self.skills             = None

    def __str__(self):
        return f"Offer(link='{self.link}'"

    @staticmethod
    def extract_record(driver, xpath, attribute):
        if attribute == 'text':
            print(driver, xpath)
            element = driver.find_element(By.XPATH, xpath).text
        else:
            element = driver.find_element(By.XPATH, xpath).get_attribute(attribute)
        return element

    @staticmethod
    def extract_array(driver, xpath, attribute):
        WebElements = driver.find_elements(By.XPATH, xpath)
        if WebElements:
            elements = [element.get_attribute(attribute) for element in WebElements]
            return elements
        else:
            return None

    @staticmethod
    def extract_struct(driver, left_xpath, right_xpath1, right_xpath2, attribute):
        temp_list = []
        n = 1
        while True:
            WebElements_1 = Offer.extract_record(driver, f'{left_xpath}[{n}]{right_xpath1}', attribute)
            WebElements_2 = Offer.extract_record(driver, f'{left_xpath}[{n}]{right_xpath2}', attribute)
            if WebElements_1:
                temp_list.append({WebElements_1: WebElements_2})
                n + 1
            else:
                break
        return temp_list

edgedriver_path = r"C:\code\edgedriver\msedgedriver.exe"
# service = Service(edgedriver_path)
# driver = webdriver.Edge(service=service)

# url = "https://justjoin.it/?keyword=data+engineer"
# driver.get(url)
# sleep(randint(3, 5))

# Set to store extracted links
set_of_links = set()
n = 1  # Initial value for n
new_count = 0 # For scrolling
old_count = 0 # For scrolling

# # Web crawler for sublinks - might be improved
# while True:
#     old_count = new_count
#     xpath = f'//*[@id="__next"]/div[2]/div[2]/div/div[2]/div/div/div[3]/div/div[2]/div[{n}]/div/div/a'
#     new_count = len(set_of_links)
#     # Find elements based on the current XPath
#     link_elements = driver.find_elements(By.XPATH, xpath)

#     if link_elements:  # If elements are found
#         prev_link_elements = link_elements
#         links = [link.get_attribute("href") for link in link_elements]
#         print(links)
#         for link in links:
#             set_of_links.add(link)
#         n += 1  # Move to the next value of n
#     else:  # No more elements found for the current n
#         driver.execute_script("arguments[0].scrollIntoView();", prev_link_elements[len(prev_link_elements)-1])
#         n = 1
#         sleep(randint(3, 5))
        
#         if old_count == new_count:  # If the scroll position remains the same, it reached the bottom
#             print("Reached the end of the page.")
#             break  # Break the loop

# driver.quit()

# print(set_of_links)
# print(len(set_of_links))

set_of_links = ['https://justjoin.it/offers/stepwise-multidisciplinary-prompt-engineer','https://justjoin.it/offers/insight-mid-senior-data-engineer-9fbb0bd9-3fdb-40b0-bb11-e82ca0af2946']

list_of_offers = []
for link in set_of_links:
    offer = Offer(link)
    service = Service(edgedriver_path)
    driver = webdriver.Edge(service=service)
    driver.get(link)
    sleep(randint(3, 5))

    offer.name             = offer.extract_record(driver, 
                                    '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/h1',
                                    "innerHTML")
    
    offer.company          = offer.extract_record(driver, 
                                    '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/div[1]',
                                    "text")
    
    offer.category         = offer.extract_record(driver, 
                                    '//*[@id="__next"]/div[2]/div[2]/div/div[1]/div/a[3]',
                                    "innerHTML")
    
    try:
        offer.location         = offer.extract_record(driver, 
                                    '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]/div',
                                    "innerHTML")
    except: #do this if there is an actual array instead of the record
        offer.location        = offer.extract_record(driver, 
                                    '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]/button/div',
                                    "text")

    offer.type_of_work     = offer.extract_array(driver, 
                                    '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[2]/div[1]/div[2]/div[2]',
                                    "innerHTML")
    
    offer.experience       = offer.extract_array(driver, 
                                    '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[2]/div[2]/div[2]/div[2]',
                                    "innerHTML")
    
    offer.operating_mode   = offer.extract_array(driver, 
                                    '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[2]/div[4]/div[2]/div[2]',
                                    "innerHTML")
    
    offer.employment_types = offer.extract_array(driver, 
                                    '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[2]/div[3]/div[2]/div[2]',
                                    "innerHTML")
    offer.salary_lower      = offer.extract_array(driver, 
                                    '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[2]/div[1]/div/div/span[1]/span[1]',
                                    "innerHTML") #partially broken
    offer.salary_upper  = offer.extract_array(driver, 
                                    '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[2]/div[1]/div/div/span[1]/span[2]',
                                    "innerHTML")
    
    # TODO skills - constantly failing for some reason, cannot find neither xpath nor CSS selector even though it's given proper path.
    # offer.skills           = offer.extract_struct(driver,
    #                                 '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[3]/div/ul/div',
    #                                 "/div", "/div", "innerHTML")

    offer.description      = offer.extract_record(driver, 
                                    '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[4]',
                                    "innerHTML")
    
    list_of_offers.append(offer.__dict__)
    # print(offer)
    driver.quit()

with open('offers_test.json', 'w', newline='') as json_file:
    json.dump(list_of_offers, json_file, indent = 4)