#!/usr/bin/env python3

"""
creates the views for homepage and episode picker combined.
"""

from flask import Flask, request, render_template, json, session
import requests
from models import *
import webbrowser
from random import randint
import os

dbg = False

app = Flask(__name__)
app.secret_key = app.secret_key= os.environ.get('SECRET_KEY', None)

#routes
@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/ep_search", methods=["GET"])
def ep_search():
    return render_template("search.html")

@app.route("/search_results", methods=["GET", "POST"])
def search_results():

    #initial search page
    if request.method == "POST":
        session["search_term"] = request.form["title"]
        session["search_page"] = 0
        r = run_search(session["search_term"], 0, dbg)
        session["search_results"] = r["results"]
        session["max_pages"] = r["max"]
        session["valid_range"] = r["range"]
        print(f"Range: {type(r['range'])}")

    # noninitials
    else:
        # change page
        session["search_page"] = int(request.args.get('page', None))

        # if page accessed incorrectly, redirect
        if "search_term" not in session:
            return ep_search()
        # if out of range
        if session["search_page"] < session["valid_range"][0] or session["search_page"] > session["valid_range"][1]:
            r = run_search(session["search_term"],
                            (session["search_page"] // 10),
                            dbg)
            session["search_results"] = r["results"]
            session["valid_range"] = r["range"]

    # gather output
    results = make_page(session["search_results"],
                        session["search_page"],
                        dbg)

    session["search_batch"] = results

    return render_template("select_show.html",
                            results=results,
                            page=session["search_page"],
                            max_page= session["max_pages"])

@app.route("/show/<path:idx>")
def specification(idx):

    # make sure that this not accessed incorrectly
    if "search_term" not in session:
        return ep_search()

    # this is to allow the user to go back from the last page
    if idx != "change":
        show = session["search_batch"][int(idx)]
        session["show_title"] = show["title"]
        session["show_link"] = show["link"]
        session["show_image"] = show["image"]
        session["show_seasons"] = get_seasons(session["show_link"], dbg)

    # return values
    details = {"title": session["show_title"],
               "link": session["show_link"],
               "image": session["show_image"],
               "seasons": session["show_seasons"]}

    if dbg:
        print(f"Show details: {details}")

    return render_template("specify_params.html", details=details)

@app.route("/result", methods=["GET", "POST"])
def result():
    # ensure that page accessed incorrectly
    if "show_title" not in session:
        return ep_search()

    # this allows repicking without doing all the work over
    if request.method == "POST":
        session["selected_seasons"] = request.form.getlist('seasons')
        session["factor"] = float(request.form.get('slider'))
        session["episodes"]= get_episodes(session["show_link"],
                                          session["selected_seasons"],
                                          session["factor"],
                                          dbg)

    # pick the episode
    ep = pick(session["episodes"])

    if dbg:
        print(ep)

    return render_template("result.html", details=ep)

if __name__ == "__main__":
    app.run(debug=False)
