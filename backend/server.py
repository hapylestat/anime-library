from flask import Flask

from alist.config import Configuration


app = Flask(__name__)
cfg = Configuration.get_instance()


@app.route("/")
def main():
    return "%s there!" % cfg.get("test1")

@app.route("/test")
def test():
  return cfg.location


if __name__ == "__main__":
    app.run(debug=True,
            port=9000)