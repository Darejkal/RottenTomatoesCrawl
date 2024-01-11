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
from typing import List
from multiprocessing import Queue,Process
from unidecode import unidecode
import time
import re
def _getTitleForMulti(link:str,driver:WebDriver,titles:Queue):
    driver.get(link)
    driver.implicitly_wait(1)
    movies=[]
    while not movies:
        movies=driver.find_elements(By.XPATH,"//td/i/a[contains(@href,'/wiki/')]")
    for m in movies:
        try:
            t=m.text
            if t:
                titles.put(t)
        except Exception:
            print(Exception)
def getTitleForMulti(queue:Queue,titles:Queue):
    driver=Firefox()
    try:
        while True:
            
            try:
                link=queue.get(timeout=10)
            except Empty:
                driver.close()
                return
            count=10
            print(link)
            while count>0:
                try:
                    _getTitleForMulti(link,driver,titles)
                    count=-1
                except:
                    count-=1
                    if count<=0:
                        with(open("movie_name_error","a")) as f:
                            f.write(link)
                            f.write("\n")
    except Exception:
        driver.close()
        raise Exception
def getTitleToFile(link:str,driver:WebDriver,titles:set,outFile:TextIOWrapper):
    driver.get(link)
    driver.implicitly_wait(1)
    movies=[]
    while not movies:
        movies=driver.find_elements(By.XPATH,"//td/i/a[contains(@href,'/wiki/')]")
    for m in movies:
        try:
            t=m.text
            if t and t not in titles:
                titles.add(t)
                outFile.write(t)
        except:
            pass
def linkGen():
    for year in range(2000,2023+1):
        for country in ["American","British","Australian","Canadian"]:
            yield (f"https://en.wikipedia.org/wiki/List_of_{country}_films_of_{year}")
def main():
    outFile=open("movie_name","a")
    driver=Firefox()
    titles=set()
    for l in list(linkGen):
        count=10
        while True:
            try:
                getTitleToFile(l,driver,titles,outFile)
                outFile.flush()
                continue
            except:
                count-=1
                if count<0:
                    with(open("movie_name_error","a")) as f:
                        f.write(l)
                        f.write("\n")
                    continue
class MovieNameScraper():
    def __init__(self,worker_num:int,linklist:List[str],path:str="movie_name") -> None:
        self.outFile=open(path,"a")
        self.outqueue=Queue(maxsize=60)
        self.inqueue=Queue()
        for link in linklist:
            self.inqueue.put(link)
        self.producers:List[Process]=[]
        for _ in range(worker_num):
            self.producers.append(Process(target=getTitleForMulti,args=(self.inqueue,self.outqueue)))
            self.producers[-1].start()
        self.writer=Process(target=self._writer,args=(self.outqueue,self.outFile))
        self.writer.start()
    @staticmethod
    def _writer(outqueue:Queue,file:TextIOWrapper):
        count=10
        while(count>0):
            try:
                text:str=outqueue.get()
                text.replace("\n"," ")
                file.write(text)
                file.write("\n")
                count=10
            except Empty:
                time.sleep(5)
                count-=1
            except Exception:
                print(Exception)
    def close(self):
        for p in self.producers:
            p.terminate()
            p.join()
        self.outFile.close()
        self.writer.terminate()
        self.writer.join()
if __name__=="__main__":
    # main()
    movieName=MovieNameScraper(4,list(linkGen()),"movie_name")
    for worker in movieName.producers:
        worker.join()
        print("A producer has exited")
    movieName.writer.join()
    print("A writer has exited")
