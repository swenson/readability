# readability

Readability is an algorithm for computing a "readability" score for a given file or piece of code, as well as a Python program implementing that algorithm.

The score is agnostic to the language of the file: its metrics are basically independent of the actual
language.

## Example use cases

* To compare the same program written in different languages, and see
which implementation is more readable
* To enforce readability standards for a code base
* Because it is fun

## Algorithm description

The algorithm computes a bunch of scores, and combines them linearly (with different weights) to create an overall score for a file.

The current attributes we consider:

* The average line length
* The logarithm of the number of lines in the file
* The average symbol to token ratio, per line. (A symbol is a non-word, non-space character. A token is any word or symbol.)
* The number of lines per "block"". (A block is a group of lines separated from other blocks by whitespace, or by one- or two-character lines, i.e., `{` or `do`.

These are currently combined with a 20 &times; multiplier for the "symbol" score above, and 1 &times; for everything else.

**Higher** scores indicate **less** readable code, i.e., good code has a **low** score.

It seems to validate some of my own intuition.
For example, the following Python code has a score of 65.64

```python
def this_is_some_good_code(var):
  for i in range(10):
    print(i)
```

While the following, functionally equivalent code, has a score of 85.43 (stricly worse), even
though it is shorter.

```python
tisgc = lambda var: [print(i) for i in range(10)]
```

It is penalized for having more symbols and longer lines.

For kicks, the following APL code is even worse: its score is 86.49.

```apl
life←{↑1 ⍵∨.∧3 4=+/,¯1 0 1∘.⊖¯1 0 1∘.⌽⊂⍵}
```

(APL example taken from http://en.wikipedia.org/wiki/APL_%28programming_language%29#Examples.)

The readability score for `readability.py` is 256.12.


## Algorithm TODOs

* Combine multiple file scores together in some more meaningful way
* Add more metrics to the mix
* Adjust coefficients


## Program features

The program computes scores for any files it is passed, and will recursively check directories.
It ignores `.git` and `.svn` directories, as well as common binary file formats.
It outputs its scores so that they can be sorted with `sort -n`.

Since the program is largely I/O-bound, it is multi-threaded, using 4 threads to try to
read all of files requested simultaneously.

## Program usage

```sh
./readability.py some-directory-or-file-names-here
```

Example:

```
./readability .
```
## Program TODOs

* Honor `.gitignore`, etc., files
* Move to a queueing model to start outputting file scores faster

## License

MIT license.
