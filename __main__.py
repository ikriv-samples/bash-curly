import sys
from myparser import process_expression

for line in sys.stdin:
  try:
    for s in process_expression(line):
      print(s)
  except Exception as ex:
    print(ex)
  