import time
import pandas as pd
from datetime import datetime
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# XPaths provided
NAME_XPATH = "/html/body/form/div[2]/div[1]/div/div/div/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]"
COMPANY_XPATH = "/html/body/form/div[2]/div[1]/div/div/div/div[1]/div[3]/div[1]/div[1]/div[2]/div[2]/span"
WEBSITE_XPATH = "/html/body/form/div[2]/div[1]/div/div/div/div[1]/div[3]/div[1]/div[1]/div[2]/div[2]/p[1]/a"
SHOW_PHONE_XPATH = "/html/body/form/div[2]/div[1]/div/div/div/div[1]/div[1]/div[2]/div[1]/div[2]/div[1]/span[1]/span"
PHONE_XPATH = "/html/body/form/div[2]/div[1]/div/div/div/div[1]/div[1]/div[2]/div[1]/div[2]/div[1]/span[2]/a/span/span"

# helper function to scrape a specific broker page, attained from big directory
def scrape_broker(url):
    # specific broker scrape
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Uncomment next line for headless if not debugging -> this will decrease computer load
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 15)
    data = {"Name": "", "Phone": "", "Company": "", "Website": ""}
    try:
        driver.get(url)
        time.sleep(1)  # buffer
        
        # Extract Name
        try:
            data["Name"] = driver.find_element(By.XPATH, NAME_XPATH).text.strip()
        except Exception as e:
            print(f"Name not found on {url}: {e}")
        
        # click show phone number in order to reveal numbver
        try:
            show_phone_elem = driver.find_element(By.XPATH, SHOW_PHONE_XPATH)
            show_phone_elem.click()
            time.sleep(1)  # buffer
        except Exception as e:
            print(f"Error clicking 'Show Phone Number' on {url}: {e}")
        
        # Extract Phone Number
        try:
            data["Phone"] = driver.find_element(By.XPATH, PHONE_XPATH).text.strip()
        except Exception as e:
            print(f"Phone not found on {url}: {e}")
        
        # Extract Company
        try:
            data["Company"] = driver.find_element(By.XPATH, COMPANY_XPATH).text.strip()
        except Exception as e:
            print(f"Company not found on {url}: {e}")
        
        # Extract Website
        try:
            data["Website"] = driver.find_element(By.XPATH, WEBSITE_XPATH).get_attribute("href")
        except Exception as e:
            print(f"Website not found on {url}: {e}")
        
    except Exception as ex:
        print(f"Error processing broker {url}: {ex}")
    finally:
        driver.quit()
    return data

def scrape_bizbuysell():
    # main chrome for directory nav
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Uncomment next line for headless if not debugging -> this will decrease computer load
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 20)

    directory_url = "https://www.bizbuysell.com/business-brokers/directory/every/"
    print("Loading directory:", directory_url)
    driver.get(directory_url)
    print("Loaded URL:", driver.current_url)
    
    all_broker_data = []
    
    try:
        while True:
            # lazy-loaded content will require a scroll to the bottom to hit next button
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # broker links accessed here
            try:
                broker_elements = wait.until(EC.presence_of_all_elements_located(
                    (By.XPATH, "//a[contains(@href, '/business-broker/')]")
                ))
            except TimeoutException:
                print("No broker links found on this page.")
                break
            
            page_broker_urls = [elem.get_attribute("href") for elem in broker_elements]
            print(f"Found {len(page_broker_urls)} broker profiles on this page.")
            
            # 2 spreads rn for speed
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                results = list(executor.map(scrape_broker, page_broker_urls))
                all_broker_data.extend(results)
            
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            try:
                next_button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(@class, 'bbsPager_next') and contains(text(), 'Next')]")
                ))
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                print("Clicking Next button...")
                next_button.click()
                time.sleep(3)
            except TimeoutException:
                print("No clickable Next button found. Reached the last page.")
                break
            except Exception as e:
                print("Error clicking Next button:", e)
                break
            
    except KeyboardInterrupt:
        print("KeyboardInterrupt detected. Saving scraped data so far...")
    except WebDriverException as e:
        print("WebDriverException encountered:", e)
    finally:
        # Generate a unique filename with a timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_filename = f"brokers_{timestamp}.xlsx"
        if all_broker_data:
            try:
                df = pd.DataFrame(all_broker_data)
                df.to_excel(excel_filename, index=False)
                print(f"Data saved to {excel_filename}")
            except Exception as e:
                print("Error saving data:", e)
        else:
            print("No data scraped.")
        try:
            driver.quit()
        except Exception as e:
            print("Error quitting driver:", e)

if __name__ == "__main__":
    scrape_bizbuysell()
