#!/usr/bin/env python
"""AIML parser for IA."""
from __future__ import print_function

import bs4
from bs4 import BeautifulSoup as Soup

import re
import os
import random

# alice, standard, None
# BOT_TYPE = "alice"
BOT_TYPE = "standard"

# BOT_TYPE = "alice"
if BOT_TYPE:
    AIML_FILES = ["{}/{}".format(BOT_TYPE, f) for f in os.listdir(BOT_TYPE)]
else:
    AIML_FILES = ["basic_chat.aiml"]

DEFAULT_RESPONSE = "Nu am inteles"
EXIT = "exit"
BYE = "Bye Bye!"

REMOVE_CHARS = ".!?;[]'{}()"

# XML tags
CATEGORY = "category"
TEMPLATE = "template"
PATTERN = "pattern"

def clean(msg):
    for char in REMOVE_CHARS:
        msg = msg.replace(char, " ")
    return msg.lower().strip().replace("  ", " ")

def isequal(str1,str2):
    n, m = len(str1), len(str2)
    dp = [[int(0) for i in range(m+1)] for j in range(n+1)]
    i = 0
    while i < n:
        j = 0
        while j < m:
            if str1[i] == str2[j]:
                dp[i + 1][j + 1] = dp[i][j] + 1
            else:
                dp[i + 1][j + 1] = max(dp[i][j + 1], dp[i + 1][j])
            j += 1
        i += 1
    if (dp[n][m] * 1.0) / n >= 0.7:
        return True
    return False

def check_char(c,length,priority,list_with_star,val,count):
    if c == "*":
       priority -= length
       list_with_star.append((count,val.strip()))
    elif c == "_":
        priority += 10
    return priority


class Bot(object):
    """Aiml bot."""
    def __init__(self, file_names):
        self._file_names = file_names
        self._patterns = {}
        self._variabile = {}

        self.learn(self._file_names)
        self._handles = {
            "random": self._h_random
        }

    def _h_default(self, tag, list_with_star):
        print("[DEBUG] Nu recunoastem {}".format(tag))
        return ""

    def _h_random(self, tag, list_with_star):
        response = ""
        lis = tag.findChildren("li")
        li = random.sample(lis, 1).pop()
        return response + self._execute(li, list_with_star)

    def _h_text(self, tag, list_with_star):
        response = ""
        lis = tag.findChildren("li")
        li = random.sample(lis, 1).pop()
        return response + self._execute(li, list_with_star)

    def _learn(self, file_name):
        data = open(file_name, "r").read()
        soup = Soup(data, "lxml")

        for category in soup.findChildren(CATEGORY):
            self._patterns[category.find(PATTERN)] = category.findChildren(TEMPLATE)


    def learn(self, file_names):
        """Learn from the aiml files."""
        for f in file_names:
            self._learn(f)

    def _match(self, pattern_text, message):
        """Returneaza True data pattern_text se potriveste cu message."""
        pattern_text = clean(pattern_text)
        message = clean(message)
        list_p = pattern_text.split()
        list_m = message.split()
        i, j, n, m = 0, 0, len(list_p), len(list_m)
        priority = 0

        # TODO(mmicu): Aici e locul pentru Domnul Victor sa straluceasca
        if pattern_text.find('*') == -1 and pattern_text.find("_") == -1:
            if n == m :
                while i < n:
                    if isequal(list_p[i],list_m[i]):
                        i += 1
                    else:
                        return (False,[],0)
                return (True,[],0)
            else :
                return (False,[],0)
        else :
            list_with_star = [] # o sa fie perechi (index,value) cu semnificatia al index star poate fi inlocuit cu valoarea value
            count = 0            
            while i < n and j < m:
                if list_p[i] != "*" and list_p[i] != "_": 
                    if isequal(list_p[i],list_m[j]):
                        i += 1
                        j += 1
                        continue
                    else: 
                        return (False,[],0)
                else:
                    count += 1;
                    length = 0;
                    val = "";
                    if i + 1 >= n: 
                        while j < m:
                          val += list_m[j];
                          val += " "
                          j += 1
                          length += 1
                        priority = check_char(list_p[i],length,priority,list_with_star,val,count)
                        i = n
                    else :
                        while j < m :
                            if not isequal(list_p[i + 1],list_m[j]):
                                val += list_m[j]
                                val += " "
                                j += 1
                                length += 1
                            else :
                                priority = check_char(list_p[i],length,priority,list_with_star,val,count)
                                i += 1;
                                break
                        if j >= m:
                            return (False,[],0)
            if i == n and j == m:
                return (True,list_with_star,priority)
            return (False,[],0)

    def match(self, message):
        """Return the patterns that matches"""
        patterns = []
        for pattern in self._patterns.keys():
            tem = self._match(pattern.text, message)
            if tem[0]:
                patterns.append((pattern, tem[1], tem[2]))
        return patterns

    def sort(self, patterns):
        """Sortam tiparele in functie de relevanta."""
        patterns.sort(key = lambda x: x[2])
        return patterns

    def _execute(self, template, list_with_start):
        response = ""
        for content in template.contents:
            if isinstance(content, str):
                response += content
            elif isinstance(content, bs4.element.Tag):
                to_run = self._handles.get(content.name, self._h_default)
                print("[debug] Tag {} running {}".format(content, to_run))
                response += to_run(content, list_with_start)
        return response


    def _handle(self, templates, list_with_star):
        total_response = ""
        for template in templates:
            total_response += self._execute(template, list_with_star)
        return total_response


    def response(self, message):
        """Returneza raspunsul."""
        # vedem ce tipare se potrivesc
        patterns = self.match(message)

        # le sortam in functie de relevanta (alea cu multe * sunt mai proate decat alea normale)
        patterns = self.sort(patterns)
        print("[debug] tipare potrivite:", "\n".join([str(p) for p in patterns]))
        # avem match
        if patterns:
            ales = patterns.pop(0)
            return self._handle(self._patterns[ales[0]], ales[1])
        return DEFAULT_RESPONSE


def main():
    bot = Bot(AIML_FILES)
    while True:
        question = raw_input(">>")
        if question.lower().strip() == "exit":
            print(BYE)
            exit()
        resp = bot.response(question)
        print("+++++", resp)


if __name__ == "__main__":
    main()
