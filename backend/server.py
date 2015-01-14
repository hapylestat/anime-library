#!/usr/bin/env python3

from alist.controller.main import Application
import alist.views


def main():
    app = Application.get_instance()
    alist.views.load()

    app.start()

if __name__ == "__main__":
    main()