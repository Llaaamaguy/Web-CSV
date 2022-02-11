from flask import Flask, render_template, request, redirect, jsonify, url_for
from werkzeug.utils import secure_filename
import os
from os.path import exists
import random
import pandas as pd
import time
import threading
from google.oauth2 import id_token
from google.auth.transport import requests
import io
from tabulate import tabulate
import json

# Init the Flask app
app = Flask(__name__)

# Determine the upload folder and allowed extensions
UPLOAD_FOLDER = "/Users/dkennedy/PycharmProjects/datatool/user_files"
ALLOWED_EXTENSIONS = ["csv"]

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = "x827GAO901Jjxj@82jceh@1"

buffer = io.StringIO()


# A check for if the file should be allowed
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Safely delete the files
def delete_files(files):
    time.sleep(60)
    for i in files:
        os.remove(i)


# Determine a unique file name
def add_file_securely(file):
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    while exists(filepath):
        file_name_extension = filename.split(".")
        file_name = file_name_extension[0]
        ext = file_name_extension[1]
        filename = file_name + str(random.randint(1, 10)) + "." + str(ext)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    file.save(filepath)
    return filepath


def add_html_securely(file_name, water=True):
    while exists(file_name):
        file_name = file_name.split(".")
        file = file_name[0]
        ext = file_name[1]
        file_name = file + str(random.randint(1, 10)) + "." + str(ext)

    if water:
        with open(file_name, "w") as f:
            f.write('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/water.css@2/out/water.css">')

    return file_name


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/handle_data", methods=["POST", "GET"])
def handle_data():
    if request.method == "POST":

        # If the user does not upload a file
        if 'file' not in request.files:
            return render_template("general_error.html", desc="Please select a file")

        file = request.files["file"]

        # Redundancy for if the user doesnt upload a file
        if file.filename == "":
            return render_template("general_error.html", desc="Please select a file")

        # Check if the file is allowed
        if not allowed_file(file.filename):
            return render_template("general_error.html", desc="You must use a .csv (comma separated values) file")

        if file and allowed_file(file.filename):
            filepath = add_file_securely(file)
            datafile = filepath
            data = pd.read_csv(filepath)

            # Generate the HTML file for the user to view their data
            html_data = data.to_html(classes="table table-striped")
            file_name = "templates/viewData" + str(random.randint(1, 9999999)) + ".html"
            file_name = add_html_securely(file_name)

            with open(file_name, "a") as f:
                f.write('<h1>Data View</h1>')
                f.write('<hr>')
                f.write(html_data)

            delfiles = [file_name, datafile]
            threading.Thread(target=delete_files, args=(delfiles,)).start()

            file_name = file_name.split("/")[1]

            return render_template(file_name)

        # The user will never see this
        return jsonify({"message": "file opened :thumbs_up:!"})

    if request.method == "GET":
        return render_template("general_error.html", desc="Please select a file")


# Data analyzation endpoint -- in development
@app.route("/analyze_data", methods=["POST", "GET"])
def analyze_data():
    if request.method == "GET":
        return jsonify({"message": "Feature coming soon"})
    if request.method == "POST":
        if 'file' not in request.files:
            return render_template("general_error.html", desc="Please select a file")

        file = request.files["file"]

        if file.filename == "":
            return render_template("general_error.html", desc="Please select a file")

        if not allowed_file(file.filename):
            return render_template("general_error.html", desc="You must use a .csv (comma separated values) file")

        filepath = add_file_securely(file)
        data = pd.read_csv(filepath)

        jsondata = data.to_json()
        parsed = json.loads(jsondata)

        data.info(buf=buffer)
        info = buffer.getvalue().split("\n")

        infohtml = ""
        for lines in info:
            infohtml = infohtml + "<pre>" + lines + "</pre> <br>\n"

        colhtml = tabulate([data.columns], tablefmt='html')

        delfiles = [filepath]
        threading.Thread(target=delete_files, args=(delfiles,)).start()

        return render_template("analyze_data.html", info=infohtml, jsondata=parsed, cols=colhtml)


# Verify the integrity of the given ID Token - This should always be True but there are rare cases where it is False
@app.route("/verify", methods=["POST", "GET"])
def verify():
    data = request.values
    idtoken = data["idtoken"]
    try:
        idinfo = id_token.verify_oauth2_token(idtoken, requests.Request(), os.environ["GOOGLE_CLIENTID"])
        userid = idinfo['sub']
        return idtoken
    except ValueError:
        return render_template("general_error.html", desc="Bad ID Token")


# Quick Access feature endpoint
@app.route("/quick_access/<idtoken>", methods=["POST", "GET"])
def quick_access(idtoken):
    return render_template("quick_access.html", id_token=idtoken)


@app.route("/render_graph", methods=["POST", "GET"])
def render_graph():
    if request.method == "POST":
        data = request.json
        print(data)
        return "OK: POST"
    if request.method == "GET":
        print("Get")
        return "BAD"


if __name__ == "__main__":
    app.debug = True

    app.run("127.0.0.1", 5000)
