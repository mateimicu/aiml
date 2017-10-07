#!/usr/bin/env python
"""AIML parser for IA."""
from __future__ import print_function

AIML_FILES = ["basic_chat.aiml"]
DEFAULT_RESPONSE = "Nu am inteles"
EXIT = "exit"
BYE = "Bye Bye!"

class Bot(object):
    def __init__(self, file_name):
        self._file_name = file_name
        self._variabile = {}

    def math(self, message):
        """Return the pattern that matches"""

    def response(self, message):
        """Returneza raspunsul."""
        return DEFAULT_RESPONSE

def main():
    bot = Bot(AIML_FILES)
    while True:
        question = raw_input(">>")
        if question.lower().strip() == "exit":
            print(BYE)
            exit()
        response = bot.response(question)
        print(response)

if __name__ == "__main__":
    main()
