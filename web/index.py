"""Univers web interface."""

from flask import Flask, render_template

app = Flask(__name__)


@app.route('/univers/admin')
def index():
    """Index function representing program entry.

    return response
    """
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
