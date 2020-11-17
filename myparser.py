# Bash parentheses
# a{b,{c,d}e}f prints abf acef adef
import sys
from enum import Enum
from dataclasses import dataclass
from itertools import chain, islice, zip_longest

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

def strings(node, prefix):
  if node is None:
    yield prefix
  else:
    for s in node.strings(prefix):
      yield s
    
class Literal:
  def __init__(self, value):
    self.value = value
    self.next = None
    
  def set_next(self, node):
    self.next = node
    
  def strings(self, prefix):
    return strings(self.next, prefix+self.value)
    
  def __str__(self):
    return f"'{self.value}'"
    

class Span:
  def __init__(self):
    self._first = self._last = None

  def append(self, node):
    if self._last:
      self._last.set_next(node)
      self._last = node
    else:
      self._first = self._last = node
      
  def set_next(self, node):
    self._last.set_next(node)
      
  def strings(self, prefix):
    return strings(self._first, prefix)

class Variant:
  def __init__(self, nodes):
    self.nodes = nodes
    
  def set_next(self, next):
    if self.nodes:
      for node in self.nodes:
        node.set_next(next)
    else:
      self.next = node

  def strings(self, prefix):
    if self.nodes:
      for node in self.nodes:
        for s in strings(node, prefix):
          yield s
    else:
      return strings(self.next, prefix)
      
  def __str__(self):
    return "(" + "|".join(str(node) for node in self.nodes) + ")"
      

def parse_span(tokenizer):
  span = Span()
  while True:
     token = tokenizer.next_token()
     if token.kind == TokenKind.LITERAL:
       span.append(Literal(token.value))
     elif token.kind == TokenKind.LEFT_BRACE:
       span.append(parse_variant(tokenizer))
     else:
       return span, token
       
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
  if s:
    return strings(parse(s), "")
  else:
    return [""]