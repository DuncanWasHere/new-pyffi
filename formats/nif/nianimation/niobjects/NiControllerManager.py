class NiControllerManager:
# START_CLASS

	def add_controller_sequence(self, controller_sequence, front = False):
		"""Add NiControllerSequence to list."""
		# check if it's already there
		if controller_sequence in self.controller_sequences: return
		# increase number of controller sequences
		num_sequences = self.num_controller_sequences
		self.num_controller_sequences = num_sequences + 1
		# add the controller sequence
		if not front:
			self.controller_sequences.append(controller_sequence)
		else:
			self.controller_sequences[:] = [controller_sequence, *self.controller_sequences]
