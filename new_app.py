#!/usr/bin/env python3

"""
creates the views for homepage and episode picker combined.
"""

from flask import Flask, request, render_template, json, session
import requests
from func_models import *
import webbrowser
from random import randint
import os

dbg = False

app = Flask(__name__)
app.secret_key= os.environ.get('SECRET_KEY', None)
session[""]

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

    # noninitials
    else:
        # if page accessed incorrectly, redirect
        if "search_term" not in session:
            return ep_search()
        # if out of range
        if session[search_page] < range[0] OR session[search_page] > range[1]:
            r = run_search(session["search_term"],
                            (session["search_page"] // 10),
                            dbg)
            session["search_results"] = r["results"]
            session["valid_range"] = r["range"]









    return render_template("select_show.html",
                            results=session["search_results"],
                            page=session["search_page"],
                            max_page= max_page)

@app.route("/show/<path:idx>")
def specification(idx):

    global active_users

    if 'user' not in session:
        return index()
    wrapper = active_users[session["user"]]

    if not wrapper.has_searched():
        return index()

    if idx != "change":
        wrapper.set_show(int(idx))

    details = wrapper.get_show().return_show()

    print(details)

    return render_template("specify_params.html", details=details)

@app.route("/result", methods=["GET", "POST"])
def result():

    global active_users

    if 'user' not in session:
        return index()

    wrapper = active_users[session["user"]]

    if not wrapper.has_searched():
        return index()

    show = wrapper.get_show()

    if request.method == "POST":
        seasons = request.form.getlist('seasons')
        factor = float(request.form.get('slider'))
        show.gather_episodes(seasons, factor)

    ep = show.pick_episode()

    print(ep)

    return render_template("result.html", details=ep)

if __name__ == "__main__":
    app.run(debug=False)
