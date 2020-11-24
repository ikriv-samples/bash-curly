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

    
class Empty:
  class _EmptyNode:
    def strings(self, prefix):
      yield prefix
    def __bool__(self):
      return False
  node = _EmptyNode()

class Literal:
  def __init__(self, value):
    self.value = value
    self._next = Empty.node

  def set_next(self, next):
    self._next = next
    
  def strings(self, prefix):
    return self._next.strings(prefix+self.value)
    

class Span:
  def __init__(self):
    self._first = self._last = Empty.node

  def __bool__(self):
    return bool(self._first)

  def append(self, node):
    if self._last:
      self._last.set_next(node)
      self._last = node
    else:
      self._first = self._last = node
      
  def set_next(self, node):
    self._last.set_next(node)
      
  def strings(self, prefix):
    return self._first.strings(prefix)

class Variant:
  def __init__(self, nodes):
    self.nodes = nodes
    
  def set_next(self, next):
    for node in self.nodes:
      node.set_next(next)

  def strings(self, prefix):
    for node in self.nodes:
      for s in node.strings(prefix):
        yield s
      
def parse_span(tokenizer):
  span = Span()
  while True:
     token = tokenizer.next_token()
     if token.kind == TokenKind.LITERAL:
       span.append(Literal(token.value))
     elif token.kind == TokenKind.LEFT_BRACE:
       span.append(parse_variant(tokenizer))
     else:
       if not span:
         raise ValueError("Empty span is not allowed")
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
        raise ValueError("Missing right brace at the end of string")
      else:
        raise ValueError(f"Unexpected token '{token.value}'")

    return Variant(nodes)
  
def parse(s):
  result, token = parse_span(Tokenizer(s))
  if token.kind != TokenKind.END:
    raise ValueError(f"Unexpected token '{token.value}', parsing terminated")
  return result
  
def process_expression(s):
  if s:
    return parse(s).strings("")
  else:
    return [""]