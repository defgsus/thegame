import glm


class LiveTransformation:

    """
    Transformation matrix with controls that generate slight updates over time
    """

    def __init__(self, initial_matrix=None):
        self._matrix = initial_matrix or glm.mat4(1)

        self._rotations = []
        self._translations = []

    @property
    def matrix(self):
        return self._matrix

    def init(self, initial_matrix=None):
        self._matrix = initial_matrix or glm.mat4(1)

    def transform(self, pos):
        """Transforms vec3 position to a direction matching the current transformation"""
        dir = glm.inverse(self.matrix) * glm.vec4(pos, 1)
        return glm.vec3(dir)

    def transform_direction(self, dir):
        """Transforms vec3 direction to a direction matching the current transformation"""
        dir = glm.inverse(self.matrix) * glm.vec4(dir, 0)
        return glm.vec3(dir)

    def rotate(self, axis, amount):
        if amount:
            self._rotations.append(
                {"axis": axis, "amount": amount, "t": 0.}
            )

    def rotate_x(self, amount):
        self.rotate(self.transform_direction((1, 0, 0)), amount)

    def rotate_y(self, amount):
        self.rotate(self.transform_direction((0, 1, 0)), amount)

    def rotate_z(self, amount):
        self.rotate(self.transform_direction((0, 0, 1)), amount)

    def translate(self, axis, amount):
        if amount:
            self._translations.append(
                {"axis": axis, "amount": amount, "t": 0.}
            )

    def translate_x(self, amount):
        self.translate(self.transform_direction((1, 0, 0)), amount)

    def translate_y(self, amount):
        self.translate(self.transform_direction((0, 1, 0)), amount)

    def translate_z(self, amount):
        self.translate(self.transform_direction((0, 0, 1)), amount)

    def update(self, dt):
        """Call this repeatedly with the time in seconds since last frame"""
        rotations = self._rotations
        self._rotations = []
        for i, rot in enumerate(rotations):
            # print(i, rot)
            amount = rot["amount"] * dt * .1 * glm.sin(rot["t"]*glm.pi())
            self._matrix = glm.rotate(self._matrix, amount, rot["axis"])
            rot["t"] += dt / (1. + abs(rot["amount"])) * 5.
            if rot["t"] < 0.99:
                self._rotations.append(rot)

        translations = self._translations
        self._translations = []
        for i, rot in enumerate(translations):
            # print(i, rot)
            amount = rot["amount"] * dt * .1 * glm.sin(rot["t"]*glm.pi())
            self._matrix = glm.translate(self._matrix, amount * rot["axis"])
            rot["t"] += dt / (1. + abs(rot["amount"])) * 5.
            if rot["t"] < 0.99:
                self._translations.append(rot)
