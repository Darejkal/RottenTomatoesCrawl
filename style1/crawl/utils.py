from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from typing import Dict
import time
def tryGetElement(ele:WebElement|WebDriver,xpath:str,label:str)->Dict:
    result=None
    try:
        result=ele.find_element(By.XPATH,xpath)
    except:
        pass
    return {label:result}
def tryGetElements(ele:WebElement|WebDriver,xpath:str,label:str)->Dict:
    result=None
    try:
        result=ele.find_elements(By.XPATH,xpath)
    except:
        pass
    return {label:result}
def tryGetElementText(ele:WebElement|WebDriver,xpath:str,label:str)->Dict:
    result=None
    try:
        result=ele.find_element(By.XPATH,xpath).text
    except:
        pass 
    return {label:result}
def tryGetElementTexts(ele:WebElement|WebDriver,xpath:str,label:str)->Dict:
    result=None
    try:
        r=ele.find_elements(By.XPATH,xpath)
        result=[]
        for item in r:
            try:
                result.append(item.text)
            except:
                pass
    except:
        pass 
    if type(result) is list and  len(result)==0:
        result=None
    return {label:result}
def tryGetElementAttri(ele:WebElement|WebDriver,xpath:str,label:str)->Dict:
    result=None
    try:
        result=ele.find_element(By.XPATH,xpath).get_attribute("state")
    except:
        pass 
    return {label:result}
def scroll_down(driver:WebDriver):
    count=0
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        count+=1
        last_height = new_height
    return count>0
