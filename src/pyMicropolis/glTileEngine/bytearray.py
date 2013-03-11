# Iterable wrapper class for C++ buffers (unsigned char*) using Python arrays.

import gltileengine
import array

class ByteArray(array.array):
	def __init__(self, t, data):
		# TODO rename self.array to self.pointer
		self.array = gltileengine.intAsBytePointer(self.buffer_info()[0])

