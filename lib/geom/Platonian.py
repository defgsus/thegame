import glm


class Platonian:
    
    class Face:
        def __init__(self, positions, *index):
            self.indices = index
            self.positions = [positions[i] for i in index]

            self.center = sum(self.positions, glm.vec3(0)) / len(self.positions)

            self.i1 = index[0]
            self.i2 = index[1]
            self.i3 = index[2]
            self.i4 = index[3] if len(index) >= 4 else None
            self.i5 = index[4] if len(index) >= 5 else None

            self.p1 = positions[self.i1]
            self.p2 = positions[self.i2]
            self.p3 = positions[self.i3]
            self.p4 = positions[self.i4] if self.i4 is not None else None
            self.p5 = positions[self.i5] if self.i5 is not None else None

    def __init__(self):
        self.positions = []
        self._face_indices = []
        self._edges = None
        self._faces = None

    def _init_cube(self):
        """
          7----6
         /|   /|
        0----3 |
        | 4--|-5
        |/   |/
        1----2
        
        """
        self.positions = (
            glm.vec3(-1, -1, -1),
            glm.vec3( 1, -1, -1),
            glm.vec3( 1,  1, -1),
            glm.vec3(-1,  1, -1),
            
            glm.vec3(-1, -1, -1),
            glm.vec3( 1, -1, -1),
            glm.vec3( 1,  1, -1),
            glm.vec3(-1,  1, -1),
        )
        self._face_indices = (
            [0, 1, 2, 3],
            [2, 5, 6, 3],
            [0, 3, 6, 7],
            [1, 4, 5, 2],
            [0, 1, 4, 7],
            [6, 5, 4, 7],
        )
    
    @property
    def face_indices(self):
        return self._face_indices
    
    @property
    def edges(self):
        if self._edges is None:
            edges = set()
            for face_indices in self._face_indices:
                for i in range(len(face_indices)-1):
                    a, b = face_indices[i], face_indices[i+1]
                    if not (b, a) in edges:
                        edges.add((a, b))
            self._edges = sorted(edges)
        return self._edges

    @property
    def faces(self):
        if self._faces is None:
            self._faces = [
                self.Face(self.positions, *face_indices)
                for face_indices in self._face_indices
            ]
        return self._faces
