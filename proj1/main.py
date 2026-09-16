# Cena: mesa, monitor crt com cursor e icones na tela, rato na frente, relogio na parede
# Controles: 
# p exibe malha poligonal
# a/s giram o rato 
# setas movem o cursor 
# j/k escalam o monitor inteiro
import glfw
from OpenGL.GL import *
import numpy as np
import math

from transformacoes import mat_translacao, mat_escala, mat_rotacao_x, mat_rotacao_y, compor
from gl_utils import init_window, build_program, upload_vbo, bind_attr, draw_triangles

import objetos
from objetos import grupos_cena
from rato import mat_base_rato, draw_rato

PI = math.pi

# inclinacao global p/ nocao de 3d sem mexer a camera
ANG_Y = 0.18
ANG_X = -0.15

# posicao de objetos na cena
MON_TX,  MON_TY  = 0.10, -0.065 # monitor
REL_TX,  REL_TY  = -0.65,  0.55 # relogio
MESA_TOPO, MESA_ALT = -0.55, 0.47 # mesa

# vbo e desenho
def empacotar(listas):
    # toma lista de vertices
    # retorna: (array, [(offset, count)])
    info = []
    all_verts = []
    offset = 0

    for vlist in listas:
        count = len(vlist)
        info.append((offset, count))
        all_verts.extend(vlist)
        offset += count

    arr = np.zeros(len(all_verts), [("position", np.float32, 3)])
    arr["position"] = np.array(all_verts, dtype=np.float32)

    return arr, info

def desenhar(pecas, base, off, loc_transf, loc_color):
    # peca = (grupo, matriz local, cor, como desenhar)
    # base translada objeto inteiro
    for grupo, mat_local, cor, draw in pecas:
        o, c = off[grupo]
        draw(loc_transf, loc_color, compor(base, mat_local), cor, o, c)

    return

# bases: posicionam o objeto na cena
def base_monitor(zoom, apoio_y):
    # o zoom escala em torno da origem local, a base do monitor desce
    # a correcao em y mantem a calota colada no tampo da mesa
    return compor(
        mat_translacao(MON_TX, MON_TY + apoio_y * math.cos(ANG_X) * (1 - zoom), 0.0),
        mat_rotacao_y(ANG_Y),
        mat_rotacao_x(ANG_X),
        mat_escala(zoom, zoom, zoom),
    )

def base_relogio():
    return compor(mat_translacao(REL_TX, REL_TY, 0.0),
                  mat_rotacao_y(ANG_Y), mat_rotacao_x(ANG_X))

def base_mesa():
    return compor(mat_translacao(0.0, MESA_TOPO - MESA_ALT / 2, 0.0),
                  mat_rotacao_y(ANG_Y), mat_rotacao_x(ANG_X))

def main():
    win = init_window(800, 700, "prototipo da cena")
    prog = build_program()

    grupos = grupos_cena()
    vertices, info = empacotar([v for _, v in grupos])
    off = {chave: info[i] for i, (chave, _) in enumerate(grupos)} # "obj/grupo" -> (offset, count)
    geo = dict(grupos) # "obj/grupo" -> vertices

    upload_vbo(vertices)
    bind_attr(prog, vertices)
    loc_transf = glGetUniformLocation(prog, "mat_transformation")
    loc_color  = glGetUniformLocation(prog, "color")

    # fixo de frame em frame
    pecas_mesa = objetos.monta_mesa()
    pecas_monitor, apoio_y = objetos.monta_monitor()
    pecas_tela = objetos.monta_tela()
    pecas_relogio = objetos.monta_relogio()
    mat_mesa, mat_relogio = base_mesa(), base_relogio()

    # forma e limites da seta atualizam
    CURSOR_ESC = 0.070
    seta, seta_borda, cur_lo, cur_hi = objetos.seta_ancorada(geo)
    cur_x0, cur_x1 = -objetos.TELA_MEIA_W - cur_lo[0] * CURSOR_ESC, objetos.TELA_MEIA_W - cur_hi[0] * CURSOR_ESC
    cur_y0, cur_y1 = -objetos.TELA_MEIA_H - cur_lo[1] * CURSOR_ESC, objetos.TELA_MEIA_H - cur_hi[1] * CURSOR_ESC

    # estado
    wireframe = False
    rato_giro = PI * 0.9               # a/s
    cursor_x, cursor_y = -0.12, 0.02   # ponta da seta (tela)
    mon_zoom = 1.0

    RATO_PASSO, CURSOR_PASSO, MON_PASSO = 0.030, 0.007, 0.004 # passo das transformacoes
    MON_MIN, MON_MAX = 0.8, 1.3 # extremos de escala
    RATO_TX, RATO_TY, RATO_TZ, RATO_ESC = -0.38, -0.48, -0.68, 0.18

    # wireframe vem por evento
    def key_event(window, key, scancode, action, mods):
        nonlocal wireframe
        if action == glfw.PRESS and key == glfw.KEY_P:
            wireframe = not wireframe

    glfw.set_key_callback(win, key_event)
    glfw.show_window(win)
    glEnable(GL_DEPTH_TEST)
    glLineWidth(2.0) # torna aba da carta mais visivel
    glfw.swap_interval(1)

    while not glfw.window_should_close(win):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.18, 0.16, 0.14, 1.0) # fundo escuro (parede)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if wireframe else GL_FILL)

        # qualquer combinacao de teclas vale para transformacoes
        if glfw.get_key(win, glfw.KEY_LEFT)  == glfw.PRESS: cursor_x -= CURSOR_PASSO
        if glfw.get_key(win, glfw.KEY_RIGHT) == glfw.PRESS: cursor_x += CURSOR_PASSO
        if glfw.get_key(win, glfw.KEY_DOWN)  == glfw.PRESS: cursor_y -= CURSOR_PASSO
        if glfw.get_key(win, glfw.KEY_UP)    == glfw.PRESS: cursor_y += CURSOR_PASSO
        if glfw.get_key(win, glfw.KEY_A)     == glfw.PRESS: rato_giro -= RATO_PASSO
        if glfw.get_key(win, glfw.KEY_S)     == glfw.PRESS: rato_giro += RATO_PASSO
        if glfw.get_key(win, glfw.KEY_J)     == glfw.PRESS: mon_zoom  -= MON_PASSO
        if glfw.get_key(win, glfw.KEY_K)     == glfw.PRESS: mon_zoom  += MON_PASSO

        # seta presa na tela
        cursor_x = min(max(cursor_x, cur_x0), cur_x1)
        cursor_y = min(max(cursor_y, cur_y0), cur_y1)

        # monitor preso a escala
        mon_zoom = min(max(mon_zoom, MON_MIN), MON_MAX)

        # desenhar e posicionar
        mat_monitor = base_monitor(mon_zoom, apoio_y)

        desenhar(pecas_mesa, mat_mesa, off, loc_transf, loc_color)

        desenhar(pecas_monitor, mat_monitor, off, loc_transf, loc_color)
        desenhar(pecas_tela, mat_monitor, off, loc_transf, loc_color)
        desenhar(objetos.monta_cursor(seta, seta_borda, cursor_x, cursor_y, CURSOR_ESC),
                 mat_monitor, off, loc_transf, loc_color)

        desenhar(pecas_relogio, mat_relogio, off, loc_transf, loc_color)
        desenhar(objetos.monta_ponteiros(glfw.get_time()), mat_relogio, off, loc_transf, loc_color)

        # o rato tem modulo proprio (import)
        draw_rato(draw_triangles, loc_transf, loc_color, off, 
                  mat_base_rato(RATO_TX, RATO_TY, RATO_TZ, RATO_ESC, rato_giro, ANG_X, ANG_Y))

        glfw.swap_buffers(win)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
