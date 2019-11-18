#!/usr/bin/env python3

"""
3rd iteration of episode_generator functionality. Original was functional,
then rewrote to be object oriented. Due to issues with session and data not
remaining consistent, trying functional to see if this fixes the problem. This
is a clean up for a final reimplementation as a single page app.
"""

import requests
from sys import argv, version
import webbrowser
import bs4
from math import ceil
from random import choices

def run_search(term, imdb_page, debug = False):
    """
    this gets a specific page from the imdb search query. imdb_page is so named
    because it is the page in imdb's search (divided into 50), while mine is
    divided into five. Thus, search will have to be rerun every 10 pages
    """

    # confirm function call
    if debug:
        print("run_search()")

    # scrub search term for imdb
    formatted_term = "+".join(term.split())

    # add page information to search term
    if imdb_page > 0:
        page_specifier = f"&start={ (imdb_page * 50) + 1 }"
    else:
        page_specifier = ""

    # get BeautifulSoup data for search term
    search_string = "https://www.imdb.com/search/title?title=" + formatted_title + "&title_type=tv_series" + page_specifier
    if debug:
        print(f"search_string: {search_string}")
    search_soup = bs4.BeautifulSoup(requests.get(search_string).text, features="html.parser")

    #get max page
    if imdb_page < 1:

        # identify element that states range and number of results
        desc = search_soup.select(".desc")[0]
        span = desc.select("span")[0].contents[0][0:-8]

        # get number of results
        if span[:8] == "1-50 of ":
            span = span[8:]
        try:
            result_num = float(span)
        except:
            result_num = 0

        # calculate max_pages
        max_pages = int(ceil(result_num / 5))
        if debug:
            print(result_num)
            print(self.max_pages)

    else:
        max_pages = None;

    # get valid pages for no_results
    low = imdb_page * 10;
    high = low + 9
    range = [low, high]

    # cultivate return list
    links = search_soup.select("h3 > a")

    if debug:
        print(links)

    search_results = []

    for i in range(len(links)):
        if debug:
            print(i)

        try:
            show_div = links[i]
        except:
            break
        s = (show_div.get("href"), show_div.contents[0])
        search_results.append(s)

    if debug:
        print(f"search results length: {len(search_results)}")

    return {"results": search_results, "max": max_pages, "range": range}
