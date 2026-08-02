# START_GLOBALS
from generated.formats.nif.imports import name_type_map
# END_GLOBALS


class ByteMatrix:
# START_CLASS
	def __init__(self, **kwargs):
		BasicBase.__init__(self, **kwargs)
		self.set_value([])

	def get_value(self):
		return self._value

	def set_value(self, value):
		assert(isinstance(value, list))
		if value:
			size1 = len(value[0])
		for x in value:
			# TODO fix this for py3k
			#assert(isinstance(x, basestring))
			assert(len(x) == size1)
		self._value = value # should be a list of strings of bytes

	def get_size(self, data=None):
		if len(self._value) == 0:
			return 8
		else:
			return len(self._value) * len(self._value[0]) + 8

	def get_hash(self, data=None):
		return tuple( x.__hash__() for x in self._value )

	def read(self, stream, data):
		size1, = struct.unpack(data._byte_order + 'I',
							stream.read(4))
		size2, = struct.unpack(data._byte_order + 'I',
							stream.read(4))
		self._value = []
		for i in range(size2):
			self._value.append(stream.read(size1))

	def write(self, stream, data):
		if self._value:
			stream.write(struct.pack(data._byte_order + 'I',
									len(self._value[0])))
		else:
			stream.write(struct.pack(data._byte_order + 'I', 0))
		stream.write(struct.pack(data._byte_order + 'I',
								len(self._value)))
		for x in self._value:
			stream.write(x)

	def __str__(self):
		size1 = len(self._value[0]) if self._value else 0
		size2 = len(self._value)
		return "< %ix%i Bytes >" % (size2, size1)
