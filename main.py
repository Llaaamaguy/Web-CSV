from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
from os.path import exists
import random
import pandas as pd
import io

app = Flask(__name__)

UPLOAD_FOLDER = "/Users/dkennedy/PycharmProjects/datatool/user_files"
ALLOWED_EXTENSIONS = ["csv"]

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

buf = io.StringIO()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/handle_data", methods=["POST", "GET"])
def handle_data():
    if request.method == "POST":

        if 'file' not in request.files:
            print("No file")

            return redirect(request.url)

        file = request.files["file"]

        if file.filename == "":
            print("No selected file")

            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

            while exists(filepath):
                fnameext = filename.split(".")
                fname = fnameext[0]
                ext = fnameext[1]
                filename = fname + str(random.randint(1, 10)) + "." + str(ext)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

            file.save(filepath)

            data = pd.read_csv(filepath)
            data.to_string(buf=buf)
            s = buf.getvalue()

            return data.to_string()

        return "file uploaded"

    if request.method == "GET":
        return "This was made by a get method?"


if __name__ == "__main__":
    app.secret_key = "x827GAO901Jjxj@82jceh@1"

    app.debug = True

    app.run("127.0.0.1", 5000)

