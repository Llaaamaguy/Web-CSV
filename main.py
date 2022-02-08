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

app = Flask(__name__)

UPLOAD_FOLDER = "/Users/dkennedy/PycharmProjects/datatool/user_files"
ALLOWED_EXTENSIONS = ["csv"]

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = "x827GAO901Jjxj@82jceh@1"


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def delete_file(html_file, data_file):
    time.sleep(60)
    os.remove(html_file)
    os.remove(data_file)


def add_file_securely(file):
    while exists(file):
        file_name_extension = file.split(".")
        file_name = file_name_extension[0]
        ext = file_name_extension[1]
        file = file_name + str(random.randint(1, 10)) + "." + str(ext)
    return file


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

        if file.filename == "":
            return render_template("general_error.html", desc="Please select a file")

        if not allowed_file(file.filename):
            return render_template("general_error.html", desc="You must use a .csv (comma separated values) file")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            datafile = filepath

            while exists(filepath):
                file_name_extension = filename.split(".")
                file_name = file_name_extension[0]
                ext = file_name_extension[1]
                filename = file_name + str(random.randint(1, 10)) + "." + str(ext)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                datafile = filepath

            file.save(filepath)
            data = pd.read_csv(filepath)

            html_data = data.to_html(classes="table table-striped")
            file_name = "templates/viewData" + str(random.randint(1, 9999999)) + ".html"
            while exists(file_name):
                file_name = file_name.split(".")
                file = file_name[0]
                ext = file_name[1]
                file_name = file + str(random.randint(1, 10)) + "." + str(ext)

            with open(file_name, "w") as f:
                f.write('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/water.css@2/out/water.css">')

            with open(file_name, "a") as f:
                f.write('<h1>Data View</h1>')
                f.write('<hr>')
                f.write(html_data)

            threading.Thread(target=delete_file, args=(file_name, datafile)).start()

            file_name = file_name.split("/")[1]

            return render_template(file_name)

        return jsonify({"message": "file opened :thumbs_up:!"})

    if request.method == "GET":
        return render_template("general_error.html", desc="Please select a file")


@app.route("/analyze_data", methods=["POST", "GET"])
def analyze_data():
    if request.method == "GET":
        return jsonify({"message": "Feature coming soon"})
    if request.method == "POST":
        if 'file' not in request.files:
            return jsonify({"error": "Please select a file"})

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "Please select a file"})

        if not allowed_file(file):
            return jsonify({"error"})

        return jsonify({"message": "Feature coming soon"})


@app.route("/verify", methods=["POST", "GET"])
def verify():
    data = request.values
    idtoken = data["idtoken"]
    try:
        idinfo = id_token.verify_oauth2_token(idtoken, requests.Request(), os.environ["GOOGLE_CLIENTID"])
        userid = idinfo['sub']
        return idtoken
    except ValueError:
        return jsonify({"Error": "Invalid id token"})


@app.route("/quick_access/<idtoken>", methods=["POST", "GET"])
def quick_access(idtoken):
    return render_template("quick_access.html", id_token=idtoken)


if __name__ == "__main__":
    app.debug = True

    app.run("127.0.0.1", 5000)
