#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Compute a readability score of text or files.

Run like: ./readability.py some directories or files or glob patterns
"""

import glob
import os
import os.path
import re
import sys

from math import log
from multiprocessing.pool import ThreadPool as Pool
from pprint import pprint
from threading import Lock

# these are the weights to multiply the individual scores by
SYMBOL_CONST = 20.0
LPB_CONST = 1.0
LINE_LEN_CONST = 1.0
LLOC_CONST = 1.0

IGNORE_DIRS = set([
  'bower_components',
  'node_modules'
])

IGNORE_DIRS = set(['/' + d for d in IGNORE_DIRS])

# ignore these file extensions
IGNORE_EXTS = [
 '7z',
 'DS_Store',
 'a',
 'acn',
 'acr',
 'alg',
 'aux',
 'avi',
 'bak',
 'BAK',
 'bbl',
 'bcf',
 'blg',
 'brf',
 'bz2',
 'class',
 'classpath',
 'com',
 'crt',
 'dat',
 'db',
 'dll',
 'dmg',
 'dvi',
 'egg',
 'end',
 'eot',
 'eps',
 'exe',
 'fdb_latexmk',
 'fls',
 'flv',
 'gem',
 'gif',
 'glg',
 'glo',
 'gls',
 'gz',
 'ico',
 'idea',
 'ids',
 'idx',
 'ilg',
 'iml',
 'ind',
 'ipr',
 'iso',
 'ist',
 'iws',
 'jar',
 'jpg',
 'key',
 'loa',
 'lof',
 'log',
 'lol',
 'lot',
 'maf',
 'metadata',
 'mo',
 'mov',
 'mp3',
 'mp4',
 'mpg',
 'mtc',
 'mtc0',
 'mw',
 'nav',
 'nlo',
 'o',
 'ogg',
 'ogv',
 'otf',
 'out',
 'pdf',
 'pdfsync',
 'pem',
 'plist',
 'png',
 'pot',
 'project',
 'ps',
 'pyc',
 'pyd',
 'pyg',
 'pyo',
 'rar',
 'rbc',
 'repl_history',
 'scmd',
 'settings',
 'sm',
 'snm',
 'so',
 'sout',
 'spec',
 'sql',
 'sqlite',
 'svg',
 'swap',
 'swp',
 'sympy',
 'tar',
 'tdo',
 'thm',
 'toc',
 'ttf',
 'ttyrec',
 'vrb',
 'wav',
 'webm',
 'wma',
 'wmv',
 'woff',
 'xdy',
 'zip']

TOKEN_RE = re.compile(r'(\W+)', flags=re.UNICODE)

EXT_RE = re.compile('.*\\.(' + '|'.join(IGNORE_EXTS) + ')')

def log2(x):
  """Computes the log of the number in base 2."""
  return log(x, 2)


def is_symbol(x):
  """Checks if a token is a non-word character, i.e., a symbol."""
  match = TOKEN_RE.match(x)
  if not match:
    return False
  return len(match.group(0)) == len(x)

def lines_per_block(text, lines):
  """Computes the average number of lines per block.
     A block is a group of lines that are separated by white space,
     or by a short delimiter (like { / }, or if / fi)."""

  blocks = []
  curr = 0
  for l in lines:
    if len(l.strip()) <= 2:
      if curr:
        blocks.append(curr)
      curr = 0
    else:
      curr += 1
  if curr:
    blocks.append(curr)
  raw = sum(b for b in blocks) / float(max(1, len(blocks)))
  return raw


def symbol_score(text, lines):
  """Computes the average ratio of symbols to total tokens (symbols and words)
     per line."""

  s = 0.0
  for l in lines:
    raw_tokens = TOKEN_RE.split(l)
    tokens = []
    for raw in raw_tokens:
      tokens.extend([r.strip() for r in raw.split()])
    syms = sum([len(t) for t in tokens if is_symbol(t)])
    non_syms = sum(len(t) for t in tokens if not is_symbol(t))
    s += syms / float(max(1, syms + non_syms))
  return s / max(1, len(lines))

def line_length(text, lines):
  """Returns the average line length."""
  return sum(len(l) for l in lines) / float(max(1, len(lines)))

def lloc(text, lines):
  """Returns the logarithm of the number of lines in the file."""
  return log2(2 + len(lines))

def raw_score(text):
  """Computes all of the different scores and returns a dictionary of them."""
  lines = text.strip().split("\n")
  return dict(symbol=symbol_score(text, lines),
              line_len=line_length(text, lines),
              lloc=lloc(text, lines),
              lines_per_block=lines_per_block(text, lines))

def score(text):
  """Computes a total score as a float based on a weighted sum of the
     different individual scores, and multiplied by the logarithm of the
     number of lines."""

  raw = raw_score(text)
  return (raw['symbol'] * SYMBOL_CONST + \
          raw['lines_per_block'] * LPB_CONST + \
          raw['line_len'] * LINE_LEN_CONST) * raw['lloc'] * LLOC_CONST

print_lock = Lock()

def score_file(fname):
  """Computes the score of a file and prints it out."""
  with open(fname) as fin:
    text = fin.read()
    s = score(text)
    with print_lock:
      print("%.2f %s" % (s, fname))
      return s

if __name__ == '__main__':
  if len(sys.argv) == 1:
    print("Usage: ./readability.py files or directories or glob patterns")
    exit()

  files = set()
  for pattern in sys.argv[1:]:
    if os.path.isdir(pattern):
      for dirname, _, fnames in os.walk(os.path.abspath(pattern)):
        if dirname.startswith('.') or "/." in dirname:
          continue

        bad = False
        for bad_dir in IGNORE_DIRS:
          if bad_dir in dirname:
            bad = True
            break
        if bad:
          continue

        for fname in fnames:
          if fname.startswith('.'):
            continue
          if EXT_RE.match(fname):
            continue
          files.add(os.path.join(dirname, fname))
    else:
      files |= set(glob.glob(pattern))

  pool = Pool(4)
  files = sorted(files)
  scores = pool.map_async(score_file, files).get((1<<30)-1)

  print '\n----\nAverage score: %.2f' % (sum(scores) / len(scores))
