#!/usr/bin/env python3
from flask import Flask
from alist.config import Configuration
import json
from alist.logger import alogger


app = Flask(__name__)
cfg = Configuration.get_instance()

def json_response(call, **options):
  log = alogger.getLogger(__name__)
  log.error(call.func_name)

  def new_json_response(*args, **kwargs):
    log.error("*%s" % new_json_response.call.func_name)
    return json.dumps({
      'query': call.func_name,
      'status': '',
      'data': call(*args, **kwargs),
      'cache': ''
    })

  new_json_response.call = call
  return new_json_response

@app.route("/test")
@json_response
def test():
  return {
    'field':'hahaha',
    'dasda':'xcaca'
  }

@app.route("/")
@json_response
def main():
    return "%s there!" % cfg.get("test")




if __name__ == "__main__":
    app.run(debug=True,
            port=9000)