# tudo sobre cada objeto: que vertices tem (geometria) e onde/de que cor cada parte fica.
# a matriz base, montada no main.py, monta a cena globalmente

import math
import numpy as np

import geometria as geo
import rato
from transformacoes import mat_translacao, mat_escala, mat_rotacao_x, mat_rotacao_z, compor
from gl_utils import draw_triangles, draw_strip, draw_linhas


# Propriedades
# para montagem e padronização dos objetos

PI = math.pi
FACES = ["frente", "direita", "tras", "esquerda", "baixo", "cima"]

# conteudo da tela depende de propriedades do monitor
MON_SX, MON_SY, MON_SZ = 0.80, 0.76, 0.75
TELA_MARGEM = 0.08    # moldura entre a borda da carcaca e a tela
TELA_SAIDA  = 0.03    # quanto a tela sobressai da face frontal

# meia largura/altura da area util da tela
TELA_MEIA_W = (1 - 2 * TELA_MARGEM) * MON_SX / 2
TELA_MEIA_H = (1 - 2 * TELA_MARGEM) * MON_SY / 2

# camadas em z para definir sobreposicao no monitor
DZ          = 0.002
Z_MOLDURA   = -0.5 * MON_SZ                    # face frontal da carcaca
Z_BOTAO     = Z_MOLDURA - DZ                   # botoes, a frente dela
Z_TELA      = (-0.5 - TELA_SAIDA) * MON_SZ     # face frontal da tela
Z_ICONE     = Z_TELA - 2 * DZ                  # icones e barra de tarefas
Z_DETALHE   = Z_ICONE - DZ                     # aba da carta, furo do cd
Z_CUR_BORDA = Z_ICONE - 2 * DZ                 # borda da seta
Z_CURSOR    = Z_ICONE - 3 * DZ                 # seta, por cima de tudo

COR_TELA = (0.05, 0.08, 0.05)   # cubo da tela e furo do cd

# relogio
REL_FACE_SAIDA = 0.01   # quanto a face branca sobressai da carcaca
REL_VOLTA_MIN  = 6.0    # segundos por volta do ponteiro de minuto

# Geometria 
# quais vertices existem e sob que nome
def cubo_por_face(prefixo=""):
    # gen_cubo devolve 24 verts = 6 strips de 4
    v = geo.gen_cubo()

    return [(prefixo + FACES[f], v[f*4:f*4+4]) for f in range(6)]

def cilindro_por_parte(r, h, sectors, stacks):
    verts, n_corpo, n_tbase, n_ttopo = geo.gen_cilindro(r=r, h=h, sectors=sectors, stacks=stacks)
    corpo = verts[:n_corpo]
    tbase = verts[n_corpo:n_corpo + n_tbase]
    ttopo = verts[n_corpo + n_tbase:]

    return [("corpo", corpo), ("tampa_base", tbase), ("tampa_topo", ttopo)]

def grupos_monitor():
    # carcaca (cubo) + tela (cubo menor) + pescoco (cilindro) + calota (esfera)
    grupos = cubo_por_face("carcaca_") + cubo_por_face("tela_")
    verts_pescoco, _, _, _ = geo.gen_cilindro(r=0.5, h=1.0, sectors=16, stacks=1)

    # esfera bem achatada
    verts_calota = geo.gen_esfera(r=0.5, sectors=16, stacks=6)
    grupos.append(("pescoco", verts_pescoco))
    grupos.append(("calota", verts_calota))

    # triangulos e um circulo (botoes da moldura)
    grupos.append(("botao_tri", geo.gen_triangulo_2d(base=1.0, altura=1.0)))
    grupos.append(("botao_circulo", geo.gen_circulo_2d(r=0.5, sectors=12)))
    return grupos

def grupos_relogio():
    # carcaca em 3 partes, a face branca reutiliza os mesmos grupos com outra matriz
    return cilindro_por_parte(r=0.5, h=0.12, sectors=30, stacks=1)

def grupos_ponteiro():
    # um grupo por ponteiro, com o tamanho ja definido
    rel_r = 0.30
    pont_base_larg, pont_base_comp = 0.04, 0.45    # retangulo cru do gen_ponteiro
    pont_hora_larg, pont_hora_comp = 0.85, 0.55    # ponteiro de hora
    pont_min_larg,  pont_min_comp  = 0.62, 0.80    # ponteiro de minuto

    verts_hora = geo.gen_ponteiro(largura=pont_base_larg * pont_hora_larg * rel_r,
                                  comprimento=pont_base_comp * pont_hora_comp * rel_r)

    verts_minuto = geo.gen_ponteiro(largura=pont_base_larg * pont_min_larg * rel_r,
                                    comprimento=pont_base_comp * pont_min_comp * rel_r)

    return [("hora", verts_hora), ("minuto", verts_minuto)]

def grupos_cursor():
    # um triangulo (copia inflada por tras forma borda escura)
    return [("triangulo", geo.gen_triangulo_2d(base=1.0, altura=1.0))]

def grupos_cd():
    # um circulo (repetido, o menor faz o furo no meio)
    return [("circulo", geo.gen_circulo_2d(r=0.5, sectors=20))]

def grupos_barra():
    # 'barra de tarefas' um retangulo
    return [("retangulo", geo.gen_quadrado_2d(w=1.0, h=1.0))]

def grupos_pasta():
    # um retangulo (duas vezes, corpo e lingueta)
    return [("retangulo", geo.gen_quadrado_2d(w=1.0, h=1.0))]

def grupos_carta():
    # retangulo (corpo) + duas linhas (aba)
    return [("corpo", geo.gen_quadrado_2d(w=1.0, h=1.0)),
            ("aba",   geo.gen_aba_carta(w=1.0, h=1.0, fundo=0.0))]

def grupos_mesa():
    # cubo unico
    return cubo_por_face()

def grupos_cena():
    # todos grupos. chave "objeto/grupo" para uso do main.py
    objetos = [
        ("monitor",  grupos_monitor()),
        ("relogio",  grupos_relogio()),
        ("ponteiro", grupos_ponteiro()),
        ("rato",     rato.gen_grupos_rato()),
        ("cursor",   grupos_cursor()),
        ("carta",    grupos_carta()),
        ("cd",       grupos_cd()),
        ("pasta",    grupos_pasta()),
        ("barra",    grupos_barra()),
        ("mesa",     grupos_mesa()),
    ]

    return [(nome + "/" + g, verts) for nome, grupos in objetos for g, verts in grupos]

def cores_cubo(frontal, lateral, topo):
    # cores das faces na ordem FACES, notar que 'tras' esta virada para camera
    # repetindo cores de faces opostas (nao aparecem na cena)
    return [frontal, lateral, frontal, lateral, topo, topo]

def pontos_2d(verts, mat):
    # vertices ja transformados, x e y
    v = np.array(verts, dtype=np.float64)

    return (mat @ np.hstack([v, np.ones((len(v), 1))]).T).T[:, :2]

# Montagem dos objetos
# cores e transformacoes previas

def monta_mesa():
    # cubo unico com tons diferentes por face (ilusao de volume sem iluminacao)
    mat = mat_escala(2.2, 0.47, 1.5)
    return [("mesa/" + f, mat, cor, draw_strip)
            for f, cor in zip(FACES, cores_cubo((0.40, 0.26, 0.14),    # frontal
                                                (0.42, 0.28, 0.16),    # lateral
                                                (0.62, 0.44, 0.26)))]  # tampo

def monta_monitor():
    # carcaca + tela + pescoco + base (calota) + botoes
    # retorna apoio_y, base da calota, a ser preservada pelo zoom
    pescoco_r, pescoco_h = 0.12, 0.05
    calota_rx, calota_ry, calota_rz = 0.45, 0.07, 0.40
    cores_carcaca = cores_cubo((0.55, 0.53, 0.50),    # frontal
                               (0.50, 0.48, 0.44),    # lateral
                               (0.92, 0.90, 0.86))    # topo

    carcaca_base_y = -MON_SY / 2
    pescoco_bot_y  = carcaca_base_y - pescoco_h
    calota_y       = pescoco_bot_y
    apoio_y        = calota_y - calota_ry / 2

    mat_carcaca = mat_escala(MON_SX, MON_SY, MON_SZ)

    mat_pescoco = compor(mat_translacao(0.0, pescoco_bot_y, 0.0),
                         mat_rotacao_x(-PI / 2), # colocar cilindro em pe
                         mat_escala(pescoco_r, pescoco_r, pescoco_h))

    mat_calota  = compor(mat_translacao(0.0, calota_y, 0.0),
                         mat_escala(calota_rx, calota_ry, calota_rz))

    mat_tela    = compor(mat_translacao(0.0, 0.0, (-0.5 - TELA_SAIDA / 2) * MON_SZ),
                         mat_escala(2 * TELA_MEIA_W, 2 * TELA_MEIA_H, TELA_SAIDA * MON_SZ))

    # botoes na moldura (canto inferior direito)
    bot_w, bot_h, bot_d = 0.030, 0.026, 0.030
    bot_x0, bot_dx = 0.23, 0.06
    bot_y = (carcaca_base_y - TELA_MEIA_H) / 2 # meio da faixa da moldura

    centra = mat_translacao(0.0, -0.5, 0.0) # gen_triangulo_2d vai de y=0 a 1

    mat_bot_cima  = compor(mat_translacao(bot_x0, bot_y, Z_BOTAO), # seta /\
                           mat_escala(bot_w, bot_h, 1.0), centra)
    mat_bot_baixo = compor(mat_translacao(bot_x0 + bot_dx, bot_y, Z_BOTAO), # seta \/
                           mat_rotacao_z(PI), mat_escala(bot_w, bot_h, 1.0), centra)

    mat_bot_circulo = compor(mat_translacao(bot_x0 + 2 * bot_dx, bot_y, Z_BOTAO), # circulo
                           mat_escala(bot_d, bot_d, 1.0))

    pecas = [("monitor/carcaca_" + f, mat_carcaca, cor, draw_strip)
             for f, cor in zip(FACES, cores_carcaca)]

    pecas += [("monitor/tela_" + f, mat_tela, COR_TELA, draw_strip) for f in FACES]

    pecas += [
        ("monitor/pescoco",     mat_pescoco,   (0.70, 0.68, 0.64), draw_triangles),
        ("monitor/botao_tri",   mat_bot_cima,  (0.34, 0.33, 0.31), draw_triangles),
        ("monitor/botao_tri",   mat_bot_baixo, (0.34, 0.33, 0.31), draw_triangles),
        ("monitor/botao_circulo", mat_bot_circulo, (0.34, 0.33, 0.31), draw_triangles),
        ("monitor/calota",      mat_calota,    (0.72, 0.70, 0.66), draw_triangles),
    ]

    return pecas, apoio_y

def monta_tela():
    # objetos da tela: barra, carta, pasta, cd, acompanhando o monitor

    # barra de tarefas
    barra_h = 0.050
    mat_barra = compor(mat_translacao(0.0, -TELA_MEIA_H + barra_h / 2, Z_ICONE),
                       mat_escala(2 * TELA_MEIA_W, barra_h, 1.0))

    # carta: retangulo + aba em V
    ctx, cty, cw, ch = -0.22, 0.07, 0.17, 0.115
    mat_carta     = compor(mat_translacao(ctx, cty, Z_ICONE),   mat_escala(cw, ch, 1.0))
    mat_carta_aba = compor(mat_translacao(ctx, cty, Z_DETALHE), mat_escala(cw, ch, 1.0))

    # pasta: lingueta encosta no corpo
    ptx, pty = -0.22, 0.225
    mat_pasta_corpo = compor(mat_translacao(ptx, pty - 0.012, Z_ICONE),
                             mat_escala(0.160, 0.105, 1.0))
    mat_pasta_ling  = compor(mat_translacao(ptx - 0.0475, pty + 0.0555, Z_ICONE),
                             mat_escala(0.065, 0.030, 1.0))

    # cd: o mesmo circulo duas vezes, um fazendo o furo
    dtx, dty, dd = 0.24, -0.16, 0.135
    mat_cd      = compor(mat_translacao(dtx, dty, Z_ICONE),   mat_escala(dd, dd, 1.0))
    mat_cd_furo = compor(mat_translacao(dtx, dty, Z_DETALHE),
                         mat_escala(dd * 0.26, dd * 0.26, 1.0))
    return [
        ("barra/retangulo", mat_barra, (0.20, 0.32, 0.62), draw_triangles),
        ("carta/corpo", mat_carta, (0.94, 0.93, 0.88), draw_triangles),
        ("carta/aba", mat_carta_aba, (0.30, 0.28, 0.26), draw_linhas),
        ("pasta/retangulo", mat_pasta_ling, (0.72, 0.56, 0.20), draw_triangles),
        ("pasta/retangulo", mat_pasta_corpo, (0.88, 0.70, 0.28), draw_triangles),
        ("cd/circulo", mat_cd, (0.74, 0.80, 0.88), draw_triangles),
        ("cd/circulo", mat_cd_furo, COR_TELA, draw_triangles),
    ]

def seta_ancorada(geo):
    # seta ancorada na ponta (ponta na origem), mais borda
    forma = compor(mat_rotacao_z(PI / 8),
                   mat_escala(0.70, 1.30, 1.0))

    # borda: mesmo triangulo em torno do centroide (y=1/3)
    borda = compor(forma, mat_translacao(0.0, 1 / 3, 0.0),
                   mat_escala(1.18, 1.18, 1.0), mat_translacao(0.0, -1 / 3, 0.0))

    p = pontos_2d(geo["cursor/triangulo"], borda)

    ponta = p[p[:, 1].argmax()] # vertice mais alto
    volta = mat_translacao(-ponta[0], -ponta[1], 0.0)

    forma, borda = compor(volta, forma), compor(volta, borda)
    q = pontos_2d(geo["cursor/triangulo"], borda)

    return forma, borda, q.min(0), q.max(0)

def monta_cursor(forma, borda, x, y, esc):
    # borda escura atras, seta clara na frente
    pos = compor(mat_translacao(x, y, 0.0), mat_escala(esc, esc, 1.0))

    return [
        ("cursor/triangulo", compor(mat_translacao(0, 0, Z_CUR_BORDA), pos, borda),
         (0.10, 0.10, 0.12), draw_triangles),
        ("cursor/triangulo", compor(mat_translacao(0, 0, Z_CURSOR), pos, forma),
         (0.96, 0.96, 0.94), draw_triangles),
    ]

def monta_relogio():
    # a face branca reusa os mesmos grupos da carcaca, em escala menor e por cima
    rel_r, rel_d = 0.30, 1.00
    face_r = rel_r - 0.06

    mat_carcaca = mat_escala(rel_r, rel_r, rel_d)
    mat_face    = compor(mat_translacao(0.0, 0.0, -REL_FACE_SAIDA),
                         mat_escala(face_r, face_r, rel_d * 0.3))

    # a tampa de tras nunca aparece
    partes = [("corpo", (0.50, 0.46, 0.40)),        # lateral, mais escura
              ("tampa_base", (0.62, 0.58, 0.52)),   # anel ao redor da face
              ("tampa_topo", (0.50, 0.46, 0.40))]   # escondida

    pecas = [("relogio/" + n, mat_carcaca, cor, draw_triangles) for n, cor in partes]
    pecas += [("relogio/" + n, mat_face, (0.95, 0.93, 0.90), draw_triangles)
              for n, _ in partes]

    return pecas

def monta_ponteiros(t):
    # velocidade cte, minuto 12x mais rapido que hora
    ang_min  = -2 * PI * t / REL_VOLTA_MIN
    ang_hora = ang_min / 12

    z = -REL_FACE_SAIDA - 0.005    # ligeiramente a frente da face

    cor = (0.15, 0.12, 0.10)

    return [(g, compor(mat_translacao(0.0, 0.0, z), mat_rotacao_z(a)), cor, draw_triangles)
            for g, a in [("ponteiro/hora", ang_hora), ("ponteiro/minuto", ang_min)]]
