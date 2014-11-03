
import alist.controller.main as main

app = main.Application.get_instance()


@app.route("/")
def view_index():
  return "%s there!" % app.cfg.get("logging")["log_level"]