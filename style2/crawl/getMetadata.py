from io import TextIOWrapper
import os
from queue import Empty 
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
import selenium
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import FirefoxOptions
from typing import List,Dict
from multiprocessing import Queue,Process
from unidecode import unidecode
import time
import re
import json
from utils import tryGetElement, tryGetElementText, tryGetElementTexts, tryGetElements
import random
def genMovieLinkAndValue():
    pattern=re.compile(r"https://www.rottentomatoes.com/m/[^/]+")
    i=0
    with open("review_list","r") as f:
        for _ in range(55289):
            i+=1
            next(f)
        for line in f:
            i+=1
            print(i)
            try:
                movieDict:Dict[str,List]=json.loads(line)
                for k,v in movieDict.items():
                        movieLink=pattern.findall(k)[0]
                        yield  movieLink,v
            except:
                with open("movie_list_enriched_error","a") as ef:
                    ef.write(movieLink)
                    ef.write("\n")
                continue
def _getMovieMetatData(driver:WebDriver,link:str):
    count=3
    while count>0:
        try:
            metabox=tryGetElement(driver,"//section[contains(@id,'movie-info')]","")[""]
            description=tryGetElementText(metabox,".//p[contains(@data-qa,'movie-info-synopsis')]","description")
            metas=tryGetElementTexts(metabox,".//li[contains(@data-qa,'movie-info-item')]","meta")
            if description["description"] is not None and metas["meta"] is not None:
                count=-1
            else:
                raise Exception
        except:
            print(link,count)
            count-=1 
            time.sleep(random.randint(2,4))
            continue
    return {key:val for d in [description,metas] for key,val in d.items()}
def getMovieMetadata(driver:WebDriver,link:str):
    count=2
    while(True):
        try:
            driver.get(link)
            driver.implicitly_wait(1)
            return _getMovieMetatData(driver,link)
        except:
            count-=1
            if(count<=0):
                return None 
def getMovieMetadataWrapper():
    outFile=open("movie_list_enriched","a")
    driver=Firefox()
    for link,_ in genMovieLinkAndValue():
        print(link)
        count=2
        while True:
            try:
                meta=getMovieMetadata(driver,link)
                if(meta):
                    outFile.write(json.dumps({link:meta}))
                    outFile.write("\n")
                    outFile.flush()
                    count=2
                    if random.random()>0.8:
                        try:
                            driver.delete_all_cookies()
                        except:
                            {}
                    break
                else:
                    raise Exception
            except:
                count-=1
                try:
                    driver.close()
                except:
                    {}
                finally:
                    driver=Firefox()
                print("Exception",link,count)
                if count<=0:
                    with open("movie_list_enriched_error","a") as ef:
                        ef.write(link)
                        ef.write("\n")
                    break
                time.sleep(2)
                continue
    driver.close()
if __name__=="__main__":
    try:
        getMovieMetadataWrapper()
    except:
        pass