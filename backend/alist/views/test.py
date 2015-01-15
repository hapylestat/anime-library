
import alist.controller.main as main

app = main.Application.get_instance()


@app.route("/test")
def view_test(args):
  try:
    app.aa += 1
  except:
    app.aa = 1

  return "This is a TEST! %s <br> %s" % (app.aa, args)


@app.route("/test/<name>")
def view_test_name(name):
  return "Passed name is: %s" % name