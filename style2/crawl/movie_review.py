from queue import Empty
import requests
import xml.etree.ElementTree as ET
from multiprocessing import Queue
import re
from utils import MovieReviewScraper
def getSitemap():
    URL = "https://www.rottentomatoes.com/sitemaps/sitemap.xml"
    page = requests.get(URL)
    root = ET.fromstring(page.content)
    sitemap=[]
    for url in root.findall(".//*"):
        if "https://www.rottentomatoes.com/sitemaps/movie" in url.text:
            sitemap.append(url.text)
    return sitemap
def genMovieLinksFromSiteMap(sitemap:str):
    print(sitemap)
    page=requests.get(sitemap)
    r = ET.fromstring(page.content)
    pattern=re.compile(r"https://www\.rottentomatoes\.com/m/[^/]+$")
    for url in r.findall(".//*"):
        if pattern.findall(url.text):
            yield (url.text+"/reviews")
def getMovieLinksFromSiteMapWrapper(prequeue:Queue,inqueue:Queue):
    count=10
    while(count>0):
        try:
            sitemap=prequeue.get(timeout=10)
            for link in genMovieLinksFromSiteMap(sitemap):
                print("getlink",link)
                inqueue.put(link)
            count=10
        except Empty:
            count-=1
        except Exception as e:
            print(e)
            count-=1
def main():
    movieName=MovieReviewScraper(2,10,getMovieLinksFromSiteMapWrapper,list(getSitemap()),"review_list")
    for worker in movieName.preproducers:
        worker.join()
        print("A producer has exited")
    for worker in movieName.producers:
        worker.join()
        print("A producer has exited")
    movieName.writer.join()
    print("A writer has exited")
if __name__=="__main__":
    main()