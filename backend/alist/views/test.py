
import alist.controller.main as main
from flask import request

app = main.Application.get_instance()

@app.route("/test")
def view_test():
  try:
    app.aa += 1
  except:
    app.aa = 1

  return "This is a TEST! %s <br> %s" % (app.aa, request.args.to_dict())

@app.route("/test/<name>")
def view_test_name(name):
  return "Passed name is: %s" % name