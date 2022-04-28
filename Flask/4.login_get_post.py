from flask import Flask, redirect, url_for, render_template, request

app = Flask("__name__")


@app.route("/")
def homepage():
    return render_template("base.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        return redirect(url_for("welcome", user=username))
    else:
        return render_template("login.html")

# path: accepts slash in the url
@app.route("/welcome-<path:user>")
def welcome(user):
    return render_template("welcome.html", username=user)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

