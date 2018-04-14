import pyglet

#from sketches.OrthoWindow import OrthoWindow as MainWindow
#from sketches.ChunkWindow import ChunkWindow as MainWindow
#from sketches.ProjectionWindow import ProjectionWindow as MainWindow
from sketches.WorldWindow import WorldWindow as MainWindow


platform = pyglet.window.get_platform()
display = platform.get_default_display()
gl_config = pyglet.gl.Config(
    major_version=3,
    minor_version=0,
    double_buffer=True,
)
main_window = MainWindow(config=gl_config, resizable=True)

pyglet.app.run()
