import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoAlertPresentException

#http://midterm-app-loadbalancer-771272835.ap-southeast-2.elb.amazonaws.com/

TARGET_URL = "http://localhost:3000"

options = webdriver.ChromeOptions()
# options.add_argument('--headless') # Uncomment to run without UI
driver = webdriver.Chrome(options=options)

def accept_alert_if_present():
    try:
        driver.switch_to.alert.accept()
        print("  (accepted a confirm dialog)")
    except NoAlertPresentException:
        pass

try:
    print(f"Navigating to {TARGET_URL}...")
    driver.get(TARGET_URL)
    wait = WebDriverWait(driver, 10)

    # Unique name so leftovers from earlier runs can't interfere
    task_name = f"ALB Test {int(time.time())}"
    task_xpath = f"//li[.//span[text()='{task_name}']]"

    print("Testing task creation with new fields...")
    # 1. Enter Title
    input_field = wait.until(EC.presence_of_element_located((By.ID, "taskInput")))
    input_field.send_keys(task_name)
    
    # 2. Select Category
    category_select = Select(driver.find_element(By.ID, "taskCategory"))
    category_select.select_by_value("University")
    
    # 3. Select Priority
    priority_select = Select(driver.find_element(By.ID, "taskPriority"))
    priority_select.select_by_value("High")
    
    # 4. Enter Date (Using JS to avoid locale formatting issues)
    date_input = driver.find_element(By.ID, "taskDate")
    driver.execute_script("arguments[0].value = '2026-10-28';", date_input)

    # Submit
    driver.find_element(By.XPATH, "//button[text()='Add Task']").click()
    wait.until(EC.presence_of_element_located((By.XPATH, task_xpath)))
    print("Task successfully created and rendered with badges.")

    print("Testing task completion toggle...")
    checkbox = wait.until(
        EC.element_to_be_clickable((By.XPATH, f"{task_xpath}//input[@type='checkbox']"))
    )
    checkbox.click()
    time.sleep(1)

    print("Testing task deletion...")
    # Re-find after the toggle, since the list may have re-rendered
    delete_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, f"{task_xpath}//button[contains(@class, 'delete-btn')]")
        )
    )
    delete_btn.click()
    accept_alert_if_present()

    try:
        wait.until(lambda d: len(d.find_elements(By.XPATH, task_xpath)) == 0)
        print("Task successfully deleted. All UI tests passed!")
    except TimeoutException:
        matches = len(driver.find_elements(By.XPATH, task_xpath))
        print(f"Deletion failed: {matches} matching task(s) still on the page.")
        driver.save_screenshot("delete_failure.png")
        with open("delete_failure.html", "w") as f:
            f.write(driver.page_source)
        print("Saved delete_failure.png and delete_failure.html for inspection.")
        raise

finally:
    time.sleep(2)
    driver.quit()