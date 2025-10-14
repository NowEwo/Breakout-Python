# type: ignore

import moderngl
import numpy as np
import pygame

from core.context import Context
from settings import *
from systems.logging import Logger


class Renderer(Context):
    def __init__(self, shader_name: str | None = None) -> None:
        self.logger = Logger("systems.renderer")
        super().__init__()
        self.shader_name = shader_name if DEBUG_ENABLED_SHADERS else ""
        self.ctx = moderngl.create_context()
        self.setup_shaders()
        self.logger.success(f"Renderer instance {self} initialised")

    def setup_shaders(self):
        """Initialize OpenGL shaders"""
        if self.shader_name:
            with open(f"shaders/{self.shader_name}.glsl") as f:
                frag_shader_src = f.read()
        else:
            frag_shader_src = """
            #version 330 core
            
            uniform sampler2D iChannel0;
            uniform vec2 iResolution;
            uniform float warp;
            uniform float scan;
            
            in vec2 v_texcoord;
            out vec4 fragColor;
            
            void main() {
                fragColor = texture(iChannel0, v_texcoord);
            }
            """

        vertex_shader_src = """
        #version 330 core
        
        in vec2 in_vert;
        out vec2 v_texcoord;
        
        void main() {
            v_texcoord = (in_vert + 1.0) / 2.0;
            gl_Position = vec4(in_vert, 0.0, 1.0);
        }
        """

        self.prog = self.ctx.program(
            vertex_shader=vertex_shader_src,
            fragment_shader=frag_shader_src
        )

        vertices = np.array([
            -1.0, -1.0,
            1.0, -1.0,
            -1.0, 1.0,
            1.0, 1.0,
        ], dtype="f4")

        vbo = self.ctx.buffer(vertices.tobytes())
        self.vao = self.ctx.simple_vertex_array(self.prog, vbo, "in_vert")

        self.texture = self.ctx.texture((RENDER_WIDTH, RENDER_HEIGHT), 3)
        self.texture.repeat_x = False
        self.texture.repeat_y = False

        if "warp" in self.prog:
            self.prog["warp"].value = 0.0
        if "scan" in self.prog:
            self.prog["scan"].value = 0.1

        self.logger.success("Shaders initialised")

    def set_curvature(self, curvature: float):
        self.logger.log(f"Screen curvature change requested to {curvature}")
        if "warp" in self.prog:
            self.prog["warp"].value = curvature

    def render_frame(self):
        flipped = pygame.transform.flip(self.game.window, False, True)
        texture_data = pygame.image.tostring(flipped, "RGB")

        self.texture.write(texture_data)
        self.texture.use(0)

        if "iResolution" in self.prog:
            self.prog["iResolution"].value = (RENDER_WIDTH, RENDER_HEIGHT)

        if "iChannel0" in self.prog:
            self.prog["iChannel0"].value = 0

        if "warp" in self.prog:
            current_warp = self.prog["warp"].value
            if current_warp < 0.5:
                self.prog["warp"].value = current_warp + 0.01

        if "scan" in self.prog:
            self.prog["scan"].value = 0.1

        self.ctx.clear(0.0, 0.0, 0.0)
        self.vao.render(moderngl.TRIANGLE_STRIP)
