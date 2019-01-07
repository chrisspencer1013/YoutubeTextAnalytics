#use this (with rename cause api is gonna be slower) to rename the episodes once downloaded

import re

with open('regex_title_test.txt','r') as f:
	for line in f:
		print(line)
		results = re.search(r"Episode\s{1}(?P<e>\d+)", line, re.DOTALL).groupdict()
		print(results)
