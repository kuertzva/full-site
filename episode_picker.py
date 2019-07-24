#! python3

"""
This is to create the function necessary to create a web application for
picking random episodes of tv shows based on IMDB information
"""

import requests
from sys import argv
import webbrowser
import bs4
from math import ceil
from random import choices

def get_image(link):

    print("initiating get_image")
    print(f"link: {link}")

    show_soup = bs4.BeautifulSoup(requests.get("https://www.imdb.com" +
                                  link).text, features="html.parser")

    # access the media viewer page
    try:
        poster_div = show_soup.select(".poster")[0]
    except:
        return None

    image_src = poster_div.select("a > img")[0].get("src")

    return image_src[0:-27] + ".jpg"

def find_show(title):
    """
    this runs a search in IMDB, selects the top result and returns the url
    """

    print("initiating find_show")

    # format the title for the insertion into the search URL
    formatted_title = ""

    for word in title.split():
        formatted_title += word
        formatted_title += "+"

    formatted_title = formatted_title[:-1]

    # use the formatted title get the search page
    search_string = "https://www.imdb.com/search/title?title=" + formatted_title + "&title_type=tv_series"

    print(f"search_string: {search_string}")
    # isolate the individual search results
    campbell = bs4.BeautifulSoup(requests.get(search_string).text, features="html.parser")
    links = campbell.select("h3 > a")
    ret_len = min(5, len(links))

    # (title, link, image)
    ret = []



    for i in range(ret_len):
        show = links[i]
        title = show.contents[0]
        link = show.get("href")
        image = get_image(link)
        ret.append({"image": image, "title": title, "link": link, "index": i})

    return ret

def get_details(link):

    print("initiating get_details")

    # create parser
    show_url = "https://www.imdb.com/" + link + "episodes/"
    tvSoup = bs4.BeautifulSoup(requests.get(show_url).text, features="html.parser")

    # isolate title of
    header = tvSoup.select(".subpage_title_block")
    print("length = " + str(len(header)))
    header = header[0]
    title = header.select(".parent")[0].select("a")[0].contents[0]

    # isolate image for show
    image = get_image('/' + link)

    # find number of seasons
    select_elem = tvSoup.select('#bySeason')
    if len(select_elem) == 0:
        seasons = 1
    else:
        options = select_elem[0].select('option')

        """
        This SHOULD work because it appears IMDB formats this select element smallest
        to largest. Should this vary between shows, code can be added to grab the
        value from each element and select the largest
        """
        seasons = int(options[-1].get('value'))


    # return in form {title, image, link, seasons}

    return {"title":title, "image":image, "url":show_url, "seasons": seasons}

def pick_episode(show_url, seasons, rating_factor):

    print("initiating pick_episode")

    episodes = []
    print(show_url, seasons, rating_factor)

    # extract episodes and ratings if relevant
    for season in seasons:
        season_url = show_url + "?season=" + season
        seasonal_soup = bs4.BeautifulSoup(requests.get(season_url).text, features="html.parser")
        episode_divs = seasonal_soup.select(".list_item")

        ep_count = 1

        for div in episode_divs:

            # get link
            ep_link = div.select('strong > a')[0].get('href')

            # get rating
            rating_elem = div.select('.ipl-rating-star__rating')

            # ensures episode has rating(has airred)
            if len(rating_elem) != 0:

                if rating_factor != 0:
                    rating = float(rating_elem[0].contents[0])
                    repeats = ceil(rating * (rating_factor / 10.0))

                else:
                    repeats = 1

                for i in range(repeats):
                    episodes.append((ep_link,(season, str(ep_count))))

            ep_count += 1

    return choices(episodes)

def episode_details(link):

    print("initiating episode_details")

    episode_url = "https://www.imdb.com/" + link

    episode_Soup = bs4.BeautifulSoup(requests.get(episode_url).text, features="html.parser")

    # get title
    title_wrapper = episode_Soup.select(".title_wrapper")[0]
    title = title_wrapper.select("h1")[0].contents[0].replace(u'\xa0', ' ')

    # get image
    poster_div = episode_Soup.select(".poster")[0]
    image = poster_div.select("a > img")[0].get("src")

    # get synopsis
    summary = episode_Soup.select(".summary_text")[0].contents[0].replace(u'\n', ' ')

    return {'title': title, 'image': image, 'summary': summary}
















if __name__ == "__main__":

    title = ' '.join(argv[1:])

    show = find_show(title)[0]

    print(show)

    details = get_details(show["link"])

    print(details)

    print(pick_episode(details['url'], range(details['seasons']), 0))
