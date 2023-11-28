import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import mysql.connector

host = "localhost"
user = "root"
password = ""
database = "webscrape"

def main():

    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

    cursor = connection.cursor()

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        driver.get("https://www.ycombinator.com/companies")

        
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, '_company_lx3q7_339'))
        )

        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(5)

            new_height = driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                break

            last_height = new_height

        company_list = driver.find_elements(By.CLASS_NAME, '_company_lx3q7_339')
        for company in company_list:
            company_name = company.find_element(By.CLASS_NAME, "_coName_lx3q7_454").text
            location = company.find_element(By.CLASS_NAME, "_coLocation_lx3q7_470").text
            description = company.find_element(By.CLASS_NAME, "_coDescription_lx3q7_479").text
            tags = company.find_elements(By.CLASS_NAME, "_pill_lx3q7_33")
            batch_tag = tags[0].text if tags else None
            industry_tag = tags[1].text if len(tags) > 1 else None
            customer_tag = tags[2].text if len(tags) > 2 else None

            sql = """
                INSERT INTO company_data (name, location, description, batch_tag, industry_tag, customer_tag)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (company_name, location, description, batch_tag, industry_tag, customer_tag)
            cursor.execute(sql, values)

            connection.commit()

    finally:
        cursor.close()
        connection.close()
        driver.quit()

if __name__ == "__main__":
    main()
