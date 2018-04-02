
a=0

"""
+----+
|****|
|*   |
|*  *|
+----+

"""

class Templates:
    
    TOP = 0
    LEFT = 1
    BOTTOM = 2
    RIGHT = 3
    TOP_LEFT = 4
    BOTTOM_LEFT = 5
    BOTTOM_RIGHT = 6
    TOP_RIGHT = 7
    
    def iter(self):
        return range(256)

    def get_features(self, idx):
        return [(idx >> i) & 1 for i in range(8)]

    def as_ascii(self, idx):
        f = self.get_features(idx)
        s = "+----+\n"
        s += "|"
        s += "*" if f[self.TOP_LEFT] else " "
        s += "**" if f[self.TOP] else "  "
        s += "*" if f[self.TOP_RIGHT] else " "
        s += "|\n|"
        s += "*" if f[self.LEFT] else " "
        s += "  "
        s += "*" if f[self.RIGHT] else " "
        s += "|\n|"
        s += "*" if f[self.BOTTOM_LEFT] else " "
        s += "**" if f[self.BOTTOM] else "  "
        s += "*" if f[self.BOTTOM_RIGHT] else " "
        s += "|\n+----+"
        return s

    def dump_all(self):
        for j in range(16):
            lines = [[] for x in range(16)]
            for i in range(16):
                idx = j*16+i
                lines[i].append("%6s" % idx)
                for s in self.as_ascii(idx).split("\n"):
                    lines[i].append(s)
            for y in range(len(lines[0])):
                print(" ".join(lines[x][y] for x in range(len(lines))))



if __name__ == "__main__":
    tmpl = Templates()
    tmpl.dump_all()


