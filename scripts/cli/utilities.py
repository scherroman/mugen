import sys


def shutdown(error_message: str):
    message(error_message)
    sys.exit(1)


def message(message: str):
    print("\n" + message)
