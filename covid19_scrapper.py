import json
import sys
import requests as req
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
from string import digits
import re
from datetime import datetime



path_do_driver = "./chromedriver"
file_out = "data_corona.json"
url = "http://covid19.sante.gov.dz/carte/"


def getNameWilaya(txt):

    remove_digits = str.maketrans('', '', digits)
    txt = txt.translate(remove_digits)

    new_txt = ""

    start = False

    for i in range(len(txt)-1, 0, -1):
        
        if txt[i] == "-" and new_txt == "":
            start = True
            continue

        if not start:
            continue
        
        new_txt = txt[i] + new_txt

    
    new_txt = new_txt.strip()

    return new_txt



driver = webdriver.ChromeOptions()
driver = webdriver.Chrome(path_do_driver)
driver.get(url)

wait = WebDriverWait(driver, 20)

sleep(10)

try:
    wilayas_elemts = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ember49")))
except:
    print("Error")
    sys.exit()

list_wilayas = driver.find_element_by_id("ember49")

wilayas_elemts = list_wilayas.find_elements_by_class_name("external-html")

wilayas_dict = {}

widgets = driver.find_elements_by_class_name("widget-body")
total_cases = int(re.sub("[^0-9]", "", widgets[0].text))
print("Total cases:", total_cases)

total_hosp = 0
total_deaths = 0
total_healed = 0

for wilaya in wilayas_elemts:
    
    res = getNameWilaya(wilaya.text)

    print("Wilaya: ", res)

    wilaya.find_elements_by_tag_name("span")[0].click()
    
    #sleep(10)

    try:
        here = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "info-panel")))
    except:
        print("Error pannel")
        sys.exit()
    
    sleep(2)
    
    info_panel = driver.find_elements_by_class_name("info-panel")[0]

    widgets = driver.find_elements_by_class_name("widget-body")
    
    cnt = 0

    for w in widgets:
        if "Rétablis" in w.text and "حالات الشفاء" in w.text:
            widget_healed = w
            cnt += 1
        if "Hospitalisés" in w.text and "في المستشفى" in w.text:
            widget_hosp = w
            cnt += 1
        if "Décédés" in w.text and "حالات الوفاة" in w.text:
            widget_deaths = w
            cnt += 1
        
        if cnt == 3:
            break  

    try:
        nb_healed = int(widget_healed.find_elements_by_class_name("indicator-center-text")[0].find_elements_by_tag_name("text")[0].text)
    except:
        nb_healed = 0
            
    try:
        nb_hosp = int(widget_hosp.find_elements_by_class_name("indicator-center-text")[0].find_elements_by_tag_name("text")[0].text)
    except:
        nb_hosp = 0

    try:
        nb_deaths = int(widget_deaths.find_elements_by_class_name("indicator-center-text")[0].find_elements_by_tag_name("text")[0].text)
    except:
        nb_deaths = 0

    total_hosp += nb_hosp
    total_deaths += nb_deaths
    total_healed += nb_healed

    print("Nb healed", nb_healed)
    print("Nb deaths", nb_deaths)
    print("Nb hosp", nb_hosp)
    
    wilayas_dict[res] = {"Hosp": int(nb_hosp),
                "Healed": int(nb_healed),
                "Deaths":int(nb_deaths)
                }


    ### Close info-pannel
    info_panel.find_elements_by_tag_name("div")[0].find_elements_by_class_name("btn")[0].click()
    


wilayas_dict["DateRaw"] = datetime.today()
wilayas_dict["Date"] = datetime.today().strftime("%d/%m/%Y %H:%M")
wilayas_dict["TOTAL"] = {"Total": total_cases, "Hosp": total_hosp, "Deaths": total_deaths, "Healed": total_healed}


with open(file_out, 'w') as fp:
    json.dump(wilayas_dict, fp,  indent=4)