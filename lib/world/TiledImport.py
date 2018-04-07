import json


class TiledImport:

    def __init__(self):
        self.width = 0
        self.height = 0
        self.layers = []

    @property
    def num_layers(self):
        return len(self.layers)

    def load(self, filename):
        with open(filename) as fp:
            data = json.load(fp)
        self.layers = [l["data"] for l in sorted(data["layers"], key=lambda l: l["name"])]
        self.width = data["width"]
        self.height = data["height"]








if __name__ == "__main__":

    t = TiledImport()

    t.load("./assets/tiled/level01.json")