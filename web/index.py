"""Univers web interface."""

from flask import Flask, render_template
#from lib import config

app = Flask(__name__)


@app.route('/univers/admin')
def index():
    """Index function representing program entry.

    return response
    """
    return render_template("index.html")


@app.route('/univers/admin/add-links')
def index():
    """Index function representing program entry.

    return response
    """
    return render_template("add_links.html")


if __name__ == "__main__":
    app.run(debug=True)
