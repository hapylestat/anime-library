#!/usr/bin/env python3

from alist.controller.main import Application


def main():
    app = Application.get_instance()
    app.start()

if __name__ == "__main__":
    main()