#!/usr/bin/env python3

import alist.controller.main as main
import alist.views

app = main.Application.get_instance()
alist.views.load()

if __name__ == "__main__":
    app.start()