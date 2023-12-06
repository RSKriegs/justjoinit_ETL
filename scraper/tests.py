from scraper import Offer, process_offer, load_config
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from time import sleep
from random import randint
import pytest 

@pytest.fixture(scope='module')
def config():
    config = load_config('scraper/config.json')
    return config

@pytest.fixture(scope='module')
def main_url(config):
    main_url = config["main_link"]
    return main_url

@pytest.fixture(scope='module')
def edgedriver_path(config):
    edgedriver_path = config["driver_path"]
    return edgedriver_path

@pytest.mark.dependency()
def test_ping_url(edgedriver_path, main_url):
    service = Service(edgedriver_path)
    driver = webdriver.Edge(service=service)
    driver.get(main_url)
    sleep(randint(3, 5))
    xpath = '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div/div/div[3]/div/div[2]/div[1]/div/div/a'
    link_elements = driver.find_elements(By.XPATH, xpath)
    assert link_elements is not None
    global link
    link = link_elements[0].get_attribute("href")
    driver.quit()
    assert link.startswith('https://justjoin.it/')

@pytest.mark.dependency(depends=['test_ping_url'])
def test_scrap_url(edgedriver_path):    
    service = Service(edgedriver_path)
    driver = webdriver.Edge(service=service)
    driver.get(link)
    sleep(randint(3, 5))
    offer = process_offer(link, driver)
    assert isinstance(offer.name, str) #to be further extended
    driver.quit()