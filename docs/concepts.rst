TinyModel Concepts
==================

TinyModel stores your data models in a json file for later use.

To be able to do this, it enforces a functional relation to the instances of your datamodel.
Which means you can access your data instance as you would the content of a mapping structure (like a dict).

Therefore you can:
- assume computation cost of data is optional (it will, except the very first time)
- store your computation while running, die, and resume where you were previously in the computation.
- explore the current knowledge held in your process (via reading the "memory" json file)
- Run "offline" process on the "memory" json file, for optimization purposes or other.

This turns out to be mostly useful for long running processes with slow interractions with the real world.

Algebraic Permanent DataTypes
-----------------------------

We aim to adopt here a categorical way to structure data, exposing algebraic data types that are permanent (as long as you dont erase the memory file).

The "base" or "atomic" types are the lowest common denominator of data types between python and json languages.
The "product" types are the types that are deterministically serializable to a json structure, without ambiguity.
The "sum"/"union" types are a bit special. There is nothing native to python or json, and they need special implementation choices. They will be addressed LATER...





