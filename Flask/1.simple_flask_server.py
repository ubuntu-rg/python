from flask import Flask, redirect, url_for
import flask
import string

app = Flask("__name__")


@app.route('/')
def homepage():
    return flask.Response('<html><head><title>Flask Server</title></head><body><h1>Flask Server V1.0</h1></body></html>')


# Add data in URL that will be reflected within the site
@app.route("/<name>")
def user_name(name):
    for char in string.digits:
        if char in name:
            return f"Bad Syntax, do not use numbers.."
    return f"Hello {name}"


# Redirect URL
@app.route("/admin")
def admin():
    return redirect(url_for("homepage"))


if __name__ == "__main__":
    app.run(host='0.0.0.0')