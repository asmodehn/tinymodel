# tinymodel
Persist your Domain Model with tinydb.

This is a very usable prototype of a new way to understand code... but we take the pragmatic approach to get something running first, and keep it running, always.

## Details
At the higher level, tinymodel is a set of decorators you can use to save your domain model in a json file database (tinydb).

tinymodel uses customisable marshmallow (de)serialization to translate from python to json.
This is suitable for your domain model, that you may want to explore by editing a simple json structure.

At the lower level, tinymodel aims is to bootstrap optimal knowledge representation, for persistent code.
Meaning the code can be restarted again, and it recover its previous state.

This is an optimization goal to achieve, and we plan to implement that using klepto.

