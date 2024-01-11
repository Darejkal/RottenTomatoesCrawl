from io import TextIOWrapper
import os
from queue import Empty 
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
import selenium
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import FirefoxOptions
from typing import List,Dict,Callable
from multiprocessing import Queue,Process
import time
import re
import json
import random
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
def _testGetMovieReview(driverWithWebsiteLoaded:WebDriver)->List:
    review_rows=tryGetElements(driverWithWebsiteLoaded,"//div[contains(@class,'review-row')]","review_row")["review_row"]
    if review_rows == None or len(review_rows)==0:
        return []
    review_list=[]
    for row in review_rows:
        tempdict={}
        try:
            tempdict.update(tryGetElementText(row,".//a[contains(@class,'display-name')]","critic"))
            review_list.append(tempdict)
        except Exception as e:
            print(e)
            continue
    return review_list
def _getMovieReview(driverWithWebsiteLoaded:WebDriver)->List:
    review_rows=tryGetElements(driverWithWebsiteLoaded,"//div[contains(@class,'review-row')]","review_row")["review_row"]
    if review_rows == None or len(review_rows)==0:
        return []
    review_list=[]
    for row in review_rows:
        tempdict={}
        try:
            tempdict.update(tryGetElementText(row,".//a[contains(@class,'display-name')]","critic"))
            tempdict.update(tryGetElementText(row,".//a[contains(@class,'publication')]","publication"))
            tempdict.update(tryGetElementAttri(row,".//score-icon-critic-deprecated","state"))
            tempdict.update(tryGetElementText(row,".//p[contains(@class,'review-text')]","review"))
            tempdict.update(tryGetElementText(row,".//p[contains(@class,'original-score-and-url')]","additional"))
            review_list.append(tempdict)
        except Exception as e:
            print(e)
            continue
    return review_list
def _loadMovieReview(driverWithWebsiteLoaded:WebDriver):
    pre_eles=len(_testGetMovieReview(driverWithWebsiteLoaded))
    cur_eles=0
    try:
        # driverWithWebsiteLoaded.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        button=tryGetElement(driverWithWebsiteLoaded,"//div[contains(@class,'load-more-container')]","")[""]
        count=3
        while not button and count>0:
            count-=1
            time.sleep(random.randint(2,3))
        if button:
            button.click()
            time.sleep(random.randint(1,3))
            scroll_down(driverWithWebsiteLoaded)
            cur_eles=len(_testGetMovieReview(driverWithWebsiteLoaded))
    except:
        pass 
    finally:
        return cur_eles>pre_eles
def getMovieReview(driver:WebDriver,link:str,label:str)->Dict:
    result=[]
    try:
        driver.get(link)
        driver.implicitly_wait(1)
        scroll_down(driver)
        while(_loadMovieReview(driver)):
            print("press button")
            continue
        count=3
        while(count>0):
            result=_getMovieReview(driver)
            if(len(result)!=0):
                break 
            count-=1
            print("getMovieReview","wait",count)
            time.sleep(random.randint(0,3))
    except Exception as e:
        print(e)
    finally:
        if not result:
            return None
        return {label:result}
def getMovieReviewMultiWrapper(inqueue:Queue,outqueue:Queue):
    try:
        driver=Firefox()
        while True:
            try:
                link=inqueue.get(timeout=50)
            except Empty:
                driver.close()
                return
            print(link)
            count=1
            while count>0:
                try:
                    result=getMovieReview(driver,link,link)
                    if result:
                        outqueue.put(result)
                    else: raise Exception(f"got empty result from getMovie, try {count}")
                    count=-1
                except Exception as e:
                    print(e)
                    count-=1
                    if count<=0:
                        with(open("review_list_error","a")) as f:
                            f.write(link)
                            f.write("\n")
    except Exception as e:
        driver.close()
        raise e
class MovieReviewScraper():
    def __init__(self,preworker_num:int,worker_num:int,getLinks:Callable,titles:str|None=None,path:str="review_list") -> None:
        self.outFile=open(path,"a")
        self.outqueue=Queue(maxsize=60)
        self.inqueue=Queue(maxsize=120)
        if titles:
            self.prequeue=Queue()
            for title in titles:
                self.prequeue.put(title)
            self.preproducers:List[Process]=[]
            self.getLinks=getLinks
            for _ in range(preworker_num):
                self.preproducers.append(Process(target=self.getLinks,args=(self.prequeue,self.inqueue)))
                self.preproducers[-1].start()
        else:
            assert preworker_num==1
            self.prequeue=None
            self.preproducers:List[Process]=[]
            self.getLinks=getLinks
            for _ in range(preworker_num):
                self.preproducers.append(Process(target=self.getLinks,args=(self.prequeue,self.inqueue)))
                self.preproducers[-1].start()
        self.producers:List[Process]=[]
        for _ in range(worker_num):
            self.producers.append(Process(target=getMovieReviewMultiWrapper,args=(self.inqueue,self.outqueue)))
            self.producers[-1].start()
        self.writer=Process(target=self._writer,args=(self.outqueue,self.outFile))
        self.writer.start()
    @staticmethod
    def _writer(outqueue:Queue,file:TextIOWrapper):
        count=10
        while(count>0):
            try:
                out:Dict[List]=outqueue.get()
                print("write",next(iter(out)),len(out[next(iter(out))]))
                file.write(json.dumps(out))
                file.write("\n")
                count=10
            except Empty:
                time.sleep(5)
                count-=1
            except Exception as e:
                print(e)
    def close(self):
        for p in self.producers:
            p.terminate()
            p.join()
        for p in self.preproducers:
            p.terminate()
            p.join()
        self.outFile.close()
        self.writer.terminate()
        self.writer.join()
def titleGen():
    with open("review_list_error_retry","r") as f:
        movieNames=set([line[:-1] for line in f])
    return list(movieNames)