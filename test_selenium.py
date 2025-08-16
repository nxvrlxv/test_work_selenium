from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
from urllib.parse import urlparse, parse_qs, unquote
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd

options = Options()
options.add_argument("--start_maximized") #на весь экран
options.add_argument("--disable-blink-features=AutomationControlled") # Маскировка автоматизации

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Открываем сайт
#driver.get("https://www.partyslate.com/find-vendors/event-planner/area/miami")
main_page = "https://www.partyslate.com/find-vendors/event-planner/area/miami"

company_links = []
for page in range(1, 4):
    url = f"https://www.partyslate.com/find-vendors/event-planner/area/miami?page={page}"
    driver.get(url)
    time.sleep(15)
    cards = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".src-components-CompanyDirectoryCard-styles__container__2JUdC.src-components-CompanyDirectoryCard-styles__with-min-height__3NcZm")))
    print(cards)
    for card in cards:
        tag_a = card.find_element("tag name", "a")
        tag_h3 = card.find_element("tag name", "h3")
        
        company_name = tag_h3.text
        link = tag_a.get_attribute("href")
        company_links.append((company_name, link))

        

#<------part 2-------->
data = []
for name, link in company_links:
    driver.get(link)
    time.sleep(10)
    # company_info = {
    #     "name": name,
    #     "link": link,
    #     "website": "-",
    #     "phone": "-",
    #     "instagram": "-",
    #     "facebook": "-",
    #     "team": [],
    #     "min_spend": "-"
    # }

    try:
        button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".chakra-button.css-15tyt09")))
        ActionChains(driver).move_to_element(button).click().perform()
        overlay = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".chakra-modal__content.css-otp7jf")))
        time.sleep(3)
        website = overlay.find_element(By.CSS_SELECTOR, ".css-123qr35").text
        phone = overlay.find_element(By.CSS_SELECTOR, ".css-1dvr8y4").text

        inst_face = overlay.find_elements(By.CSS_SELECTOR, ".css-6cxgxb")
        instagram = "-"
        facebook = "-"
        for linkk in inst_face:
            href = linkk.get_attribute("href")
            if "instagram.com" in href:
                instagram = href
            if "facebook.com" in href:
                facebook = href

        # print(f"{website}: {phone}")
        
        print(f"Instagram: {instagram}")
        print(f"Facebook: {facebook}")
    except:
        website = '-'
        phone = '-'
    
    try:
        driver.get(link)
        time.sleep(4)
        min_spend = driver.find_element(By.CSS_SELECTOR, ".css-1nmdp34").text
        print(min_spend)
    except:
        min_spend = '-'


    #meet the team
    driver.get(link)
    time.sleep(4)
    team_members = []
    try:
        while True:
            
            member_name = driver.find_element(By.CSS_SELECTOR, ".css-1ham2m0").text
            print(member_name)
            if member_name is None:
                member_name = "-"
            
            member_container = driver.find_element(By.CSS_SELECTOR, ".css-5peb2r")
            members_job_title = member_container.find_element(By.CSS_SELECTOR, ".css-1pxun7d").text.strip()
            print(members_job_title)
            if members_job_title is None:
                members_job_title = "-"
            
           
            team_members.append((member_name, members_job_title))

            
            next_buttons = driver.find_elements(By.CSS_SELECTOR, ".css-1qz0g1e")
            if next_buttons[1] is None:
                break

            if next_buttons[1].get_attribute("disabled"):
                break

            ActionChains(driver).move_to_element(next_buttons[1]).click().perform()
            time.sleep(2)
    except:
        pass


    if team_members:
        for member_name, members_job_title in team_members:
            data.append({
                "Company Name": name,
                "Website": website,
                "Phone": phone,
                "Email": 'contact@partyslate.com',
                "Instagram": instagram,
                "Facebook": facebook,
                "Min Spend": min_spend,
                "Team Member Name": member_name,
                "Team Member Title": members_job_title})
    else:
        data.append({
                "Company Name": name,
                "Website": website,
                "Phone": phone,
                "Email": 'contact@partyslate.com',
                "Instagram": instagram,
                "Facebook": facebook,
                "Min Spend": min_spend,
                "Team Member Name": "-",
                "Team Member Title": "-"})
        
df = pd.DataFrame(data)

df.to_excel("companies_with_team.xlsx", index=False)
print("Данные сохранены в файл companies_with_team.xlsx")