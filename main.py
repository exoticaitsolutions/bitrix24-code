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
searches_name = os.getenv('SEARCHES_NAMES')
SEARCHES_NAME_LIST = [name.strip() for name in searches_name.split(',')]


logger = setup_logging()


# Set up Chrome options
downloads_folder = os.path.expanduser("~/Downloads")

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
    print("sucesfully click on my account buton")
    logger.info("sucesfully click on my account buton")
    return driver

def scrapping():
    driver = login()
    dashboard_button = driver.find_element(By.XPATH, "//*[contains(@class, 'portal-auth-bitrix24-popup__list')]")
    dashboard_button.click()
    time.sleep(20)
    print("sucesfully click on dashboard button")
    logger.info("sucesfully click on dashboard button")

    cut = driver.find_element(By.XPATH, '/html/body/div[3]/div/div[1]/div/div[1]/div[1]/div/div[1]/div[1]')
    cut.click()
    time.sleep(20)

    bi_builder = driver.find_element(By.XPATH, '//*[@id="bx_left_menu_menu_bi_constructor"]/a/span[2]')
    bi_builder.click()
    time.sleep(20)

    click_deal_analyse = driver.find_element(By.XPATH, '//*[@id="biconnector_superset_dashboard_grid_table"]/tbody/tr[2]/td[2]/div/span/div/div/a')
    click_deal_analyse.click()
    time.sleep(50)

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
        print("Edit button clicked successfully.")
        logger.info("Edit button clicked successfully.")
        driver.switch_to.default_content()
        # Close the current tab
        driver.close()
        print("Current tab closed successfully.")

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
            print("name : ", name)
            search_button.clear()  
            search_button.send_keys(name.strip())  
            search_button.send_keys(Keys.ENTER)  
            time.sleep(10)
            print("---------------")

            # Locate and click the link in the results
            try:
                link_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="app"]/div[2]/div[1]/div[2]/table/tbody/tr/td[2]/span/span/div/a')
                    )
                )
                print("click h0 gya ")
                link_element.click()
                time.sleep(20)  # Wait to ensure the page loads after the click
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
                # Move the file to the current directory
                # Get all files in the Downloads folder
                files = os.listdir(downloads_folder)
                
                # Get the most recently modified file (assuming it is the most recently downloaded)
                latest_file = max([f for f in files if f.endswith('.csv')], key=lambda f: os.path.getmtime(os.path.join(downloads_folder, f)))

                # Full path to the latest file
                latest_file_path = os.path.join(downloads_folder, latest_file)


                # Define the current working directory
                current_directory = os.getcwd()
                # Define the destination path
                # destination = os.path.join(current_directory, latest_file)
                csv_name = f"{name}.csv"
                destination = os.path.join(current_directory, csv_name)
                shutil.move(latest_file_path, destination)
                print(f"File downloaded and renamed to {csv_name} successfully.")
                logger.info(f"File downloaded and renamed to {csv_name} successfully.")
                csv_names.append(csv_name)
                print("csv_name : ", csv_names)
                time.sleep(5)
            

                    
                driver.get(back_url)
                time.sleep(10)  # Wait to ensure the page loads after the click
                search_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name='slice_name']"))
                )
                search_button.click()
                
            except Exception as e:
                print(f"Error locating or clicking the link for '{name}': {e}")
                logger.info(f"Error locating or clicking the link for '{name}': {e}")
                continue
        return csv_names

    except Exception as e:
        print(f"Error: {e}")
        logger.info(f"Error: {e}")



# scrapping()