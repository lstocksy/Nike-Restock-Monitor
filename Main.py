from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import requests
import json
import time

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
PATH = "C:\Program Files (x86)\chromedriver.exe"

lastKnownStock = [False, False, False, False, False, False, False, False]

def checkStock():
    driver = webdriver.Chrome(PATH, chrome_options=options)
    driver.get("https://www.nike.com/gb/t/air-force-i-06-shoe-vXJB1w/314192-117")

    elements = driver.find_elements_by_class_name("visually-hidden")
    
    sizeList = ["UK 3", "UK 3.5", "UK 4", "UK 4.5", "UK 5", "UK 5.5", "UK 6", "UK 6.5"]

    newStock = []

    elementCounter = 3
    sizeCounter = 0
    for i in elements:
        if elementCounter <= 10:
            if elements[elementCounter].is_enabled():
                if lastKnownStock[sizeCounter] != True:
                    lastKnownStock[sizeCounter] = True
                    newStock.append(sizeList[sizeCounter])
            elementCounter += 1 
            sizeCounter += 1
    
    driver.quit()
    return newStock

def sendWebhook(urlInp, titleInp, descriptionInp):
    url =  urlInp

    data = {}
    #for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
    data["content"] = ""
    data["username"] = "Restock Monitor"

    #leave this out if you dont want an embed
    data["embeds"] = []
    embed = {}
    #for all params, see https://discordapp.com/developers/docs/resources/channel#embed-object
    embed["description"] = descriptionInp
    embed["title"] = titleInp
    data["embeds"].append(embed)

    result = requests.post(url, data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)

runForever = True
while runForever == True:
    detectedStock = checkStock()
    embedDescription = "New Stock Detected: \n"
    for i in detectedStock:
        embedDescription = embedDescription + "\n" + i
    sendWebhook("https://discordapp.com/api/webhooks/775043409970069515/0rnaFl5thweEllXdPtk_D1K8EYGAVxWandIHW9SDpl8yoq-1SNpOSNq2D_EmlF3hjM8f", "Nike Air Force 1 (GS)", embedDescription)
    time.sleep(10800)