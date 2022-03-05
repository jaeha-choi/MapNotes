from flask import Flask

app = Flask(__name__)


@app.route('/')
def root():
    return "<p>Placeholder for Prog 5 website</p>"


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
