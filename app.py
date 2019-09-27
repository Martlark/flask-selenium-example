import time

from flask import Flask, render_template, request, session

app = Flask(__name__)
refresh_count = 0


@app.route('/shutdown')
def testing_shutdown():
    if app.testing:
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
        return 'shutdown'
    return 'not testing'


@app.route('/auto_refresh')
def public_test():
    global refresh_count
    refresh_count += 1
    return render_template("auto_refresh.html", title="Auto Refresh Grid Example", refresh_count=refresh_count,
                           time_seconds=int(time.time()))


@app.route('/')
def public_index():
    return render_template("index.html", title="Home Page", time_seconds=int(time.time()))


if __name__ == '__main__':
    app.run(debug=True)
