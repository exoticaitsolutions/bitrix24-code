import os
import shutil
import time
from logging_setup import setup_logging
from webdriver_configration import driver_confrigration
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv
from selenium.webdriver.chrome.options import Options
from urls import *

# Load environment variables from the .env file
load_dotenv()

# Access the google_credentials path from the .env file
EMAIL = os.getenv('BITRIX24_EMAIL')
PASSWORD = os.getenv('BITRIX24_PASSWORD')
SEARCHES_NAME = os.getenv('SEARCHES_NAMES')
SEARCHES_INPUTS = os.getenv('SEARCHES_INPUTS')
CSV_FOLDER = os.getenv('CSV_FOLDER')

SEARCHES_NAME_LIST = [name.strip() for name in SEARCHES_NAME.split(',')]


logger = setup_logging()


# Set up Chrome options
downloads_folder = os.path.expanduser("~/Downloads")
# Get the current working directory
current_directory = os.getcwd()

# Create the full path for the folder
csv_folder_path = os.path.join(current_directory, CSV_FOLDER)

# Create the folder if it doesn't exist
if not os.path.exists(csv_folder_path):
    os.makedirs(csv_folder_path)

csv_names = []

def login():
    driver = driver_confrigration()
    driver.get(login_url)
    time.sleep(15)

    input_email_field = driver.find_element(By.ID, "login")
    input_email_field.send_keys(EMAIL)
    time.sleep(5)
    next_button = driver.find_element(By.XPATH, "//button[@data-action='submit']")
    next_button.click()
    time.sleep(5)
    input_password_field = driver.find_element(By.ID, "password")
    input_password_field.send_keys(PASSWORD)
    next_button = driver.find_element(By.XPATH, "//button[@data-action='submit']")
    next_button.click()
    time.sleep(10)
    login_button = driver.find_element(By.CSS_SELECTOR, ".portal-auth-bitrix24__button.portal-auth-bitrix24__button_type_2")
    login_button.click()
    time.sleep(10)
    enter_button = driver.find_element(By.CSS_SELECTOR, ".bx-ui-button.bx-ui-button_primary")
    enter_button.click()
    time.sleep(10)
    my_account_button = driver.find_element(By.XPATH, "//div[contains(@class, 'portal-auth-bitrix24__button portal-auth-bitrix24__button_type_2')]")

    # Click the button
    my_account_button.click()
    time.sleep(10)
    logger.info("sucesfully click on my account buton")
    return driver

def scrapping():
    driver = login()
    dashboard_button = driver.find_element(By.XPATH, "//*[contains(@class, 'portal-auth-bitrix24-popup__list')]")
    dashboard_button.click()
    time.sleep(20)
    logger.info("sucesfully click on dashboard button")

    cut = driver.find_element(By.XPATH, '/html/body/div[3]/div/div[1]/div/div[1]/div[1]/div/div[1]/div[1]')
    cut.click()
    time.sleep(20)

    bi_builder = driver.find_element(By.XPATH, '//*[@id="bx_left_menu_menu_bi_constructor"]/a/span[2]')
    bi_builder.click()
    time.sleep(20)
    
    if SEARCHES_INPUTS:
        logger.info(f"Starting search for: {SEARCHES_INPUTS}")
        search = driver.find_element(By.CLASS_NAME, 'main-ui-filter-search-filter')
        search.clear() 
        search.send_keys(SEARCHES_INPUTS)
        time.sleep(10)
        search.send_keys(Keys.ENTER)
        time.sleep(5)
        first_result = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.dashboard-title-wrapper__item.dashboard-title-preview a'))
        )
        first_result.click()
        time.sleep(15) 

    try:
        # Wait for the iframe to load
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe.side-panel-iframe"))
        )
        driver.switch_to.frame(iframe)
        
        # Locate and click the Edit button
        edit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "edit-btn"))
        )
        edit_button.click()
        time.sleep(20)
        driver.switch_to.default_content()
        # Close the current tab
        driver.close()

        # Switch to another tab (the first tab in this case)
        driver.switch_to.window(driver.window_handles[0])
        driver.get(chart_url)
        time.sleep(10)
        search_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='slice_name']"))
        )
        search_button.click()
        # searches_name = ('My Chart - Bids per Bidder', 'My Chart - Job Category wise for Deals each stage')

        back_url = driver.current_url
        for name in SEARCHES_NAME_LIST:
            logger.info(f"Starting search for: {name}")
            search_button.clear()  
            search_button.send_keys(name.strip())  
            search_button.send_keys(Keys.ENTER)  
            time.sleep(10)

            # Locate and click the link in the results
            try:
                try:
                    link_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//*[@id="app"]/div[2]/div[1]/div[2]/table/tbody/tr/td[2]/span/span/div/a')
                        )
                    )
                    link_element.click()
                    time.sleep(20)  # Wait to ensure the page loads after the click
                except:
                    logger.info("Searching name not found")
                    continue
                button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//button[@aria-label="Menu actions trigger"]')))
                button.click()
                time.sleep(2)
                download_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@class="ant-dropdown-menu-submenu-title" and @title="Download"]'))
                )
                download_button.click()

                time.sleep(2)
                export_to_csv = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//li[contains(@class, 'ant-dropdown-menu-item') and span[text()='Export to .CSV']]"))
                )
                export_to_csv.click()
                time.sleep(60)
                files = os.listdir(downloads_folder)
                latest_file = max([f for f in files if f.endswith('.csv')], key=lambda f: os.path.getmtime(os.path.join(downloads_folder, f)))
                latest_file_path = os.path.join(downloads_folder, latest_file)
                current_directory = os.getcwd()
                csv_name = f"{name}.csv"
                # destination = os.path.join(current_directory, csv_name)
                destination = os.path.join(csv_folder_path, csv_name)
                shutil.move(latest_file_path, destination)
                logger.info(f"File downloaded and renamed to {csv_name} successfully.")
                # csv_names.append(csv_name)
                csv_names.append(destination)
                logger.info(f"sending Csv Names : {csv_names}")
                time.sleep(5)
                    
                driver.get(back_url)
                time.sleep(10)  # Wait to ensure the page loads after the click
                search_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name='slice_name']"))
                )
                search_button.click()
                
            except Exception as e:
                logger.info(f"Error locating or clicking the link for '{name}': {e}")
                continue
        return csv_names

    except Exception as e:
        logger.info(f"Error: {e}")



# scrapping()