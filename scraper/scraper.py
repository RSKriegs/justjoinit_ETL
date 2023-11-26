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

def extract_record(driver, xpath, attribute):
    element = driver.find_element(By.XPATH, xpath).get_attribute(attribute)
    return element

def extract_array(driver, xpath, attribute):
    WebElements = driver.find_elements(By.XPATH, xpath)
    if WebElements:
        elements = [element.get_attribute(attribute) for element in WebElements]
        return elements
    else:
        return None

def extract_struct(driver, left_xpath, right_xpath1, right_xpath2, attribute):
    temp_list = []
    n = 1
    while True:
        WebElements_1 = extract_record(driver, f'{left_xpath}[{n}]{right_xpath1}', attribute)
        WebElements_2 = extract_record(driver, f'{left_xpath}[{n}]{right_xpath2}', attribute)
        if WebElements_1:
            temp_list.append({WebElements_1: WebElements_2})
            n + 1
        else:
            break
    return temp_list

offer = {
    "link": "",
    "name": "",
    "company": "",
    "category": "",
    "location": [],
    "salary": {
        "lower": "",
        "upper": "" #PLN - default currency
    },
    "employment_types": [],
    "type_of_work": "",
    "experience": "",
    "operating_mode": "",
    # "skills": [], #skills are not working for some reason, work in progress
    "description":""
}
list_of_offers = []

edgedriver_path = r"C:\code\edgedriver\msedgedriver.exe"
service = Service(edgedriver_path)
driver = webdriver.Edge(service=service)

url = "https://justjoin.it/?keyword=data+engineer"
driver.get(url)
sleep(randint(3, 5))

# Set to store extracted links
set_of_links = set()
n = 1  # Initial value for n
new_count = 0 # For scrolling
old_count = 0 # For scrolling

# Web crawler for sublinks - might be improved
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
            print("Reached the end of the page.")
            break  # Break the loop

driver.quit()

print(set_of_links)
print(len(set_of_links))

for link in set_of_links:
    service = Service(edgedriver_path)
    driver = webdriver.Edge(service=service)
    driver.get(link)
    sleep(randint(3, 5))
    offer["link"]             = link
    offer["name"]             = extract_record(driver, 
                                    '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/h1',
                                    "innerHTML")
    offer["company"]          = driver.find_element(By.XPATH, 
                                    '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/div[1]'
                                    ).text
    offer["category"]         = extract_record(driver, 
                                    '//*[@id="__next"]/div[2]/div[2]/div/div[1]/div/a[3]',
                                    "innerHTML")
    offer["location"]         = extract_array(driver, 
                                    '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]/div',
                                    "innerHTML") #partially broken
    offer["salary"]["lower"]  = extract_array(driver, 
                                    '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[2]/div[1]/div/div/span[1]',
                                    "innerHTML") #partially broken
    offer["salary"]["upper"]  = extract_array(driver, 
                                    '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[2]/div[1]/div/div/span[1]/span[2]',
                                    "innerHTML")
    offer["type_of_work"]     = extract_array(driver, 
                                    '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[2]/div[1]/div[2]/div[2]',
                                    "innerHTML")
    offer["experience"]       = extract_array(driver, 
                                    '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[2]/div[2]/div[2]/div[2]',
                                    "innerHTML")
    offer["employment_types"] = extract_array(driver, 
                                    '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[2]/div[3]/div[2]/div[2]',
                                    "innerHTML")
    offer["operating_mode"]   = extract_array(driver, 
                                    '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[2]/div[4]/div[2]/div[2]',
                                    "innerHTML")
    #TODO skills - constantly failing for some reason, cannot find neither xpath nor CSS selector even though it's given proper path.
    # offer["skills"]           = extract_struct(driver,
    #                                 '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[3]/div/ul/div',
    #                                 "/div/h6", "/div/span", "innerHTML")
    offer["description"]      = extract_record(driver, 
                                    '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[5]',
                                    "innerHTML")
    
    if offer["location"] == None: #do this if there is an actual array instead of the record
        offer["location"]         = driver.find_element(By.XPATH, 
                                    '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]/button/div'
                                    ).text
    list_of_offers.append(str(offer)) #temp fix - look #1
    print(offer)
    driver.quit()
    
print(list_of_offers)

with open('offers_test.json', 'w', newline='') as json_file:
    json.dump(list_of_offers, json_file)