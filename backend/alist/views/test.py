
import alist.controller.main as main

app = main.Application.get_instance()

@app.route("/test")
def view_test():
  return "This is a TEST!"