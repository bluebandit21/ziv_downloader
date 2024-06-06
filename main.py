#!/bin/env python3.12

import requests
import bs4
from pyrate_limiter import Duration, Rate, Limiter, BucketFullException
import typing
import zipfile
import io
import os

class BadChart(Exception):
    pass

limiter = Limiter(Rate(4, Duration.SECOND), max_delay=10000)

def lget(*args, **kwargs):
    limiter.try_acquire("ZIV get")
    return requests.get(*args, **kwargs)


ZIV_BASE="https://zenius-i-vanisher.com/v5.2/"

def crawl_packs(urls: typing.List[str]):
    pack_names = []
    print("Downloading list of packs...")
    for url in urls:
        pack_name = crawl_pack(url)
        pack_names.append(pack_name)
    print("Compressing downloaded packs...")
    os.mkdir('compressed')
    for pack_name in pack_names:
        compress_pack(pack_name)

def crawl_pack(url: str) -> str:
    print(f"Crawling pack at URL {url}")
    pack_page_html = lget(url).content
    pack_page = bs4.BeautifulSoup(pack_page_html, features="html.parser")

    pack_name = pack_page.find(attrs={"class":"headertop"}).find('h1').contents[0]

    def is_chart_elt(tag):
        if (not tag.has_attr("id")) or (not tag.has_attr("href")):
            return False
        return tag['id'].startswith("sim") and tag['href'].startswith("viewsimfile.php")
    
    chart_elts = pack_page.find_all(is_chart_elt)
    chart_hrefs: typing.List[str] = [chart_elt['href'] for chart_elt in chart_elts]

    chart_ids = [
        href[href.rfind('=')+1:] for href in chart_hrefs
    ]

    for chart_id in chart_ids:
        try:
            access_chart(f"downloads/{pack_name}", chart_id)
        except (BadChart, zipfile.BadZipFile):
            print("\t\tBad Chart? -- Human Intervention Required")
    return pack_name

def compress_pack(pack_name: str):
    # Takes pack at downloads/pack_name and generates a zipped file of the entirety at compressed/pack_name.zip
    print(f"Compressing pack {pack_name}...")
    with zipfile.ZipFile(f"compressed/{pack_name}.zip", "x", zipfile.ZIP_LZMA) as zipf:
        for root, _, files in os.walk(f"downloads/{pack_name}"):
            for filename in files:
                zipf.write(os.path.join(root, filename), os.path.join(root.removeprefix("downloads/"),filename))

def access_chart(pack_name: str, chart_id: str):
    chart_url = f"{ZIV_BASE}download.php?type=ddrsimfile&simfileid={chart_id}"
    chart_url_alt = f"{ZIV_BASE}download.php?type=ddrsimfilecustom&simfileid={chart_id}"
    print(f"\tFetching: {chart_url}...")
   
    chart = lget(chart_url)
    if chart.content.startswith("File not found".encode(encoding='ascii')):
        print(f"\t\tUnavailable; trying {chart_url_alt}...")
        chart = lget(chart_url_alt)
        if chart.content.startswith("File not found".encode(encoding='ascii')):
            raise BadChart()
        
    zipf = zipfile.ZipFile(io.BytesIO(chart.content))
    zipf.extractall(pack_name)



if __name__ == "__main__":
    # Paste a bunch of packs here :)
    pack_urls="""https://zenius-i-vanisher.com/v5.2/viewsimfilecategory.php?categoryid=365
https://zenius-i-vanisher.com/v5.2/viewsimfilecategory.php?categoryid=1535
https://zenius-i-vanisher.com/v5.2/viewsimfilecategory.php?categoryid=717"""

    crawl_packs(pack_urls.splitlines())