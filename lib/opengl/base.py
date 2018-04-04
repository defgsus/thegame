from pyglet.gl import *
from .error import OpenGlError
from .types import *


class OpenGlObjects:
    instance_counter = 0
    instances = dict()


class OpenGlBaseObject:

    def __init__(self, name=None):
        OpenGlObjects.instance_counter += 1
        self._name = name or "%s" % OpenGlObjects.instance_counter
        while self._name in OpenGlObjects.instances:
            self._name += str(id(self))[-2:]
        self._handle = None

    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__, self.name)

    def __repr__(self):
        return self.__str__()

    @property
    def name(self):
        return self._name

    @property
    def handle(self):
        return self._handle

    def is_created(self):
        return self._handle is not None

    def check_created(self, action_name):
        if not self.is_created():
            raise OpenGlError("%s on uninitialized %s" % (action_name, self))

    def create(self):
        if self.is_created():
            raise OpenGlError(".create() on initialized %s" % self)
        self._create()
        OpenGlObjects.instances[self.name] = self

    def release(self):
        if not self.is_created():
            raise OpenGlError(".release() on uninitialized %s" % self)
        self._release()
        if self.name in OpenGlObjects.instances:
            del OpenGlObjects.instances[self.name]

    def bind(self):
        if not self.is_created():
            raise OpenGlError(".bind() on uninitialized %s" % self)
        self._bind()

    def unbind(self):
        if not self.is_created():
            raise OpenGlError(".unbind() on uninitialized %s" % self)
        self._unbind()

    @classmethod
    def dump_instances(cls):
        for name in sorted(OpenGlObjects.instances):
            print(OpenGlObjects.instances[name])