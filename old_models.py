#!/usr/bin/env python3

"""
2nd iteration of the episode_generators functionality. While prior
implementation was functional in nature, this is Object Oriented. Beyond making
me a stronger Object Oriented Programmer, the benefit is that this will allow me
to store values inside object.
"""

import requests
from sys import argv, version
import webbrowser
import bs4
from math import ceil
from random import choices

class proto():
    def __init__(self, link, debug):
        self.link = link
        self.debug = debug

    def get_image(self): ###
        """
        Acquire an image for either a show or episode.

        Note: There is a series of values at the ends of the titles that appears
        to specify it is a smaller version of a larger image. When this is
        removed, full size image can be accessed. I don't completely understand
        this mechanism (do the extra characters specify a separate copy of the
        original image or do they make the original image smaller?)
        """

        if self.debug:
            print("begin get_image")
            print(f"link: {self.link}")

        req = requests.get("https://www.imdb.com" + self.link)
        show_soup = bs4.BeautifulSoup(req.text, features="html.parser")

        # access poster poster_div
        try:
            poster_div = show_soup.select(".poster")[0]
        except:
            return None

        image_src = poster_div.select("a > img")[0].get("src")

        # chop size specifier off file name
        return image_src[0:-27] + ".jpg"





class episode(proto):
    def __init__(self, link, season, number, rating, debug):

        proto.__init__(self, link, debug)

        episode_url = "https://www.imdb.com/" + self.link
        self.episode_soup = bs4.BeautifulSoup(requests.get(episode_url).text, features="html.parser")

        self.debug = debug
        self.title = self.get_title()
        self.summary = self.get_summary()
        self.image = self.get_image()
        self.link = link
        self.season = season
        self.number = number
        self.rating = rating

        episode_url = "https://www.imdb.com/" + self.link
        self.episode_soup = bs4.BeautifulSoup(requests.get(episode_url).text, features="html.parser")

    def __str__(self):
        return "This episode is {self.title} (season {self.season}, episode {self.number}), with a rating of {self.rating}"

    def get_title(self):
        if self.debug:
            print("begin get_title")

        title_wrapper = self.episode_soup.select(".title_wrapper")[0]
        title = title_wrapper.select("h1")[0].contents[0].replace(u'\xa0', ' ')

        return title

    def get_summary(self):
        if self.debug:
            print("begin get_summary")

        summary = self.episode_soup.select(".summary_text")[0].contents[0].replace(u'\n', ' ')

        if self.debug:
            print(summary)

        return summary

    def return_episode(self):
        return {"title":self.title, "summary":self.summary, "image": self.image,
                "link":self.link, "season":self.season, "number":self.number,
                "rating":self.rating}




class show(proto):
    def __init__(self, link, title, debug):

        proto.__init__(self, link, debug)

        self.debug = debug
        self.title = title
        self.link = link
        self.image = self.get_image()
        self.seasons = []
        self.episode = None

        self.episodes = {"episodes": [], "weights": []}

    def __str__(self):

        ret_string = f"This show is titled {self.title}"

        if self.seasons == 0:
            return ret_string +"."
        else:
            return ret_string + f" and has {self.seasons}."

    def set_seasons(self):

        if self.debug:
            print("being get_seasons")

        show_url = "https://www.imdb.com/" + self.link + "episodes/"
        tvSoup = bs4.BeautifulSoup(requests.get(show_url).text, features="html.parser")

        # find number of seasons
        select_elem = tvSoup.select('#bySeason')
        if len(select_elem) == 0:
            self.seasons = 1
        else:
            options = select_elem[0].select('option')

            """
            This SHOULD work because it appears IMDB formats this select element smallest
            to largest. Should this vary between shows, code can be added to grab the
            value from each element and select the largest
            """
            for season in options:
                self.seasons.append(season.get('value'))
            print(f"Seasons {self.seasons}")

    def return_show(self):
        return {"title": self.title, "link": self.link, "image": self.image,
                "seasons": self. seasons}

    def gather_episodes(self, seasons, rating_factor):

        if self.debug:
             print("initiating pick_episode")
             print(seasons, rating_factor)

        base_url = f"https://www.imdb.com/{self.link}episodes?season="

        if self.debug:
            print(base_url)

        for season in seasons:
            season_url = base_url + season
            season_soup = bs4.BeautifulSoup(requests.get(season_url).text, features="html.parser")
            episode_divs = season_soup.select(".list_item")

            for i in range(len(episode_divs)):

                div = episode_divs[i]
                ep_link = div.select('strong > a')[0].get('href')
                rating_elem = div.select('.ipl-rating-star__rating')

                # ensures episode has rating(has airred)
                if len(rating_elem) != 0:
                    rating = float(rating_elem[0].contents[0])

                    self.episodes["episodes"].append((ep_link, (int(season)), i + 1, rating))

                    if rating_factor != 0:
                        weight = rating ** rating_factor
                        self.episodes["weights"].append(weight)
                        if self.debug:
                            print(f"weight: {weight}")


    def pick_episode(self):

        if len(self.episodes["weights"]) != 0:
            e = choices(self.episodes["episodes"],
                        weights = self.episodes["weights"])[0]

        else:
            e = choices(self.episodes["episodes"])[0]

        self.episode = episode(e[0], e[1], e[2], e[3], self.debug)

        return self.episode.return_episode()

    def get_episode(self):

        if episode == None:
            print("Warning: No episode has been selected")

        else:
            return self.episode

class wrapper_object():
    def __init__(self, debug=False):

        self.debug = debug

        # search values
        self.search_term = None
        self.internal_page = 1
        self.external_page = 1
        self.search_results = []
        self.display_shows = (0, [])
        self.max_pages = None


        self.show = None

    def __str__(self):
        ret_string = "This is a wrapper object"

        if self.show != None:
            ret_string += f" for the show {self.show}."

        elif len(self.search_results) != 0:
            ret_string += f" with the potential shows {self.search_results}."

        else:
            ret_string += "."

        return ret_string

    def set_search_term(self, search_term):
        self.search_term = search_term

    def run_search(self):

        if self.debug:
            print("initiating find_show")

        formatted_title = "+".join(self.search_term.split())

        if self.external_page > 1:
            page_specifier = f"&start={ ((self.external_page - 1) * 50) + 1 }"

        else:
            page_specifier = ""

        search_string = "https://www.imdb.com/search/title?title=" + formatted_title + "&title_type=tv_series" + page_specifier

        if self.debug:
            print(f"search_string: {search_string}")

        search_soup = bs4.BeautifulSoup(requests.get(search_string).text, features="html.parser")

        if self.max_pages == None:

            desc = search_soup.select(".desc")[0]
            span = desc.select("span")[0].contents[0][0:-8]
            if span[:8] == "1-50 of ":
                span = span[8:]
            try:
                result_num = float(span)
            except:
                result_num = 0
            self.max_pages = int(ceil(result_num / 5))
            if self.debug:
                print(result_num)
                print(self.max_pages)

        links = search_soup.select("h3 > a")

        if self.debug:
            print(links)

        self.search_results = []

        for i in range(len(links)):
            if self.debug:
                print(i)

            try:
                show_div = links[i]
            except:
                break
            s = (show_div.get("href"), show_div.contents[0], self.debug)
            self.search_results.append(s)

        if self.debug:
            print(f"search results length: {len(self.search_results)}")

    def get_shows(self):

        if len(self.search_results) == 0:
            return (0,[])

        if self.debug:
            print("begin get_shows")

        start = 5 * (self.internal_page - 1) - (50 * (self.external_page - 1))

        if self.debug:
            print(f"start: {start}")

        if self.internal_page != self.display_shows[0]:

            self.display_shows = (self.internal_page, [])

            for i in range(start, start + 5):
                if self.debug:
                    print(i)

                try:
                    args = self.search_results[i]
                except:
                    break
                s = show(args[0], args[1], args[2])

                self.display_shows[1].append(s)

        return self.display_shows

    def get_search_page(self):
        return {"internal": self.internal_page, "external": self.external_page}

    def has_searched(self):
        if len(self.search_results) > 0:
            return True
        return False

    def change_page(self, change):

        if self.debug:
            print("begin change_page")
            print(f"change: {change}")

        self.internal_page += change

        print(f"intenrnal_page: {self.internal_page}")

        external_page = ((self.internal_page - 1) // 10) + 1

        if self.debug:
            print(f"external page: {external_page}")


        if self.external_page != external_page:
            self.external_page = external_page
            self.run_search()

        return self.get_search_page()



    def set_show(self, idx):

        if self.debug:
            print("begin set_show")
            print(f"search results length: {len(self.search_results)}")
            print(f"index: {idx}")

        self.show = self.display_shows[1][idx]
        print(self.show)
        self.show.set_seasons()

    def get_show(self):

        if self.show == None:
            print("Warning: no show yet determined")
        else:
            return self.show

    def get_max_page(self):
        return self.max_pages
