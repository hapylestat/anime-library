#!/usr/bin/env python3


def main():
    app = Application.get_instance()
    app.start()


def requirements_check():
    import sys
    if sys.version_info[0] < 3:
        print("Error. Python major version less than 3 is not supported")
        sys.exit(-1)

if __name__ == "__main__":
  requirements_check()

  from alist.controller.main import Application
  main()