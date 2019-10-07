#!/usr/bin/env

"""
Bug list:
"""

from flask import Flask, request, render_template, json, session
import requests
from models import *
import webbrowser
from random import randint

dbg = False

app = Flask(__name__)
active_users = {"": "placeholder"}
app.secret_key= "Food-is-good-Soup"

# helper functions
def create_object(search_term):
    global active_users, dbg

    user = ""

    while user in active_users:

        # create cookie
        key = search_term
        for i in range(3):
            key += str(randint(0, 9))

        user = key

    session["user"] = user

    active_users[session["user"]] = wrapper_object(dbg)

def destruct():

    global active_users

    active_users.pop(session["user"])

#routes
@app.route("/")
def homepage():
    return render_template("index.html")
@app.route("/plaid")
def plaidman():
    return render_template("plaid.html")

@app.route("/ep_search", methods=["GET"])
def ep_search():
    return render_template("search.html")

@app.route("/search_results", methods=["GET", "POST"])
def search_results():

    global active_users

    # initial search page
    if request.method == "POST":

        title = request.form["title"]
        create_object(title)

        wrapper = active_users[session["user"]]
        wrapper.set_search_term(title)
        wrapper.run_search()
        page = 1


    # page change
    else:
        # if page not accessed correct, redirect to beginning
        if 'user' not in session:
            return index()
        wrapper = active_users[session["user"]]

        if not wrapper.has_searched():
            return index()

        page = request.args.get('page', None)
        print(page)

        # ensure page is correct
        wrapper.change_page(int(page) - wrapper.get_search_page()["internal"])
        page = wrapper.get_search_page()["internal"]

    results = wrapper.get_shows()[1]

    if len(results) == 0:
        return render_template("no_results.html")

    return render_template("select_show.html", results=results, page=page, max_page= wrapper.get_max_page())

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
