import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from PIL import Image
from io import BytesIO
import pytesseract
import base64

def current_month(driver):

    bill_month_xpath = driver.find_element(By.XPATH, '//*[@id="page1-div"]/b/p[3]')
    bill_owner_xpath = driver.find_element(By.XPATH, '//*[@id="page1-div"]/b/table[1]/tbody/tr[1]/td')
    bill_month = bill_month_xpath.text
    bill_owner = bill_owner_xpath.text
    return bill_month, bill_owner

def get_fill_captcha(driver):
    """====================Captcha Reading and Filling========================"""
    
    # Step 1: Locate the CAPTCHA element
    captcha_element = driver.find_element(By.XPATH, "//*[@id='ContentPane']/table/tbody/tr[3]/td/img")  # Adjust XPath
    
    #Step 2: Take screenshot directly to memory
    captcha_png = captcha_element.screenshot_as_png  # bytes, not file
    
    # Step 3: Convert bytes to PIL image
    captcha_img = Image.open(BytesIO(captcha_png))
    
    # Step 4: OCR
    captcha_text = pytesseract.image_to_string(captcha_img).strip()
    print("CAPTCHA Text:", captcha_text)
    
    # Step 5: Fill the input field
    driver.find_element(By.ID, "code").send_keys(captcha_text)
    time.sleep(1)

        
    view_bill_btn = driver.find_element(By.XPATH, "//button[text()='View/Print Bill']")
    driver.execute_script("arguments[0].scrollIntoView(true);", view_bill_btn)
    driver.execute_script("arguments[0].click();", view_bill_btn)

    time.sleep(2)

def print_and_save_bill(driver):
    print("to print bill and save into directory attempt")
    # Use Chrome DevTools Protocol to print to PDF
    result = driver.execute_cdp_cmd("Page.printToPDF", {
            "landscape": False,
            "printBackground": True
        })
        
        
        # Save the PDF to file
    bill_owner, bill_month = current_month(driver)
    print(bill_month, bill_owner)
    with open(f"{bill_owner}_{bill_month}_bill", "wb") as f:
        print("in opening file")
        f.write(base64.b64decode(result['data']))
    print(f"Saved Print for bill of {bill_month} month")

def download_bill(customer_id):

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    
    driver = webdriver.Chrome(options=chrome_options)
    # print("Opening Chrome")
    time.sleep(5)
    
    driver.maximize_window()

    url = "https://www.lesco.gov.pk:36269/Modules/CustomerBillN/CheckBill.asp"
    driver.get(url)
    
    time.sleep(2)
    print(f"Title: {driver.title}")
    print(f"Current URL: {driver.current_url}")
    
    # locating Customer ID input field
    cust_id_input_field_xpath = "//input[@name='txtCustID']"
    input_field = driver.find_element(by = By.XPATH, value = cust_id_input_field_xpath)
    
    #entering customerID
    input_field.send_keys(str(customer_id))
    time.sleep(1)
    print("Got entered Customer ID")
    
    #scrolling page
    footor_input_field_xpath = "//input[@id='txtUser']"
    footor_input_field = driver.find_element(By.XPATH, footor_input_field_xpath)
    driver.execute_script("arguments[0].scrollIntoView();", footor_input_field)
    time.sleep(2)
    
    #for customer ID
    customer_menu_btn_xpath = "//tbody//tr//td//p//input[@name='btnViewMenu']"
    customer_menu_btn = driver.find_element(by = By.XPATH, value = customer_menu_btn_xpath)
    try:
        customer_menu_btn.click()
    except:
        print("Button not found")
    
    time.sleep(1)
    
    # Fill captcha
    get_fill_captcha(driver)


    """==============print to PDF only if current url is to print the bill==============="""
    
    # Try to fill captcha multiple times until URL ends with /Bill.aspx
    max_attempts = 5
    attempt = 0

    while not driver.current_url.endswith("/Bill.aspx") and attempt < max_attempts:
        print(f"Captcha attempt {attempt + 1} failed. Retrying...")
        get_fill_captcha(driver)
        time.sleep(2)  # Give the page time to navigate
        attempt += 1

    if driver.current_url.endswith("36260/Bill.aspx"):
        print("Captcha successful!")
        print_and_save_bill(driver)
    else:
        print("Captcha failed after max attempts. Exiting.")

        


    driver.quit()
    

