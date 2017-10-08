#!/usr/bin/env python
"""AIML parser for IA."""
from __future__ import print_function

import bs4
from bs4 import BeautifulSoup as Soup

import util

import re
import os
import random
import datetime

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

def isok(a,b,c):
    if abs(a-b) > 2 or abs(a-c) > 2:
        return False
    return True

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
    if (float(dp[n][m]) * 1.0) / float(n) >= 0.8 and isok(dp[n][m],n,m):
        return (True,(float(dp[n][m]) * 1.0) / float(max(n,m)))
    return (False,0)

def check_char(c,length,priority,list_with_star,val,count):
    if c == "*":
       priority += length*0.05
       list_with_star.append((count,val.strip()))
    elif c == "_":
        priority += 0.3
    return priority


class Bot(object):
    """Aiml bot."""
    def __init__(self, file_names):
        self._file_names = file_names
        self._patterns = {}
        self._variabile = {}
        self._bot = {"":""}

        self.learn(self._file_names)
        self._handles = {
            "br": self._h_br,
            "random": self._h_random,
            "srai": self._h_srai,
            "sr": self._h_srai,
            "star": self._h_star,
            "thatstar": self._h_star,
            "bot": self._h_bot,
            "get": self._h_get,
            "date": self._h_date,
            "id": self._h_id,
            "size": self._h_size,
            "uppercase": self._h_uppercase,
            "lowecase": self._h_lowercase,
            "title": self._h_formal,
            "think": self._h_think,
            "set": self._h_set,
            "gossip": self._h_gossip,
            "person": self._h_person,
            "person2": self._h_person2,
            "gender": self._h_gender
        }

    def _h_br(self, tag, list_with_star):
        return "\n"
    def _h_gender(self, tag, list_with_star):
        response = self._execute(tag, list_with_star)
        for re, val in util.defaultGender.items():
            response.replace(re, val)
        return response

    def _h_person(self, tag, list_with_star):
        response = self._execute(tag, list_with_star)
        for re, val in util.defaultPerson.items():
            response.replace(re, val)
        return response

    def _h_person2(self, tag, list_with_star):
        response = self._execute(tag, list_with_star)
        for re, val in util.defaultPerson2.items():
            response.replace(re, val)
        return response

    def _h_person(self, tag, list_with_star):
        response = self._execute(tag, list_with_star)
        for re, val in util.defaultPerson.items():
            response.replace(re, val)
        return response

    def _h_gossip(self, tag, list_with_star):
        response = self._execute(tag, list_with_star)
        with open("gossip.txt", "w") as f:
            f.writelines([response])
        return ""

    def _h_set(self, tag, list_with_star):
        response = self._execute(tag, list_with_star)
        self._variabile[tag["name"]] = response
        return ""

    def _h_think(self, tag, list_with_star):
        self._execute(tag, list_with_star)
        return ""

    def _h_formal(self, tag, list_with_star):
        response = self._execute(tag, list_with_star)
        return response.title()

    def _h_lowercase(self, tag, list_with_star):
        response = self._execute(tag, list_with_star)
        return response.lower()

    def _h_uppercase(self, tag, list_with_star):
        response = self._execute(tag, list_with_star)
        return response.uppercase()

    def _h_date(self, tag, list_with_star):
        return str(datetime.datetime.now())

    def _h_size(self, tag, list_with_star):
        return str(len(self._patterns))

    def _h_id(self, tag, list_with_star):
        return str("localhost")

    def _h_bot(self, tag, list_with_star):
        return self._bot.get(tag.get("name", ""), "")

    def _h_get(self, tag, list_with_star):
        return self._variabile.get(tag.get("name", ""), "")


    def _h_random(self, tag, list_with_star):
        response = ""
        lis = tag.findChildren("li")
        li = random.sample(lis, 1).pop()
        return response + self._execute(li, list_with_star)

    def _h_srai(self, tag, list_with_star):
        response = self._execute(tag, list_with_star)
        return self.response(response)

    def _h_star(self, tag, list_with_star):
        response = ""
        try:
            if "index" in tag:
                index = int(tag["index"])
                for ind, value in list_with_star:
                    if ind == index:
                        response += value
            else:
                for _, value in list_with_star:
                    response += value
        except Exception as exp:
            print("[DEBUG] Exceptie la star " + str(exp))
        return response

    def _h_default(self, tag, list_with_star):
        print("[DEBUG] Nu recunoastem {} : \n\n {} \n\n\n".format(tag, tag.contents))
        return ""

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
        priority = 0 * 1.0

        if n > m :
            return (False,[],0)

        # TODO(mmicu): Aici e locul pentru Domnul Victor sa straluceasca
        if pattern_text.find('*') == -1 and pattern_text.find("_") == -1:
            if n == m :
                while i < n:
                    tu = isequal(list_p[i],list_m[i])
                    priority += tu[1]
                    if tu[0]:
                        i += 1
                    else:
                        return (False,[],0)
                return (True,[],priority)
            else :
                return (False,[],1)
        else :
            list_with_star = [] # o sa fie perechi (index,value) cu semnificatia al index star poate fi inlocuit cu valoarea value
            count = 0            
            while i < n and j < m:
                if list_p[i] != "*" and list_p[i] != "_": 
                    tu = isequal(list_p[i],list_m[i])
                    priority += tu[1]
                    if tu[0]:
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
        patterns.sort(key = lambda x: x[2], reverse=True)
        return patterns

    def _execute(self, template, list_with_start):
        response = ""
        for content in template.contents:
            # print("CONTENT - ", content, " - ", type(content))
            if isinstance(content, (str, bs4.element.NavigableString)):
                # print("STR - ", content)
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
        # normalizarea
        for re, val in util.defaultNormal.items():
            message.replace(re, val)
        # vedem ce tipare se potrivesc
        patterns = self.match(message)

        # le sortam in functie de relevanta (alea cu multe * sunt mai proate decat alea normale)
        patterns = self.sort(patterns)
        # print("[debug] tipare potrivite:", "\n".join([str(p) for p in patterns]))
        # avem match
        if patterns:
            ales = patterns.pop(0)
            print("[DEBUG] Pattern ales", ales)
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
