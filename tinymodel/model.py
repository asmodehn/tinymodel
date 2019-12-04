
from collections import Mapping, OrderedDict

from tinydb import TinyDB, Query


class TinyModel(Mapping):

    def __init__(self, class_name, persist_db, schema):
        self._schema = schema
        self._persist = persist_db
        self._name = class_name
        self.table = persist_db.table(class_name, )
        self.idx = OrderedDict()  # some kind of cache ??

    def __getitem__(self, item):
        if item in self.idx:
            item_val = self.table.get(doc_id=self.idx[item])
        else:  # search
            q = Query()
            item_res = self.table.search(q.name == item)
            assert isinstance(item_res, list)
            if not item_res:
                raise KeyError(f"{item} not found")
            else:
                item_val = item_res[0]  # get the first result
                # TODO : should be unique...
                self.idx[item] = item_val.doc_id
        return item_val

    def __iter__(self):
        return iter([e.get('name', 'UNKNOWN') for e in self.table])

    def __len__(self):
        return len(self.table)

