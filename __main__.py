import sys
from myparser import process_expression

for line in sys.stdin:
  for s in process_expression(line):
    print(s)
  