import pyglet
from sketches.OrthoWindow import OrthoWindow

platform = pyglet.window.get_platform()
display = platform.get_default_display()
gl_config = pyglet.gl.Config(
    major_version=3,
    minor_version=0,
    double_buffer=True,
)
main_window = OrthoWindow(config=gl_config, resizable=True)

pyglet.app.run()
