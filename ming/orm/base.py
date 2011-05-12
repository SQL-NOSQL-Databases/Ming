from .icollection import instrument

def state(obj):
    '''The state of a mapped object'''
    return obj.__ming__.state

def mapper(v, doc_cls=None):
    '''Map a ORM class onto its document class'''
    if isinstance(v, type):
        cls = v
    else:
        cls = type(v)
        return mapper(type(v))
    if doc_cls is not None:
        pass
    return cls.__ming__.mapper

def session(v):
    '''The ORMSession object managing either a class or an instance'''
    if isinstance(v, type):
        return v.__mongometa__.session
    else:
        return session(type(v))

def lookup_class(name):
    from .mapped_class import MappedClass
    try:
        return MappedClass._registry[name]
    except KeyError:
        for n, cls in MappedClass._registry.iteritems():
            if n.endswith('.' + name): return cls
        raise

class Decoration(object):

    def __init__(self, obj, bson):
        self.obj = obj
        doc_cls = mapper(obj).doc_cls
        self.state = ObjectState()
        doc = instrument(doc_cls.make(bson),
                         DocumentTracker(self.state))
        self.state.document = doc
        self.state.original_document = bson

class ObjectState(object):
    new, clean, dirty, deleted = 'new clean dirty deleted'.split()

    def __init__(self):
        self._status = self.new
        self.original_document = None
        self.document = None
        self.extra_state = {}

    def soil(self):
        if self.status == self.clean:
            self.status = self.dirty

    def _get_status(self):
        return self._status
    def _set_status(self, value):
        self._status = value
    status = property(_get_status, _set_status)

    def __repr__(self):
        return '<ObjectState status=%s>' % self.status

class DocumentTracker(object):
    __slots__ = ('state',)

    def __init__(self, state):
        self.state = state

    def soil(self, value):
        self.state.soil()
    added_item = soil
    removed_item = soil
    cleared = soil

