import numpy as np
import moderngl

import pygame

from components.logging import Logger

class ShaderEngine:
    def __init__(self, engine) -> None:
        self.engine = engine

        self.logger = Logger("components.shaders")

        self.ctx = moderngl.create_context()
        self.setup_shaders()

    def setup_shaders(self):
        """Initialize OpenGL shaders"""

        self.logger.log("Initialising OpenGL shaders ...")

        with open("shaders/crt.glsl") as f:
            frag_shader_src = f.read()
        
        vertex_shader_src = """
        #version 120
        attribute vec2 in_vert;
        varying vec2 v_text;
        void main() {
            v_text = (in_vert + 1.0) / 2.0;
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
            -1.0,  1.0,
             1.0,  1.0,
        ], dtype="f4")
        
        vbo = self.ctx.buffer(vertices.tobytes())
        self.vao = self.ctx.simple_vertex_array(self.prog, vbo, "in_vert")
        
        self.texture = self.ctx.texture((self.engine.width, self.engine.height), 3)
        self.texture.repeat_x = False
        self.texture.repeat_y = False

        self.logger.success("Shaders initialised")
    
    def set_curvature(self, curvature: float):
        self.logger.success(f"Shader's curvature set to {curvature}")
        self.prog["warp"].value = curvature # type: ignore
    
    def render_frame(self):
        flipped = pygame.transform.flip(self.engine.screen, False, True)
        texture_data = pygame.image.tostring(flipped, "RGB")
        self.texture.write(texture_data)
        self.texture.use(0)
        
        self.prog["iResolution"].value = (self.engine.width, self.engine.height) # type: ignore
        if self.engine.started and self.prog["warp"].value < 0.5: # type: ignore
            self.prog["warp"].value += 0.01 # type: ignore
        self.prog["scan"].value = 0.1 # type: ignore
        self.prog["iChannel0"].value = 0 # type: ignore
        
        self.ctx.clear(0.0, 0.0, 0.0)
        self.vao.render(moderngl.TRIANGLE_STRIP)