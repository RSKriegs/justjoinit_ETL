#TODO
#1. Cleanup/modularization/maybe some optimizations/nice-to-haves like Docker
#2. Deduplications - if needed, look -> SCD2
#3. Any other bug fixes

# Set up for MS Edge

import os
import json

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from time import sleep
from random import randint

class Offer:

    def __init__(self, link):
        self.link               = link
        self.name               = None
        self.company            = None
        self.category           = None
        self.location           = None
        self.experience         = None
        self.operating_mode     = None
        self.type_of_work       = None
        self.salaries           = None
        self.skills             = None
        self.description        = None

    def __str__(self):
        return f"Offer(link='{self.link}')"

    @staticmethod
    def extract_record(driver, xpath, attribute = None):
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
    def extract_skills(driver, xpath, attribute, key_tag_name, value_tag_name):
        WebElements = driver.find_element(By.XPATH, xpath)

        KeyTemps = WebElements.find_elements(By.TAG_NAME,key_tag_name)
        ValueTemps = WebElements.find_elements(By.TAG_NAME, value_tag_name)
        elements = {KeyTemps[i].get_attribute(attribute) : ValueTemps[i].get_attribute(attribute) for i in range(0, len(KeyTemps))}
        return elements

def load_config(file):
    f = open(file)
    return json.load(f)

def write_json(file, data, indent):
    if not os.path.isfile(file):
        with open(file, mode='w', newline='') as file:
            json.dump([data], file, indent = indent)
    else:
        with open(file) as infile:
            temp = json.load(infile)

        temp.append(data)
        with open(file, mode='w', newline='') as file:
            json.dump(temp, file, indent = indent)

if __name__ == '__main__':
    config = load_config('scraper/config.json')

    edgedriver_path = config["driver_path"]
    service = Service(edgedriver_path)
    driver = webdriver.Edge(service=service)

    url = config["main_link"]
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

    print(f'''Links to be extracted are as follows:
          
          {set_of_links}''')

    list_of_offers = []
    for link in set_of_links:
        offer = Offer(link)
        print(f'Following offer is processed: {offer.__str__()}')
        service = Service(edgedriver_path)
        driver = webdriver.Edge(service=service)
        driver.get(link)
        sleep(randint(3, 5))

        offer.name              = offer.extract_record(driver, 
                                        '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/h1',
                                        "innerHTML")
        
        offer.company           = offer.extract_record(driver, 
                                        '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/div[1]',
                                        "text")
        
        offer.category          = offer.extract_record(driver, 
                                        '//*[@id="__next"]/div[2]/div[2]/div/div[1]/div/a[3]',
                                        "innerHTML")

        offer.type_of_work      = offer.extract_array(driver, 
                                        '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[2]/div[1]/div[2]/div[2]',
                                        "innerHTML")
        
        offer.experience        = offer.extract_array(driver, 
                                        '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[2]/div[2]/div[2]/div[2]',
                                        "innerHTML")
        
        offer.operating_mode    = offer.extract_array(driver, 
                                        '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[2]/div[4]/div[2]/div[2]',
                                        "innerHTML")
        
        #extracting salaries
        list_of_salaries = []
        employment_types        = offer.extract_record(driver, 
                                        '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[2]/div[3]/div[2]/div[2]',
                                        "innerHTML").split(',')
        
        salaries_lower          = offer.extract_array(driver, 
                                        '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[2]/div[1]/div/div/span[1]/span[1]',
                                        "innerHTML") #partially broken
        
        salaries_upper          = offer.extract_array(driver, 
                                        '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[2]/div[1]/div/div/span[1]/span[2]',
                                        "innerHTML")
        
        for i in range(0, len(employment_types)):
            list_of_salaries.append({"employment_type"  : employment_types[i],
                                    "lower"             : salaries_lower[i] if salaries_lower else None,
                                    "upper"             : salaries_upper[i] if salaries_upper else None
                                    })
        
        offer.salaries = list_of_salaries
        
        #extracting location
        try:
            offer.location          = offer.extract_record(driver, 
                                        '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]/div',
                                        "innerHTML")
        except: #do this if there is an actual array instead of the record
            offer.location          = offer.extract_record(driver, 
                                        '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]/button/div',
                                        "text")

        #extracting skills & description
        #their positioning seems to be related and both may lay in different positions depending on the job offer, hence the logic
        try:
            offer.skills            = offer.extract_skills(driver,
                                            '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[4]/div/ul',
                                            "innerHTML", "h6", "span")
        except:
            pass
            
        if offer.skills:
            offer.description       = offer.extract_record(driver, 
                                            '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[5]',
                                            "innerHTML")
        else:
            try:
                print(f'First scenario for skills extraction for {offer.__str__()} failed - proceeding further')
                offer.skills            = offer.extract_skills(driver,
                                                '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[3]/div/ul',
                                                "innerHTML", "h6", "span")
                
                offer.description       = offer.extract_record(driver, 
                                                '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[4]',
                                                "innerHTML")
            except:
                print(f'Could not find skills for {offer.__str__()} - leaving empty dict, default setting for description')
                
                offer.description       = offer.extract_record(driver, 
                                                '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[2]/div[5]',
                                                "innerHTML")
        
        print(f'''Final offer dict:
              
              {offer.__dict__}''')
        
        write_json(config["offers_file"], offer.__dict__, 4)
        driver.quit()

    print(f'Offers extraction process finished - check {config["offers_file"]} file')