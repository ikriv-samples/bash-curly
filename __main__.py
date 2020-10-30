# Bash parentheses
# a{b,{c,d}e}f prints abf acef adef
import sys
from enum import Enum
from dataclasses import dataclass
from itertools import zip_longest, islice

class TokenKind(Enum):
  LEFT_BRACE = 0
  RIGHT_BRACE = 1
  COMMA = 2
  LITERAL = 3
  END = 4

@dataclass(frozen=True)  
class Token:
  kind: TokenKind
  value: str
  
class Tokenizer:
  token_map = {
    "{": TokenKind.LEFT_BRACE,
    "}": TokenKind.RIGHT_BRACE,
    ",": TokenKind.COMMA
  }
  
  def __init__(self, s:str):
    self.s = s.strip(" \t\n\r")
    self.pos = 0
    
  @staticmethod
  def is_special_char(c) -> bool:
    return (c is None) or (c in Tokenizer.token_map)
    
  def current_char(self) -> str:
    pos = self.pos
    if pos < len(self.s):
      return self.s[pos]
    return None
    
  def next_token(self) -> Token:
    if self.pos >= len(self.s):
      return Token(TokenKind.END, "")
       
    initial_pos = self.pos
    while not Tokenizer.is_special_char(self.current_char()):
      self.pos += 1
      
    if self.pos > initial_pos:
      return Token(TokenKind.LITERAL, self.s[initial_pos:self.pos])
    
    c = self.current_char()
    token = Token(Tokenizer.token_map[c], c)
    self.pos += 1
    return token

def print_node(node, prefix):
  if node is None:
    print(prefix)
  else:
    node.print(prefix)
    
class Literal:
  def __init__(self, value):
    self.value = value
    
  def set_next(self, node):
    self.next = node
    
  def print(self, prefix):

    print_node(self.next, prefix+self.value)
    
  def __str__(self):
    return f"'{self.value}'"
    

class Span:
  def __init__(self, nodes):
    self.nodes = nodes
	# iterate over pairs of adjacent nodes
    for node,next in zip_longest(nodes, islice(iter(nodes),1,None)):
      node.set_next(next)
      
  def set_next(self, node):
    if self.nodes:
      self.nodes[-1].set_next(node)
    else:
      self.next = node
      
  def print(self, prefix):
    to_print = self.nodes[0] if self.nodes else self.next
    print_node(to_print, prefix)
        
  def __str__(self):
    return ",".join(str(node) for node in self.nodes)


class Variant:
  def __init__(self, nodes):
    self.nodes = nodes
    
  def set_next(self, next):
    if self.nodes:
      for node in self.nodes:
        node.set_next(next)
    else:
      self.next = node

  def print(self, prefix):
    if self.nodes:
      for node in self.nodes:
        print_node(node, prefix)
    else:
      print_node(self.next, prefix)
      
  def __str__(self):
    return "(" + "|".join(str(node) for node in self.nodes) + ")"
      

def parse_span(tokenizer):
  nodes = []
  while True:
     token = tokenizer.next_token()
     if token.kind == TokenKind.LITERAL:
       nodes.append(Literal(token.value))
     elif token.kind == TokenKind.LEFT_BRACE:
       nodes.append(parse_variant(tokenizer))
     else:
       return Span(nodes), token
       
def parse_variant(tokenizer):
  nodes = []
  while True:
    span, token = parse_span(tokenizer)
    nodes.append(span)
    if token.kind == TokenKind.COMMA:
      continue

    if token.kind != TokenKind.RIGHT_BRACE:
      # it's an error; variant should end with a right brace
      if token.kind == TokenKind.END:
        print("Missing right brace at the end of string", file=sys.stderr)
      else:
        print(f"Unexpected token '{token.value}'", file=sys.stderr)

    return Variant(nodes)
  
def parse(s):
  result, token = parse_span(Tokenizer(s))
  if token.kind != TokenKind.END:
    print(f"Unexpected token '{token.value}', parsing terminated")
  return result
  
def process_expression(s):
  print_node(parse(s), "")

for line in sys.stdin:
  process_expression(line)
  