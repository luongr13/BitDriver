from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementNotVisibleException
import time
import csv
from handleDB import *


# Login into Bits 2.0
#
def login(driver, username, pw):
    """
    :type driver: WebDriver
    :type username: str
    :type pw: str
    """
    id_field = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.NAME, "UserId")))
    id_field.clear()
    id_field.send_keys(username)

    pw_field = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.NAME, "Password")))
    pw_field.clear()
    pw_field.send_keys(pw)

    submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    submit_button.click()


# Navigate to the pull inventory page
#
def navigatePullInventory(driver):
    """
    :type driver: WebDriver
    """
    elem = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.ID, "ancInventory")))
    elem.click()


# Choose an option from Select View
#
# 0 - on hand
# 1 - pending
# 2 - completed
# 3 - all
#
def selectPullOption(driver, choice):
    """
    :type driver: WebDriver
    :type choice: int
    """
    field_flag = driver.find_element(By.ID, 'GridView_DXFREditorcol1_I')
    values = ['on hand', 'pending', 'all']
    select = Select(driver.find_element(By.ID, 'sltfilterItemsview'))
    select.select_by_value(values[choice])

    if choice != 0:
        WebDriverWait(driver, 10).until(EC.staleness_of(field_flag))


# Clear any previous filters and input the new filters
#
def fillFilter(driver, item_description, qb_item, order_num):
    """
    :type driver: WebDriver
    :type item_description: str
    :type qb_item: str
    :type order_num: str
    """
    for i in range(1, 10):
        field = driver.find_element(By.ID, 'GridView_DXFREditorcol' + str(i) + '_I')

        # Make sure the field is empty
        if len(field.get_property("value")) != 0:
            field.clear()
            WebDriverWait(driver, 10).until(EC.staleness_of(field))
            field = driver.find_element(By.ID, 'GridView_DXFREditorcol' + str(i) + '_I')    

        # Enter Item Description
        if (i == 3) and (len(item_description) != 0):
            field.send_keys(item_description)
            WebDriverWait(driver, 10).until(EC.staleness_of(field))

        if (i == 4) and (len(qb_item) != 0):
            field.send_keys(qb_item)
            WebDriverWait(driver, 10).until(EC.staleness_of(field))
            
        # Enter Order Number
        if (i == 9) and (len(order_num) != 0):
            field.send_keys(order_num)
            WebDriverWait(driver, 10).until(EC.staleness_of(field))


# Locate the Cart button and click the element
#
def checkOut(driver):
    """
    :type driver: WebDriver
    """
    tick_box = driver.find_element(By.XPATH, '//*[@id="GridView_DXDataRow0"]/td[1]')
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(tick_box))
    tick_box.click();
    
    cart_btn = driver.find_element(By.ID, 'btnCart')
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(cart_btn))
    cart_btn.click()

    WebDriverWait(driver, 10).until(EC.staleness_of(tick_box))


# Fill in the fields that are needed to
# complete an inventory pull and save changes.
# Update the spreadsheet_db accordingly if the
# pull is successful or not and terminate the script
# if it was not successful.
#
def pullInventory(driver, spreadsheet_db, customer_db, key):
    """
    :type driver: WebDriver
    :type spreadsheet_db: Dictionary[str]
    :type customer_db: Dictionary[str]
    :type key: str
    """
    fields = ('ParentCompany', 'FacilityName', 'txtDate', 'TicketNumber', 'Requestor', 'Approver')
    containers = ('select2-ParentCompany-container', 'select2-FacilityName-container')

    try:
        pull_data = getBitsData(spreadsheet_db[key], customer_db)
        actions = ActionChains(driver)
        
        # First two fields (parent company and facility name) are Select elements
        for i in range(6):
            if (i < 2):
                select = Select(driver.find_element(By.ID, fields[i]))
                select.select_by_visible_text(pull_data[i])
                driver.find_element(By.ID, containers[i]).click()
            else:
                element = driver.find_element(By.ID, fields[i])
                element.clear()
                element.send_keys(pull_data[i])
                element.send_keys(Keys.ENTER)

        # Is the entry related to Onboarding?
        if (pull_data[5].lower() == 'onboarding'):
            onboarding = driver.find_element(By.ID, 'IsRelatedToEstimate')

        # Make qty field visible
        qty_field = driver.find_element(By.XPATH, '//*[@id="GridView_DXDataRow0"]/td[6]')
        actions.double_click(qty_field).perform()

        # Fill qty
        input_field = driver.find_element(By.ID, 'GridView_DXEditor5_I')
        WebDriverWait(driver, 10).until(EC.visibility_of(input_field))
        input_field.send_keys(pull_data[6])

        # Save entry
        save_btn = driver.find_element(By.ID, 'btnSaveNew')
        save_btn.click()
    except:
        writeCSV(spreadsheet_db, 'Leftover.csv')
        logging.error(traceback.format_exc())
        quit()

    try:
        del spreadsheet_db[key]
    except:
        writeCSV(spreadsheet_db, 'Leftover.csv')
        quit()
        
    WebDriverWait(driver, 10).until(EC.staleness_of(save_btn))
    back_btn = driver.find_element(By.ID, 'btnBack')
    back_btn.click()
    WebDriverWait(driver, 10).until(EC.staleness_of(back_btn))


if __name__ == "__main__" :
    USERNAME = ''
    PASSWORD = ''

    customer_db = {}
    spreadsheet_db = {}
    readCustomerInfo(customer_db, 'CustomerInfo.csv')
    readSpreadsheet(spreadsheet_db, 'Spreadsheet.csv')
    
    driver = webdriver.Chrome()
    driver.get("http://bits.cts.ms")
    assert "BITS2.0 - Login" in driver.title
    
    login(driver, USERNAME, PASSWORD)
    navigatePullInventory(driver)          
    selectPullOption(driver, 0)         
    fillFilter(driver,
               '',
               'Desktop:Desktop:AMAZO_01_31609851',
               '114-8944833-1609851')
    
    for key in spreadsheet_db:
        checkOut(driver)
        pullInventory(driver, spreadsheet_db, customer_db, key)

