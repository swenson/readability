#!/usr/bin/env python
# -*- coding: utf-8 -*-

import readability
import unittest

good_code = """
def this_is_some_good_code(var):
  for i in range(10):
    print(i)
"""

bad_code = """
tisgc = lambda var: [print(i) for i in range(10)]
"""

apl_code = u"""
life←{↑1 ⍵∨.∧3 4=+/,¯1 0 1∘.⊖¯1 0 1∘.⌽⊂⍵}
"""

class TestReadability(unittest.TestCase):
  def setUp(self):
    pass

  def test_good_better_than_bad(self):
    good_score = readability.score(good_code)
    bad_score = readability.score(bad_code)
    apl_score = readability.score(apl_code)

    self.assertTrue(good_score < bad_score < apl_score)

  def test_ignore_pattern(self):
    self.assertFalse(readability.EXT_RE.match("abc.py"))
    self.assertTrue(readability.EXT_RE.match("abc.pyc"))

if __name__ == '__main__':
    unittest.main()
