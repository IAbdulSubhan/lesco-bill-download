import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
from PIL import Image
from io import BytesIO
import pytesseract
import base64

def current_month(driver):
    try:
        bill_month_xpath = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="page1-div"]/b/p[3]'))
        )
        bill_owner_xpath = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="page1-div"]/b/table[1]/tbody/tr[1]/td'))
        )
        bill_month = bill_month_xpath.text
        bill_owner = bill_owner_xpath.text
        return bill_month, bill_owner
    except TimeoutException:
        print("Timeout while trying to get current month details")
        return None, None
    except Exception as e:
        print(f"Error getting current month: {str(e)}")
        return None, None

def get_fill_captcha(driver):
    """====================Captcha Reading and Filling========================"""
    try:
        # Wait for CAPTCHA element to be present and visible
        captcha_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//*[@id='ContentPane']/table/tbody/tr[3]/td/img"))
        )
        
        # Take new screenshot each time
        captcha_png = captcha_element.screenshot_as_png
        captcha_img = Image.open(BytesIO(captcha_png))
        
        # OCR with some basic cleanup
        captcha_text = pytesseract.image_to_string(captcha_img).strip()
        captcha_text = ''.join(c for c in captcha_text if c.isalnum())  # Remove special chars
        
        if not captcha_text:
            raise ValueError("Empty CAPTCHA text")
            
        print("CAPTCHA Text:", captcha_text)
        
        # Clear and fill the input field
        code_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "code"))
        )
        code_input.clear()
        code_input.send_keys(captcha_text)
        
        # Scroll and click the button
        driver.execute_script("window.scrollBy(0, 100);")
        time.sleep(0.5)    
        
        view_bill_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='View/Print Bill']"))
        )
        driver.execute_script("arguments[0].click();", view_bill_btn)
        
        # Wait for either success or failure
        try:
            # Check if we got an error message (CAPTCHA failed)
            WebDriverWait(driver, 3).until(
                EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Invalid Code') or contains(text(), 'Wrong Code')]"))
            )
            print("CAPTCHA verification failed")
            return False
        except TimeoutException:
            # No error message found, assume success
            return True
            
    except Exception as e:
        print(f"Error processing CAPTCHA: {str(e)}")
        return False


def print_and_save_bill(driver):
    try:
        print("Attempting to print bill and save into directory")
        # Wait for bill page to load
        WebDriverWait(driver, 10).until(
            lambda d: d.current_url.endswith("/Bill.aspx")
        )
        
        # Get bill details
        bill_owner, bill_month = current_month(driver)
        if not bill_month or not bill_owner:
            raise Exception("Could not get bill details")
            
        print(f"Processing bill for {bill_month} month for {bill_owner}")
        
        # Use Chrome DevTools Protocol to print to PDF
        result = driver.execute_cdp_cmd("Page.printToPDF", {
            "landscape": False,
            "printBackground": True
        })
        
        # Save the PDF to file
        filename = f"{bill_owner}_{bill_month}_bill.pdf"
        with open(filename, "wb") as f:
            f.write(base64.b64decode(result['data']))
        print(f"Successfully saved bill as {filename}")
        return True
    except TimeoutException:
        print("Timeout while waiting for bill page to load")
        return False
    except Exception as e:
        print(f"Error saving bill: {str(e)}")
        return False

def download_bill(customer_id):
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_experimental_option("prefs", {
            "credentials_enable_service": False,
            "profile.password_manager_leak_detection": False
        })
        
        driver = webdriver.Chrome(options=chrome_options)
        time.sleep(2)
        
        driver.maximize_window()

        url = "https://www.lesco.gov.pk:36269/Modules/CustomerBillN/CheckBill.asp"
        driver.get(url)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='txtCustID']"))
        )
        
        print(f"Title: {driver.title}")
        print(f"Current URL: {driver.current_url}")
        
        # Scrolling page
        driver.execute_script("window.scrollBy(0, 153);")
        time.sleep(0.5)

        # Enter customer ID
        input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='txtCustID']"))
        )
        input_field.clear()
        input_field.send_keys(str(customer_id))
        time.sleep(1)
        print("Entered Customer ID")
        
        # Click view menu button
        customer_menu_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//tbody//tr//td//p//input[@name='btnViewMenu']"))
        )
        customer_menu_btn.click()
        time.sleep(1)
        
        # Try to fill captcha multiple times until URL ends with /Bill.aspx
        max_attempts = 5
        attempt = 0
        success = False

        while attempt < max_attempts and not driver.current_url.endswith("/Bill.aspx"):
            print(f"Attempt {attempt + 1} of {max_attempts}")
            if get_fill_captcha(driver):
                # Wait to see if we navigated to the bill page
                try:
                    WebDriverWait(driver, 5).until(
                        lambda d: d.current_url.endswith("/Bill.aspx")
                    )
                    success = True
                    break
                except TimeoutException:
                    print("Didn't navigate to bill page after CAPTCHA submission")
            attempt += 1

        if success:
            print("Captcha successful!")
            if not print_and_save_bill(driver):
                print("Failed to save the bill")
        else:
            print("Captcha failed after max attempts. Exiting.")

    except TimeoutException:
        print("Timeout occurred while waiting for page elements")
    except NoSuchElementException:
        print("Could not find required element on the page")
    except WebDriverException as e:
        print(f"WebDriver error occurred: {str(e)}")
    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

# Example usage
# download_bill("YOUR_CUSTOMER_ID")