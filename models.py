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

def get_image(link, debug = False):
    """
    Acquire an image for either a show or episode.

    Note: There is a series of values at the ends of the titles that appears
    to specify it is a smaller version of a larger image. When this is
    removed, full size image can be accessed. I don't completely understand
    this mechanism (do the extra characters specify a separate copy of the
    original image or do they make the original image smaller?)
    """

    if debug:
        print("begin get_image")
        print(f"link: {link}")

    req = requests.get("https://www.imdb.com" + link)
    show_soup = bs4.BeautifulSoup(req.text, features="html.parser")

    # access poster poster_div
    try:
        poster_div = show_soup.select(".poster")[0]
    except:
        return None

    image_src = poster_div.select("a > img")[0].get("src")

    # chop size specifier off file name
    return image_src[0:-27] + ".jpg"

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
    search_string = "https://www.imdb.com/search/title?title=" + formatted_term + "&title_type=tv_series" + page_specifier
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
            print(max_pages)

    else:
        max_pages = None;

    # get valid pages for no_results
    low = imdb_page * 10;
    high = low + 9
    page_range = [low, high]

    # cultivate return list
    links = search_soup.select("h3 > a")

    if debug:
        print(links)

    search_results = []

    print(len(links))

    for i in range(len(links)):
        if debug:
            print(f"result: {i}")

        try:
            show_div = links[i]
        except:
            break
        s = (show_div.contents[0], show_div.get("href"))
        search_results.append(s)

    if debug:
        print(f"search results length: {len(search_results)}")

    return {"results": search_results, "max": max_pages, "range": page_range}

def make_page(results, page, debug = False):
    """
    gives the information for five shows, formatted for IMDB display

    results need to be the output of run_search()
    page is the page of our search results, not of the page on imdb
    """

    if debug:
        print("initiating make_page()")

    start = 5 * (page % 10)
    shows = []

    if debug:
        print(f"start: {start}")

    for i in range(start, start + 5):
        if debug:
            print(i)

        try:
            args = results[i]
        except:
            break

        s = {"title": args[0],"link": args[1],"image": get_image(args[1])}

        shows.append(s)
    if debug:
        for show in shows:
            print(show)
    return shows

def get_seasons(link, debug=False):
    """
    This determines how many seasons a show has using the link to the show

    This returns a list as opposed to an int due to the possibility of
    irregularities
    """

    if debug:
        print("begin get_seasons()")

    # get the BeautifulSoup data
    show_url = "https://www.imdb.com/" + link + "episodes/"
    tv_soup = bs4.BeautifulSoup(requests.get(show_url).text, features="html.parser")

    # We are acquiring this data from a drop down, which the below line selects
    select_elem = tv_soup.select('#bySeason')
    seasons = []
    # account for the possibility of a one season show
    if len(select_elem) == 0:
        seasons.append(1)
    else:
        # get contents of drop down
        options = select_elem[0].select('option')

        # add each season
        for season in options:
            seasons.append(season.get('value'))
        if debug:
            print(f"Seasons {seasons}")

    return seasons

def get_episodes(link, seasons, factor, debug=False):
    """
    this returns a dictionary containing a list of dicts containing the
    episodes link, season, episode number and rating and a list of weights
    for their selection
    """

    if debug:
        print("begin get_episodes()")
        print(seasons, factor)

    episodes = {"episodes": [], "weights": []}

    #this is the url that will be modified to access individual seasons
    base_url = f"https://www.imdb.com/{link}episodes?season="

    if debug:
        print(f"Base URL: {base_url}")

    # iterate through seasons
    for season in seasons:
        season_url = base_url + season
        season_soup = bs4.BeautifulSoup(requests.get(season_url).text, features="html.parser")
        episode_divs = season_soup.select(".list_item")

        #iterate through episodes
        for i in range(len(episode_divs)):
            div = episode_divs[i]
            ep_link = div.select('strong > a')[0].get('href')
            rating_elem = div.select('.ipl-rating-star__rating')

            # excludes unrated episodes ensuring they have been airred
            if len(rating_elem) != 0:
                rating = float(rating_elem[0].contents[0])

                #add episode
                episodes["episodes"].append({"link": ep_link,
                                    "season": int(season),
                                    "episode_number": i + 1,
                                    "rating": rating})

                # add weight if there is a factor selected
                if factor != 0:
                    weight = rating ** factor
                    episodes["weights"].append(weight)
                    if debug:
                        print(f"weight: {weight}")
    return episodes

def create_episode(e, debug=False):
    """
    takes an entry in the episode list and gathers all the necessary data
    """
    #{"title": , "summary": , "image": , "link": , "season": , "number": , "rating"}

    if debug:
        print("beginning create_episode()")

    episode = {}

    # get BeautifulSoup data for extracting details
    episode_url = "https://www.imdb.com/" + e["link"]
    episode_soup = bs4.BeautifulSoup(requests.get(episode_url).text, features="html.parser")

    #get title
    title_wrapper = episode_soup.select(".title_wrapper")[0]
    episode["title"] = title_wrapper.select("h1")[0].contents[0].replace(u'\xa0', ' ')

    #get summary
    episode["summary"] = episode_soup.select(".summary_text")[0].contents[0].replace(u'\n', ' ')

    #get image
    episode["image"] = get_image(e["link"], debug)

    #link
    episode["link"] = e["link"]

    #season
    episode["season"] =  e["season"]

    #number
    episode["number"] = e["episode_number"]

    #rating
    episode["rating"] = e["rating"]

    return episode


def pick(episodes, debug=False):
    """
    Pick the episode, gather its data and return all as a dictionary
    """

    if debug:
        print("begin pick()")

    # pick episodes
    # if factored
    if len(episodes["weights"]) != 0:
        e = choices(episodes["episodes"],
                    weights = episodes["weights"])[0]
    # otherwise
    else:
        e = choices(episodes["episodes"])[0]

    # gather the data
    episode = create_episode(e)

    return episode
