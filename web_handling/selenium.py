from cgitb import text
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import requests
import time

desired_capabilities = DesiredCapabilities.CHROME
desired_capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
timeout = 10

driver = webdriver.Chrome(desired_capabilities=desired_capabilities)
def exit():
    print( "Timed out waiting for page to load")
    driver.quit()

def setup():
    driver.get('https://leetcode.com/accounts/login/?next=/profile/account/')
    try:
        element_present = EC.presence_of_element_located((By.ID, 'signin_btn'))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        exit()

    driver.find_element(By.ID, "id_login").send_keys("cppcsaccount")
    driver.find_element(By.ID, "id_password").send_keys("billybronc0")

    try:
        element_not_present = EC.invisibility_of_element((By.ID, 'initial-loading'))
        WebDriverWait(driver, timeout).until(element_not_present)
    except TimeoutException:
        exit()

    driver.find_element(By.ID, "signin_btn").click()

    try:
        element_present = EC.presence_of_element_located((By.ID, 'profile-app'))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        exit()

    driver.get("https://leetcode.com/problems/two-sum/")

    try:
        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'CodeMirror-lines'))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        exit()

    driver.find_element(By.CLASS_NAME, "select__3t8J").click()
    driver.find_element(By.XPATH, "//li[contains(text(), 'Python3')]").click()
    driver.execute_script("document.getElementsByClassName(\"btns__1OeZ\")[0].innerHTML += '<textarea id=\"clipboard\" rows=\"4\" cols=\"50\">shit</textarea>'")
    
def typeCode(code):
    clipboard = driver.find_element(By.ID, 'clipboard')
    clipboard.click()
    actions = ActionChains(driver)
    actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
    actions.send_keys(code).perform()
    actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
    actions.key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()
    code_editor = driver.find_element(By.CLASS_NAME, 'CodeMirror-lines')
    code_editor.click()
    actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
    actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
    
def submitAttachmentToLeetcode(attachment):
    url = str(attachment)
    code = requests.get(url).text
    return submitCode(code)

def submitCode(code):
    print("attempting submission")
    typeCode(code)
    driver.find_element(By.XPATH, '//button[@data-cy="submit-code-btn"]').click()
    try:
        element_present = EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Pending')]"))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        exit()
    time.sleep(3)
    try:
        element_present = EC.presence_of_element_located((By.XPATH, "//a[starts-with(@href, '/submissions/detail')]"))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        exit()
    result_url = driver.find_element(By.XPATH, "//a[starts-with(@href, '/submissions/detail')]").get_property("href")
    print(result_url)
    driver.execute_script("window.open()")
    driver.switch_to.window(driver.window_handles[1])
    driver.get(result_url)

    # wait until done loading
    try:
        element_present = EC.presence_of_element_located((By.CLASS_NAME, "testcase-table-re"))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        exit()
    
    result_state = driver.find_element(By.ID, "result_state").get_attribute("innerText")
    print(result_state)
    result_progress = driver.find_element(By.ID, "result_progress").get_attribute("innerText")
    print(result_progress)
    
    driver.execute_script("window.close()")
    driver.switch_to.window(driver.window_handles[0])

    return {
        "result_state": result_state,
        "result_progress": result_progress
    }
