import argparse
import importlib
import os
import time
import traceback

import pyglet

from lib.opengl.core.base import *
from lib.opengl import *

from sketches.RenderGraphWindow import RenderGraphWindow


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "module_name", type=str,
        help="Name of module where a create_render_graph method is found"
    )

    return parser.parse_args()


def import_graph_module(module_name):
    module = importlib.import_module(module_name)
    module = importlib.reload(module)

    return module


class MainWindow(RenderGraphWindow):

    def __init__(self, render_graph_module_name, **kwargs):
        # render_settings = RenderSettings(1024, 1024)

        self.render_graph_module_name = render_graph_module_name
        render_graph_module = import_graph_module(self.render_graph_module_name)
        self.render_graph_module_filename = render_graph_module.__file__
        super().__init__(render_graph_module.create_render_graph(), **kwargs)

        self._last_file_check_time = time.time()
        self._last_file_time = os.stat(self.render_graph_module_filename).st_mtime

    def update(self, dt):

        #self.render_settings.projection.rotation += .0002 * glm.sin(glm.vec3(
        #    self.render_settings.time,
        #    self.render_settings.time*1.1,
        #    self.render_settings.time*1.3,
        #))
        super().update(dt)

        cur_time = time.time()
        if cur_time - self._last_file_check_time >= 1.:
            cur_stamp = os.stat(self.render_graph_module_filename).st_mtime
            if cur_stamp != self._last_file_time:
                self._last_file_time = cur_stamp
                self._reload_module()
            self._last_file_check_time = cur_time

    def _reload_module(self):
        try:
            render_graph_module = import_graph_module(self.render_graph_module_name)
            import_graph_module(self.render_graph_module_name)
            self.set_render_graph(render_graph_module.create_render_graph())
        except BaseException as e:
            print(f"EXCEPTION in create_render_graph\n{e.__class__.__name__}: {e}\n{traceback.format_exc()}")


def run_window(render_graph_module_name):
    gl_config = pyglet.gl.Config(
        major_version=3,
        minor_version=0,
        double_buffer=True,
    )
    main_window = MainWindow(
        render_graph_module_name=render_graph_module_name,
        config=gl_config,
        resizable=True,
    )

    pyglet.app.run()


if __name__ == "__main__":
    args = parse_arguments()

    run_window(args.module_name)


