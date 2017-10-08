#!/usr/bin/env python
"""AIML parser for IA."""
from __future__ import print_function

from bs4 import BeautifulSoup as Soup
import re

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
    dp = [[int(0) for i in range(m+1)] for j in range(n+1)];
    i = 0;
    while i < n :
        j = 0;
        while j < m:
            if str1[i] == str2[j]:
                dp[i + 1][j + 1] = dp[i][j] + 1 
            else:
                dp[i + 1][j + 1] = max(dp[i][j + 1],dp[i + 1][j])
            j += 1
        i += 1
    if (dp[n][m] * 1.0) / n >= 0.7:
        return True
    return False


class Bot(object):
    def __init__(self, file_names):
        self._file_names = file_names
        self._patterns = {}
        self._variabile = {}
        
        self.learn(self._file_names)

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
                        return (False,[])
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
                        i = n
                        if list_p[i] == "*":
                            priority -= length
                            list_with_star.append((count,val.strip()))
                        elif list_p[i] == "_":
                            priority += 10
                    else :
                        while j < m :
                            if not isequal(list_p[i + 1],list_m[j]) :
                                val += list_m[j]
                                val += " "
                                j += 1
                                length += 1
                            else :
                                i += 1;
                                if list_p[i] == "*":
                                    priority -= length
                                    list_with_star.append((count,val.strip()))
                                elif list_p[i] == "_" :
                                    priority += 10
                                break
                        if j >= m:
                            return (False,[],0)
            if i == n and j == m:
                return (True,list_with_star,priority)
            return (False,[],0)

    def match(self, message):
        """Return the patterns that matches"""
        patterns = []
        for pattern, _ in self._patterns.items():
            t = self._match(pattern.text, message)
            if t[0]:
                patterns.append(pattern)
                print(t[1],t[2])
        return patterns

    def sort(self, patterns):
        """Sortam tiparele in functie de relevanta."""
        return patterns

    def response(self, message):
        """Returneza raspunsul."""
        # vedem ce tipare se potrivesc
        patterns = self.match(message)

        # le sortam in functie de relevanta (alea cu multe * sunt mai proate decat alea normale)
        patterns = self.sort(patterns)
        print("[debug] tipare potrivite:",patterns)
        return DEFAULT_RESPONSE

def main():
    bot = Bot(AIML_FILES)
    # import pdb; pdb.set_trace()
    while True:
        question = raw_input(">>")
        if question.lower().strip() == "exit":
            print(BYE)
            exit()
        response = bot.response(question)
        print(response)


if __name__ == "__main__":
    main()
