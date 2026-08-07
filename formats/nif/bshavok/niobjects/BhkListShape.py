# START_GLOBALS
from generated.utils.mathutils import vecAdd, vecscalarMul, matAdd
# END_GLOBALS

class BhkListShape:
# START_CLASS

	def get_mass_center_inertia(self, density = 1, solid = True):
		"""Return center of gravity and area."""
		subshapes_mci = [ subshape.get_mass_center_inertia(density = density,
														solid = solid)
						  for subshape in self.sub_shapes ]
		total_mass = 0
		total_center = (0, 0, 0)
		total_inertia = ((0, 0, 0), (0, 0, 0), (0, 0, 0))

		# get total mass
		for mass, center, inertia in subshapes_mci:
			total_mass += mass
		if total_mass == 0:
			return 0, (0, 0, 0), ((0, 0, 0), (0, 0, 0), (0, 0, 0))

		# get average center and inertia
		for mass, center, inertia in subshapes_mci:
			total_center = vecAdd(total_center,
								  vecscalarMul(center, mass / total_mass))
			total_inertia = matAdd(total_inertia, inertia)
		return total_mass, total_center, total_inertia

	def add_shape(self, shape, front = False):
		"""Add shape to list."""
		# check if it's already there
		if shape in self.sub_shapes: return
		# A newly initialized list shape contains its required single null ref.
		# Replace that placeholder instead of adding a second entry.
		if len(self.sub_shapes) == 1 and self.sub_shapes[0] is None:
			self.sub_shapes[0] = shape
		elif not front:
			self.sub_shapes.append(shape)
		else:
			self.sub_shapes.insert(0, shape)
			self.sub_shapes.shape = (len(self.sub_shapes),)
		self.num_sub_shapes = len(self.sub_shapes)

		n_filter = self.filters.dtype(
			self.context, self.filters.arg, self.filters.template)
		n_filter.layer = type(n_filter.layer).from_value(0)
		if front and len(self.filters):
			self.filters.insert(0, n_filter)
			self.filters.shape = (len(self.filters),)
		else:
			self.filters.append(n_filter)
		self.num_filters = len(self.filters)

	def remove_shape(self, shape):
		"""Remove a shape from the shape list."""
		# get list of shapes excluding the shape to remove
		shapes = [s for s in self.sub_shapes if s != shape]
		# set sub_shapes to this list
		self.num_sub_shapes = len(shapes)
		self.sub_shapes[:] = shapes
		self.sub_shapes.shape = (len(shapes),)
		# filter list size should match sub_shapes
		self.filters[:] = []
		self.filters.shape = (0,)
		for _ in shapes:
			n_filter = self.filters.dtype(
				self.context, self.filters.arg, self.filters.template)
			n_filter.layer = type(n_filter.layer).from_value(0)
			self.filters.append(n_filter)
		self.num_filters = len(self.filters)
