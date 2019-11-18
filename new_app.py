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
app.secret_key= os.environ.get('SECRET_KEY', None)
