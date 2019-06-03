from controlpyweb.abstract_reader_writer import AbstractReaderWriter
import threading
from controlpyweb.errors import ControlPyWebReadOnlyError
from str2bool import str2bool

lock = threading.Lock()


class SingleIO:
    def __init__(self, name: str, addr: str, default: object, reader: AbstractReaderWriter = None):
        self.name = name
        self.addr = addr
        self._reader_writer = reader
        self._value = default

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other

    def __get__(self, instance, owner):
        try:
            self.read()
        except:
            pass
        return self

    def __set__(self, obj, value):
        raise ControlPyWebReadOnlyError

    def __str__(self):
        return f'{type(self).__name__}: {self.name} = {self.value}'

    @property
    def value(self):
        return self._convert_type(self._value)

    @staticmethod
    def _convert_type(value):
        return value

    def read(self):
        with lock:
            val = self._reader_writer.read(self.addr)
            self._value = val
            return val

    def read_immediate(self):
        with lock:
            val = self._reader_writer.read_immediate(self.addr)
            self._value = val
            return val


class DiscreteIn(SingleIO):
    def __init__(self, name: str, addr: str, default: bool = False, reader: AbstractReaderWriter = None):
        super().__init__(name, addr, default, reader)

    @staticmethod
    def _convert_type(value):
        if isinstance(value, str):
            return str2bool(value)
        return bool(value)

    def __bool__(self):
        return self.value


class IOOut(DiscreteIn):
    def __init__(self, name: str, addr: str, default: bool, writer: AbstractReaderWriter):
        super().__init__(name, addr, default, writer)

    def __set__(self, instance, value):
        self.write(value)

    def write(self, value):
        self._reader_writer.write(self.addr, self._convert_type(value))
        self._value = value

    def write_immediate(self, value):
        self._reader_writer.write_immediate(self.addr, self._convert_type(value))
        self._value = value


class DiscreteOut(IOOut, DiscreteIn):
    def __init__(self, name: str, addr: str, default: bool = False, writer: AbstractReaderWriter = None):
        super().__init__(name, addr, default, writer)




