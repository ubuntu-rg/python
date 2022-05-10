from flask import Flask, redirect, url_for, render_template

app = Flask(__name__)

@app.route("/")
def homepage():
    return render_template("inherit.html")

@app.route("/about")
def about():
    return render_template("about_us.html")

if __name__ == "__main__":
    app.run("0.0.0.0", port=8080, debug=True)