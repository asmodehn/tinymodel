import contextlib
import datetime
import pytz

from tinydb import TinyDB
from .model import TinyModel


class TinyMutableModel(TinyModel):

    def __init__(self, class_name, persist_db, schema):
        super(TinyMutableModel, self).__init__(class_name=class_name, persist_db=persist_db, schema=schema)
        self.schema = self._schema()  # Instantiating the schema
        self.past = persist_db.table("Past")
        #TODO : mergeable ?? CRDT ?? distributed DAG ?

    def __setitem__(self, key, value):
        serialized = self.schema.dump(value)  # or use dump string directly here ??
        # TODO : or use the field / schema distinction already in marshmallow ??
        if type(serialized) in [int, str, float]:  # TODO : basic types directly storable in json...
            # TODO : We probably need to have more strict restrictions here
            data = {key: serialized}
        else:
            name_pair = {'name': key}  # AKA "the indexing problem"
            data = {k: v for k, v in value.items()}  # if hasattr(value, 'items') else {'value': value}
            data.update(name_pair)

        if key in self and self[key] != data:
            # tracking past events if there is a difference...
            self.past.insert({
                'table': self.table.name,
                'until': datetime.datetime.now(tz=pytz.utc).isoformat(),
                key: self[key]  # get the current version
            })

        # By default we do not track time. Present is now.
        docid = self.table.insert(data)

        self.idx[key] = docid


@contextlib.contextmanager
def mutate(model: TinyModel):

    yield TinyMutableModel(class_name=model._name, persist_db=model._persist, schema=model._schema)

    return model


if __name__ == '__main__':

    class DataModel:
        def __init__(self, value):
            self.myvalue = value

    m = TinyMutableModel("DataModel", persist_db=TinyDB('tinymodel.json'))

    m['test1'] = vars(DataModel(value = 42))
    m['test2'] = vars(DataModel(value=51))

    assert m['test1'] == {'name': 'test1', 'myvalue': 42}, print(m.get('test1'))
    assert m['test2'] == {'name': 'test2', 'myvalue': 51}, print(m.get('test2'))