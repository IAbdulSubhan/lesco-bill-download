import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from PIL import Image
from io import BytesIO
import pytesseract
import base64

def current_month():

    bill_month_xpath = driver.find_element(By.XPATH, '//*[@id="page1-div"]/b/p[3]')
    bill_month = bill_month_xpath.text
    return bill_month

def get_fill_captcha():
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

def print_and_save_bill():
    # Use Chrome DevTools Protocol to print to PDF
        result = driver.execute_cdp_cmd("Page.printToPDF", {
            "landscape": False,
            "printBackground": True
        })
        
        
        # Save the PDF to file
        with open(f"{customer_id}_{current_month()}_bill", "wb") as f:
            f.write(base64.b64decode(result['data']))

        print(f"Saved Print for bill of {current_month()} month")

def download_bill(customer_id):

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    
    driver = webdriver.Chrome(options=chrome_options)
    print("Opening Chrome")
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
    get_fill_captcha()

    get_bill_url = driver.current_url

    """==============print to PDF only if current url is to print the bill==============="""
    
    if get_bill_url == "https://www.lesco.gov.pk:36260/Bill.aspx":
        print_and_save_bill()
    else:
        print_and_save_bill


    driver.quit()
    

