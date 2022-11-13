from flask import Flask, render_template, redirect, url_for, request, session
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "daidonprabeshdada"
app.permanent_session_lifetime = timedelta(hours=1)


@app.route('/', methods=["POST", "GET"])
def index():
    if request.method == "POST":
        session.permanent = True
        user = request.form["title"]

        session["user"] = user

        return redirect(url_for("inbox"))
    else:
        if "user" in session:
            user = session["user"]
            return render_template('base.html', user_valid=user)
        else:
            return render_template('base.html')


@app.route('/user')
def inbox():
    if "user" in session:
        user = session["user"]
        return render_template('customarea.html', username=user)
    else:
        return redirect(url_for("index"))


@app.route('/logout')
def logout():
    session.pop("user", None)

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
