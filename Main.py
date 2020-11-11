from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import requests
import json
import time
from datetime import datetime
import random

#configuring selenium
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
PATH = "C:\Program Files (x86)\chromedriver.exe"

#array of bools to track what sizes are instock
lastKnownStock = []

#function to check stock of item
def checkStock(url):
    driver = webdriver.Chrome(PATH, options=options)
    driver.get(url)
    elements = driver.find_elements_by_name("skuAndSize")
    sizes = driver.find_elements_by_class_name("css-xf3ahq")
    name = driver.find_element_by_id("pdp_product_title")
    sizeList = []
    newStock = ["**" + name.get_attribute("innerHTML") + "**"]
    
    for i in sizes:
        sizeList.append(i.get_attribute("innerHTML"))
        lastKnownStock.append(False)

    if driver.current_url == url:
        counter = 0
        restockCount = 0
        for i in elements:
            try:
                if elements[counter].is_enabled():
                    if lastKnownStock[counter] != True:
                        lastKnownStock[counter] = True
                        newStock.append(sizeList[counter])
                        restockCount += 1
                else:
                    if lastKnownStock[counter] == True:
                        lastKnownStock[counter] = False
            except:
                pass
            counter += 1 
        driver.quit()
        if restockCount > 0:
            print(restockCount, "new restock(s) detected - check Discord")
    return newStock  


#function to send embed to discord webhook
def sendWebhook(urlInp, titleInp, descriptionInp):
    url =  urlInp
    data = {}
    data["content"] = ""
    data["username"] = "Restock Monitor"
    data["embeds"] = []
    embed = {}
    embed["description"] = descriptionInp
    embed["title"] = titleInp
    data["embeds"].append(embed)

    result = requests.post(url, data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)

#infinite loop - checks for restocks every 2-3 hours
print("""    _   ___ __           ____            __             __      __  ___            _ __            
   / | / (_) /_____     / __ \___  _____/ /_____  _____/ /__   /  |/  /___  ____  (_) /_____  _____
  /  |/ / / //_/ _ \   / /_/ / _ \/ ___/ __/ __ \/ ___/ //_/  / /|_/ / __ \/ __ \/ / __/ __ \/ ___/
 / /|  / / ,< /  __/  / _, _/  __(__  ) /_/ /_/ / /__/ ,<    / /  / / /_/ / / / / / /_/ /_/ / /    
/_/ |_/_/_/|_|\___/  /_/ |_|\___/____/\__/\____/\___/_/|_|  /_/  /_/\____/_/ /_/_/\__/\____/_/ """)

url = input("\n\nPlease input the url to check: ")
webhook = input("Please input webhook for restock alerts: ")
runForever = True
while runForever == True:
    detectedStock = checkStock(url)
    if len(detectedStock) > 1:
        embedDescription = ""
        for i in detectedStock:
            embedDescription = embedDescription +"\n" + i
        sendWebhook(webhook, "Restock Detected", embedDescription)
    print("Last checked at", datetime.now())
    wait = random.randint(7200, 10800)
    time.sleep(wait)

