
Status
======

Currently tested and working:

"Atomic types":
- string (python data type, serialized to json via marshmallow )
- bytes (python data type, serialized to json via marshmallow )
- int (python data type, serialized to json via marshmallow )

"Product types":
- frozen dataclasses (because they are simply hashable)

