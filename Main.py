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
lastKnownStock = [False, False, False, False, False, False, False, False]

#function to check stock of item
def checkStock(url):
    driver = webdriver.Chrome(PATH, chrome_options=options)
    driver.get(url)
    elements = driver.find_elements_by_class_name("visually-hidden")
    sizeList = ["UK 3", "UK 3.5", "UK 4", "UK 4.5", "UK 5", "UK 5.5", "UK 6", "UK 6.5"]
    newStock = []

    if driver.current_url == url:
        if elements[2].is_enabled():
            elementCounter = 3
            sizeCounter = 0
            for i in elements:
                if elementCounter <= 10:
                    if elements[elementCounter].is_enabled():
                        if lastKnownStock[sizeCounter] != True:
                            lastKnownStock[sizeCounter] = True
                            newStock.append(sizeList[sizeCounter])
                    else:
                        if lastKnownStock[sizeCounter] == True:
                            lastKnownStock[sizeCounter] = False
                    elementCounter += 1 
                    sizeCounter += 1
            driver.quit()
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
runForever = True
while runForever == True:
    detectedStock = checkStock("https://www.nike.com/gb/t/air-force-i-06-shoe-vXJB1w/314192-117")
    if len(detectedStock) > 0:
        embedDescription = "New Stock Detected: \n"
        for i in detectedStock:
            embedDescription = embedDescription + "\n" + i
        sendWebhook("https://discordapp.com/api/webhooks/775142172285730826/c0mpZ21UdMQUX2hIz9tClrTMoOiaYB9Ad_Rw1uUILJjoscDlTrJhcM6xOQ0oqn3UAoYl", "Nike Air Force 1 (GS)", embedDescription)
    print("Last checked at", datetime.now())
    wait = random.randint(7200, 10800)
    time.sleep(wait)

    #https://www.nike.com/gb/t/air-force-i-06-shoe-vXJB1w/314192-117