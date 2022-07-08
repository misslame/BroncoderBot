from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import requests
from config.config import LEETCODE_PASSWORD, LEETCODE_USERNAME
from submission_handling.browser_state import *
from problem_fetching.problem_fetch import getQuestionByTitleSlug
import asyncio
import copy
import os

# TODO: Add captcha support to some extent

timeout = 60

my_browser_state = BrowserState()
options = webdriver.ChromeOptions()
"""
desired_capabilities = DesiredCapabilities.CHROME
options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(desired_capabilities=desired_capabilities, options=options)
"""

options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
options.add_argument("--headless")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(
    service=Service(executable_path=os.environ.get("CHROMEDRIVER_PATH")), options=options
)


response_dict_base = {"msg": None, "err": False, "details": {}}


def exit():
    print("Timed out waiting for page to load")
    my_browser_state.state = BROKEN
    driver.quit()


async def setup(question):
    my_browser_state.state = SETTING_UP
    driver.get("https://leetcode.com/accounts/login/?next=/profile/account/")
    try:
        element_present = EC.presence_of_element_located((By.ID, "signin_btn"))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        exit()

    driver.find_element(By.ID, "id_login").send_keys(LEETCODE_USERNAME)
    driver.find_element(By.ID, "id_password").send_keys(LEETCODE_PASSWORD)

    try:
        element_not_present = EC.invisibility_of_element((By.ID, "initial-loading"))
        WebDriverWait(driver, timeout).until(element_not_present)
    except TimeoutException:
        exit()

    driver.find_element(By.ID, "signin_btn").click()

    driver.get("https://leetcode.com/problems/{}".format(question["titleSlug"]))

    try:
        element_present = EC.invisibility_of_element((By.ID, "initial-loading"))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        exit()

    try:
        element_present = EC.presence_of_element_located(
            (By.XPATH, '//*[contains(text(), "Got it!")]')
        )
        WebDriverWait(driver, 5).until(element_present)
        driver.find_element(By.XPATH, '//*[contains(text(), "Got it!")]').click()
    except TimeoutException:
        pass

    driver.find_element(By.XPATH, "//*[@data-cy='lang-select']").click()
    driver.find_element(By.XPATH, "//li[contains(text(), 'Python3')]").click()
    tab_fix = """onkeydown=\"if(event.keyCode===9){var v=this.value,s=this.selectionStart,e=this.selectionEnd;this.value=v.substring(0, s)+'\t'+v.substring(e);this.selectionStart=this.selectionEnd=s+1;return false;}\""""
    driver.execute_script(
        f'document.getElementsByClassName("btns__1OeZ")[0].innerHTML += `<textarea id="clipboard" {tab_fix} rows="4" cols="50">shit</textarea>`'
    )
    my_browser_state.state = READY


async def changeProblem(title_slug):
    my_browser_state.state = SETTING_UP

    problem = await getQuestionByTitleSlug(title_slug)
    # make sure the problem exists

    driver.get("https://leetcode.com/problems/{}".format(title_slug))

    try:
        element_present = EC.invisibility_of_element((By.ID, "initial-loading"))
        WebDriverWait(driver, 5).until(element_present)
    except TimeoutException:
        exit()

    try:
        element_present = EC.presence_of_element_located(
            (By.XPATH, '//*[contains(text(), "Got it!")]')
        )
        WebDriverWait(driver, 10).until(element_present)
        driver.find_element(By.XPATH, '//*[contains(text(), "Got it!")]').click()
    except TimeoutException:
        pass

    driver.find_element(By.XPATH, "//*[@data-cy='lang-select']").click()
    driver.find_element(By.XPATH, "//li[contains(text(), 'Python3')]").click()
    tab_fix = """onkeydown=\"if(event.keyCode===9){var v=this.value,s=this.selectionStart,e=this.selectionEnd;this.value=v.substring(0, s)+'\t'+v.substring(e);this.selectionStart=this.selectionEnd=s+1;return false;}\""""
    driver.execute_script(
        f'document.getElementsByClassName("btns__1OeZ")[0].innerHTML += `<textarea id="clipboard" {tab_fix} rows="4" cols="50">shit</textarea>`'
    )
    my_browser_state.state = READY


async def typeCode(code):
    clipboard = driver.find_element(By.ID, "clipboard")
    clipboard.click()
    actions = ActionChains(driver)
    actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
    actions.send_keys(code).perform()
    actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
    actions.key_down(Keys.CONTROL).send_keys("c").key_up(Keys.CONTROL).perform()
    code_editor = driver.find_element(By.CLASS_NAME, "CodeMirror-lines")
    code_editor.click()
    actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
    actions.key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()


async def submitAttachmentToLeetcode(attachment, language):
    if my_browser_state.state == BUSY:
        return {
            "msg": "Broncoder is currently busy. Eventually we'll add a queue system, but try again later",
            "err": True,
        }
    if my_browser_state.state == SETTING_UP:
        return {
            "msg": "Broncoder is currently setting up. Please try again in a couple of seconds",
            "err": True,
        }
    url = str(attachment)
    code = requests.get(url).text
    return await submitCode(code, language)


async def submitCode(code, language="Python3"):
    response_dict = copy.deepcopy(response_dict_base)
    my_browser_state.state = BUSY
    # print("attempting submission")

    # driver.find_element(By.XPATH, "//*[@data-cy='lang-select']").click()
    # lang_button = driver.find_element(By.XPATH, f"//li[contains(text(), '{language}')]")
    driver.execute_script(
        f"document.querySelector('[data-cy=\"lang-select-{language}\"]').click()"
    )

    await typeCode(code)

    # driver.find_element(By.XPATH, '//button[@data-cy="submit-code-btn"]').click()
    driver.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div[1]/div/div[3]/div/div[3]/div[2]/div/button/span').click()
    # Attempt at finding an alternate path to click the button by clicking the inner span within the button
    
    '''
    BUG: Error seems to be around this region. My assumption is that the submit button is somehow not being clicked.
    Commenting out the code segment below containing 'status_present' will throw a TimeoutException-related error saying that a timeout occurred in trying to find the element of 'detail_present'
    Commenting out both code segments of 'status_present' and 'detail_present' will causes 'result_url' to throw an error of being unable to find the element in question.
    '''
    try:
        status_present = EC.presence_of_element_located((By.CLASS_NAME, "status__1eAa"))

        WebDriverWait(driver, timeout).until(status_present)
    except TimeoutException:
        exit()

    # await asyncio.sleep(5)

    # print("done waiting")

    try:
        detail_present = EC.presence_of_element_located((By.CLASS_NAME, "detail__1Ye5"))
        WebDriverWait(driver, timeout).until(detail_present)
    except TimeoutException:
        exit()

    result_url = driver.find_element(By.CLASS_NAME, "detail__1Ye5").get_property("href")

    # print(result_url)
    driver.execute_script("window.open()")
    driver.switch_to.window(driver.window_handles[1])
    driver.get(result_url)

    # wait until done loading
    try:
        element_present = EC.presence_of_element_located(
            (By.CLASS_NAME, "testcase-table-re")
        )
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        exit()

    response_dict["details"]["result_state"] = driver.find_element(
        By.ID, "result_state"
    ).get_attribute("innerText")

    # print(response_dict["details"]["result_state"])

    if response_dict["details"]["result_state"] == "Accepted":
        response_dict["details"]["result_memory"] = driver.find_element(
            By.ID, "result_memory"
        ).get_attribute("innerText")
        response_dict["details"]["result_runtime"] = driver.find_element(
            By.ID, "result_runtime"
        ).get_attribute("innerText")

    if response_dict["details"]["result_state"] in [
        "Accepted",
        "Wrong Answer",
        "Runtime Error",
        "Time Limit Exceeded",
    ]:
        response_dict["details"]["result_progress"] = driver.find_element(
            By.ID, "result_progress"
        ).get_attribute("innerText")
        # print(response_dict["details"]["result_progress"])

        result_progress_split = response_dict["details"]["result_progress"].split(" / ")

        if len(result_progress_split) == 2:
            num = int(result_progress_split[0])
            den = int(result_progress_split[1])
            response_dict["details"]["result_progress_percent"] = num / den

    driver.execute_script("window.close()")
    driver.switch_to.window(driver.window_handles[0])
    my_browser_state.state = READY

    response_dict["msg"] = "Submission to leetcode.com completed"
    response_dict["err"] = False
    return response_dict
