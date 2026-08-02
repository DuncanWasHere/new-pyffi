# START_GLOBALS
from generated.formats.nif.imports import name_type_map
# END_GLOBALS


class BoneData:
# START_CLASS
	def get_transform(self):
		"""Return scale, rotation, and translation into a single 4x4 matrix."""
		return self.skin_transform.get_transform()

	def set_transform(self, mat):
		"""Set rotation, transform, and velocity."""
		self.skin_transform.set_transform(mat)

	def update_center_radius(self, vertices):
		"""Update the bounding sphere from the vertices this bone influences."""
		boneverts = [vertices[skinweight.index] for skinweight in self.vertex_weights]
		if not boneverts:
			return

		# bounding box of the influenced vertices
		low = name_type_map['Vector3'](self.context)
		low.x = min(v.x for v in boneverts)
		low.y = min(v.y for v in boneverts)
		low.z = min(v.z for v in boneverts)

		high = name_type_map['Vector3'](self.context)
		high.x = max(v.x for v in boneverts)
		high.y = max(v.y for v in boneverts)
		high.z = max(v.z for v in boneverts)

		center = (low + high) * 0.5

		# the radius is the largest distance from that centre
		r2 = 0.0
		for v in boneverts:
			d = center - v
			r2 = max(r2, d.x * d.x + d.y * d.y + d.z * d.z)
		radius = r2 ** 0.5

		# the centre is stored in bone space, the radius is unaffected by it
		center *= self.get_transform()

		self.bounding_sphere.center.x = center.x
		self.bounding_sphere.center.y = center.y
		self.bounding_sphere.center.z = center.z
		self.bounding_sphere.radius = radius
