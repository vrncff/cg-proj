# janela, shaders, vbo, draw calls

import glfw
from OpenGL.GL import *
import ctypes

VERTEX_CODE = """
    attribute vec3 position;
    uniform mat4 mat_transformation;
    void main(){
        gl_Position = mat_transformation * vec4(position, 1.0);
    }
"""

FRAGMENT_CODE = """
    uniform vec4 color;
    void main(){
        gl_FragColor = color;
    }
"""

def init_window(w, h, titulo):
    glfw.init()
    glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
    win = glfw.create_window(w, h, titulo, None, None)
    if not win:
        raise RuntimeError("falha ao criar janela glfw")
    glfw.make_context_current(win)
    return win

def compile_shader(src, tipo):
    sh = glCreateShader(tipo)
    glShaderSource(sh, src)
    glCompileShader(sh)
    if not glGetShaderiv(sh, GL_COMPILE_STATUS):
        raise RuntimeError(glGetShaderInfoLog(sh).decode())
    return sh

def build_program():
    prog = glCreateProgram()
    vs = compile_shader(VERTEX_CODE,   GL_VERTEX_SHADER)
    fs = compile_shader(FRAGMENT_CODE, GL_FRAGMENT_SHADER)
    glAttachShader(prog, vs)
    glAttachShader(prog, fs)
    glLinkProgram(prog)
    if not glGetProgramiv(prog, GL_LINK_STATUS):
        raise RuntimeError(glGetProgramInfoLog(prog).decode())
    glUseProgram(prog)
    return prog

def upload_vbo(vertices):
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    return vbo

def bind_attr(prog, vertices):
    stride = vertices.strides[0]
    loc = glGetAttribLocation(prog, "position")
    glEnableVertexAttribArray(loc)
    glVertexAttribPointer(loc, 3, GL_FLOAT, False, stride, ctypes.c_void_p(0))

# desenho: cada uma manda matriz, cor e um trecho do vbo
def set_transform(loc_transf, mat):
    glUniformMatrix4fv(loc_transf, 1, GL_TRUE, mat.flatten())

def draw_triangles(loc_transf, loc_color, mat, cor, offset, count):
    set_transform(loc_transf, mat)
    glUniform4f(loc_color, *cor, 1.0)
    glDrawArrays(GL_TRIANGLES, offset, count)

def draw_strip(loc_transf, loc_color, mat, cor, offset, count):
    # faces de cubo: cada uma e um strip de 4 vertices
    set_transform(loc_transf, mat)
    glUniform4f(loc_color, *cor, 1.0)
    glDrawArrays(GL_TRIANGLE_STRIP, offset, count)

def draw_linhas(loc_transf, loc_color, mat, cor, offset, count):
    # linha aberta ligando os pontos na ordem (aba do envelope)
    set_transform(loc_transf, mat)
    glUniform4f(loc_color, *cor, 1.0)
    glDrawArrays(GL_LINE_STRIP, offset, count)
