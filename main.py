from flask import Flask, render_template, redirect, url_for, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "daidonprabeshdada"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///redirects.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(days=1)

db = SQLAlchemy(app)


class redirects(db.Model):
    _id = db.Column("id", db.INTEGER, primary_key=True)
    linker = db.Column(db.String(30))
    text = db.Column(db.String(500))

    def __init__(self, linker, text):
        self.linker = linker
        self.text = text


def redirect_of(current_session: dict()) -> bool:
    if "link" in current_session:
        return True
    else:
        return False


@app.route('/', methods=["POST", "GET"])
def index():
    if request.method == "POST":
        session.permanent = True
        link = request.form["title"]
        link = " ".join(link.split())

        if redirect_of(session) and link != session["link"]:
            logout()

        session["link"] = link

        found_user = redirects.query.filter_by(linker=link).first()
        if found_user:
            session["textinput"] = found_user.text
        else:
            lnk = redirects(link, "")
            db.session.add(lnk)
            db.session.commit()

        return redirect(url_for("inbox"))
    else:
        if redirect_of(session):
            link = session["link"]
            return render_template('base.html', link_valid=link)
        else:
            return render_template('base.html')


@app.route('/link', methods=["POST", "GET"])
def inbox():
    text = None
    if redirect_of(session):
        link = session["link"]

        if request.method == "POST":
            text = request.form["textinput"]
            session["textinput"] = text
            found_user = redirects.query.filter_by(linker=link).first()
            found_user.text = text
            db.session.commit()
            flash("Your text has been saved for later!", "info")
        else:
            if "textinput" in session:
                text = session["textinput"]
        return render_template('customarea.html', linkname=link, textinput=text)
    else:
        return redirect(url_for("index"))


@app.route('/logout')
def logout():
    link = session["link"]
    session.pop("link", None)
    session.pop("textinput", None)
    flash(f"{link.capitalize()} was replaced from the session!", "info")

    return redirect(url_for("index"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)
