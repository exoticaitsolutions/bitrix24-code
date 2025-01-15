from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver


def driver_confrigration():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")
    # options.add_argument("--headless")
    
    # Use Service for ChromeDriverManager
    service = Service(ChromeDriverManager().install())
    
    # Pass options and service to Chrome WebDriver
    driver = webdriver.Chrome(service=service, options=options)
    return driver















