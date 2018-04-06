import glm


class Projection:

    P_ORTHO = "o"
    P_PERSPECTIVE = "p"

    def __init__(self, width, height, projection=P_ORTHO):
        self.projection = self.P_ORTHO
        self.width = width
        self.height = height

    def get_matrix(self):
        glm.perspective(30, self.width / self.height, 0.01, )


