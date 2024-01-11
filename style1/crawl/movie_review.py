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
from utils import *
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
    pre_eles=len(_getMovieReview(driverWithWebsiteLoaded))
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
            cur_eles=len(_getMovieReview(driverWithWebsiteLoaded))
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
def getLinks(prequeue:Queue,inqueue:Queue):
    count=10
    driver=Firefox()
    while(count>0):
        m:str=prequeue.get(timeout=10)
        # inqueue.put(f"https://www.rottentomatoes.com/m/{m}/reviews")
        try:
            driver.get(f"https://www.rottentomatoes.com/search?search={m}")
            driver.implicitly_wait(1)
            ele=tryGetElements(driver,"//a[contains(@href,'https://www.rottentomatoes.com/m/') and contains(@class,'unset') and contains(@slot,'title')]","")[""]
            if ele:
                print("search",m,"=>",len(ele))
                for el in ele:
                    try:
                        attri=el.get_attribute("href")+"/reviews"
                        if attri:
                            inqueue.put(attri)
                    except:
                        continue
            else:
                print(f"search {m} empty",count)
                raise Empty
            count=10
        except Empty:
            time.sleep(random.randint(1,2))
            count-=1
        except Exception as e:
            print(e)
class MovieReviewScraper():
    def __init__(self,preworker_num:int,worker_num:int,titles:List[str],path:str="review_list") -> None:
        self.outFile=open(path,"a")
        self.outqueue=Queue(maxsize=60)
        self.inqueue=Queue(maxsize=120)
        self.prequeue=Queue()
        for title in titles:
            self.prequeue.put(title)
        self.preproducers:List[Process]=[]
        for _ in range(preworker_num):
            self.preproducers.append(Process(target=getLinks,args=(self.prequeue,self.inqueue)))
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
                file.flush()
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
if __name__=="__main__":
    # main()
    movieName=MovieReviewScraper(3,5,titleGen(),"review_list")
    for worker in movieName.preproducers:
        worker.join()
        print("A producer has exited")
    for worker in movieName.producers:
        worker.join()
        print("A producer has exited")
    movieName.writer.join()
    print("A writer has exited")
