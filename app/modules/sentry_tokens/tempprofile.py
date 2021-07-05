import random
import re

regex = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z")
isdate = "2019-08-07T20:25:09.870Z"
isnot = "not date"
choices = [isnot, isdate]
for i in range(10000):
    item = random.choice(choices)
    if regex.match(item):
        print(f"{i} date")
