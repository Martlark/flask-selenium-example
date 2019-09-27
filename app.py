import time

from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/shutdown')
def testing_shutdown():
    if app.testing:
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
        return 'shutdown'
    return 'not testing'


@app.route('/grid')
def public_test():
    return render_template("grid.html", title="Auto Refresh Grid Example", time_seconds=int(time.time()))


@app.route('/')
def public_index():
    return render_template("index.html", title="Home Page", time_seconds=int(time.time()))


if __name__ == '__main__':
    app.run(debug=True)
