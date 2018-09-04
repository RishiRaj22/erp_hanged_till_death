## Necessary Configuration
user_id = None
password = None

## Optional configuration
html_location = "temp.html"
timeout_seconds = 40
retry_limit = 3

import subprocess

from sys import argv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

driver = None


def run(tries):
    print("Attempt #{}".format(retry_limit - tries))
    if tries == 0:
        return False
    try:
        driver.get(
            "http://115.114.127.54:8080/psc/bitcsprd/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.B_SS_ATTEND_ROSTER.GBL?PortalActualURL=http%3a%2f%2f115.114.127.54%3a8080%2fpsc%2fbitcsprd%2fEMPLOYEE%2fHRMS%2fc%2fSA_LEARNER_SERVICES.B_SS_ATTEND_ROSTER.GBL&PortalRegistryName=EMPLOYEE&PortalServletURI=http%3a%2f%2f115.114.127.54%3a8080%2fpsp%2fbitcsprd%2f&PortalURI=http%3a%2f%2f115.114.127.54%3a8080%2fpsc%2fbitcsprd%2f&PortalHostNode=HRMS&NoCrumbs=yes&PortalKeyStruct=yes")
        uid = driver.find_element_by_id("userid")
        uid.send_keys(user_id)
        pwd = driver.find_element_by_id("pwd")
        pwd.send_keys(password)
        lb = driver.find_element_by_class_name("psloginbutton")
        print("Logging in...")
        lb.click()
        toggle = WebDriverWait(driver, timeout_seconds).until(
            EC.presence_of_element_located((By.ID, "SSR_DUMMY_RECV1$sels$0"))
        )
        print("Fetching attendance...")
        toggle.click()
        attendance_button = driver.find_element_by_id("DERIVED_AA2_B_ATTEND_ROSTER")
        attendance_button.click()
        table = WebDriverWait(driver, timeout_seconds).until(
            EC.presence_of_element_located((By.ID, "CLASS_TBL_VW$scroll$0"))
        )
    except Exception:
        print("Error. Retrying ")
        return run(tries - 1)
    return "<table>" + table.get_attribute('innerHTML') + "</table>"


def printusage():
    print("Set variables in the configuration at the top of the file,",
          "or pass arguments like:",
          "python attendance.py <user-id> <password>",
          sep='\n')


def main():
    global driver
    global html_location
    global user_id
    global password

    if len(argv) > 2:
        user_id = argv[1]
        password = argv[2]
    if len(argv) == 4:
        html_location = argv[3]

    if user_id == None or password == None:
        printusage()
        return

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=options)
    success = run(retry_limit)
    if success == False:
        print("Error updating attendance")
    else:
        try:
            with open(html_location, 'r') as f:
                old = f.read()
        except Exception:
            old = ''

        if old == success:
            print("No changes")

        else:
            f = open(html_location, "w+")
            f.write(success)
            print("Wrote result to {}".format(html_location))
            subprocess.call(["xdg-open", html_location])

    driver.quit()


main()
