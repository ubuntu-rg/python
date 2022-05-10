from flask import Flask, redirect, url_for, render_template

app = Flask(__name__)

# Pass argument to HTML file. Use {{content}} to get the content
# @app.route("/<name>")
# def homepage(name):
#     return render_template("index.html", content=name)


@app.route("/")
def homepage():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)