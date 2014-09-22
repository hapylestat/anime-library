from flask import Flask
from alist.config import Configuration

app = Flask(__name__)
cfg = Configuration.getInstance()

@app.route("/")
def main():
    return "Hello there!"

@app.route("/test")
def test():
  return cfg.location


if __name__ == "__main__":
    app.run(debug=True,
            port=9000)