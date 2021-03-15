# litecounter

> Very simple counter implemented on top of SQLite

## Why?

You can use this to implement a persistent counter. It also uses some SQLite syntax to initialize keys to `0` when the counter starts on them, just as if you had a `collections.defaultdict` where the default is `0`.

## Installation

```
pip install litecounter
```

**IMPORTANT**: This package uses SQLite's [UPSERT](https://sqlite.org/lang_upsert.html) statment so it needs to run at least with SQLite version 3.24.0 (released 2018-06-04).

If you need to run the latest version, you can use [pysqlite3](https://github.com/coleifer/pysqlite3).

All the litements libraries (including this one) accept either a filename or an already created sqlite connection. Apart from that, if you have pysqlite3 installed it will use that instead of the sqlite3 module from the standard library.

## Examples

The examples are taken from the tests in [`tests.ipynb`](./tests.ipynb)


```python

TEST_1 = "key_test_1"
TEST_2 = "key_test_2"

from litecounter import SQLCounter

counter = SQLCounter(":memory:")

# Increment from 0 to 20

for _ in range(20):
    counter.incr(TEST_1)
    
assert counter.count(TEST_1) == 20

# Decrement 10 (from 20 to 10)

for _ in range(10):
    counter.decr(TEST_1)
    
assert counter.count(TEST_1) == 10

# From 0 to -10, then -20.

for _ in range(10):
    counter.decr(TEST_2)
    
assert counter.count(TEST_2) == -10

for _ in range(10):
    counter.decr(TEST_2)
    
assert counter.count(TEST_2) == -20

# Set fist key to 0.

counter.zero(TEST_1)

assert counter.count(TEST_1) == 0

# Increment the second test key by 100, from -20 to 80.

for _ in range(100):
    counter.incr(TEST_2)
    
assert counter.count(TEST_2) == 80

# Delete key works

assert counter.count(TEST_1) == 0

counter.delete(TEST_1)

assert counter.count(TEST_1) is None

# When the key does not exist, delete just ignores it

counter.delete("foobar")

# Check `__repr__`

import random

for key in ["foo", "bar", "baz", "foobar", "asd", TEST_1]:
    for _ in range(random.randint(0,10)):
        counter.incr(key)

print(counter)

# SQLCounter(dbname=':memory:', items=[('key_test_2', 80), ('foo', 8), ('baz', 5), ('foobar', 6), ('key_test_1', 10)])
```

    
## Meta


Ricardo Ander-Egg Aguilar – [@ricardoanderegg](https://twitter.com/ricardoanderegg) –

- [ricardoanderegg.com](http://ricardoanderegg.com/)
- [github.com/polyrand](https://github.com/polyrand/)
- [linkedin.com/in/ricardoanderegg](http://linkedin.com/in/ricardoanderegg)

Distributed under the MIT license. See ``LICENSE`` for more information.

## Contributing

The only hard rules for the project are:

* No extra dependencies allowed
* No extra files, everything must be inside the main module's `.py` file.
* Tests must be inside the `tests.ipynb` notebook.