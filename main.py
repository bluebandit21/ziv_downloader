#!/bin/env python3.12

import requests
import bs4
from pyrate_limiter import Duration, Rate, Limiter, BucketFullException

limiter = Limiter(Rate(4, Duration.SECOND), max_delay=10000)

def lget(*args, **kwargs):
    limiter.try_acquire("ZIV get")
    return requests.get(*args, **kwargs)


ZIV_BASE="https://zenius-i-vanisher.com/v5.2/"

def crawl_pack(url: str):
    print(f"Crawling pack at URL {url}")
    pack_page_html = lget(url).content
    pack_page = bs4.BeautifulSoup(pack_page_html, features="html.parser")

    def is_chart_elt(tag):
        if (not tag.has_attr("id")) or (not tag.has_attr("href")):
            return False
        return tag['id'].startswith("sim") and tag['href'].startswith("viewsimfile.php")
    
    chart_elts = pack_page.find_all(is_chart_elt)
    chart_hrefs = [ZIV_BASE + chart_elt['href'] for chart_elt in chart_elts]

    print(chart_hrefs)

def access_chart(url: str):
    pass



if __name__ == "__main__":
    crawl_pack("https://zenius-i-vanisher.com/v5.2/viewsimfilecategory.php?categoryid=94")