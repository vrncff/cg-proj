# rato montado com primitivas, a partir de uma referencia feita no blender
# chamadas de gen_grupos_rato() e draw_rato()

import math
from geometria import gen_esfera, gen_cilindro, gen_pera
from transformacoes import mat_translacao, mat_escala, mat_rotacao_x, mat_rotacao_y, mat_rotacao_z, compor

PI = math.pi

# corpo e cabeca sao 'peras' quanto menor o fator, mais fina a ponta
# o corpo afina pra cima, a cabeca pra frente no focinho
PERA_CORPO  = 0.60
PERA_CABECA = 0.55

# uma cor por parte
PELO     = (0.62, 0.55, 0.50)
PELE     = (0.90, 0.66, 0.66)
PELE_ESC = (0.78, 0.48, 0.50)
PRETO    = (0.08, 0.07, 0.07)

# cada parte (tipo, posicao, rotacao em graus, raio por eixo, cor)
# vem da referencia do blender
PARTES = [
    # corpo e cabeca
    ("pera_corpo",  ( 0.00,  0.00,  0.000), ( -18,   0,    0), (0.755, 0.755, 1.000), PELO),
    ("pera_cabeca", ( 0.00,  0.72,  1.100), (   0,   0,    0), (0.545, 0.675, 0.486), PELO),

    # pernas e pes
    ("esfera",   ( 0.35, -0.28, -0.500), (   0,    0,    0), (0.419, 0.419, 0.419), PELO),
    ("esfera",   (-0.35, -0.28, -0.500), (   0,    0,    0), (0.419, 0.419, 0.419), PELO),
    ("esfera",   ( 0.57, -0.06, -0.900), (   0,    0,    0), (0.090, 0.367, 0.090), PELE),
    ("esfera",   (-0.57, -0.06, -0.900), (   0,    0,    0), (0.090, 0.367, 0.090), PELE),

    # bracos
    ("esfera",   ( 0.36,  0.61,  0.140), ( -39, -2.5,  8.1), (0.080, 0.240, 0.080), PELO),
    ("esfera",   (-0.36,  0.61,  0.140), ( -39, -2.5,  8.1), (0.080, 0.240, 0.080), PELO),

    # orelhas: circulo de fora e circulo de dentro, ligeiramente menor
    # encostadas na cabeca, com a base um pouco afundada nela
    ("cilindro", ( 0.40,  0.11,  1.420), (   6,  105,   25), (0.450, 0.450, 0.030), PELO),
    ("cilindro", (-0.40,  0.11,  1.420), (   6, -105,  -25), (0.450, 0.450, 0.030), PELO),
    ("cilindro", ( 0.43,  0.11,  1.420), (   6,  105,   25), (0.360, 0.360, 0.030), PELE),
    ("cilindro", (-0.43,  0.11,  1.420), (   6, -105,  -25), (0.360, 0.360, 0.030), PELE),

    # rosto: olhos levemente pra fora
    ("esfera",   ( 0.00,  1.35,  1.223), (   0,    0,    0), (0.056, 0.056, 0.056), PELE_ESC),
    ("esfera",   ( 0.55,  0.61,  1.260), (   0,    0,    0), (0.110, 0.110, 0.110), PRETO),
    ("esfera",   (-0.55,  0.61,  1.260), (   0,    0,    0), (0.110, 0.110, 0.110), PRETO),

    # rabo: dois cilindros deformados e emendados grosseiramente
    ("cilindro", ( 0.00, -0.94,  0.068), (  30,    0,    0), (0.030, 0.080, 0.650), PELE),
    ("cilindro", ( 0.00, -1.20,  0.980), ( -10,    0,    0), (0.030, 0.080, 0.400), PELE),
]

def gen_grupos_rato(sectors=12, stacks=12):
    # nome do grupo igual a PARTES
    return [
        ("esfera", gen_esfera(r=1.0, sectors=sectors, stacks=stacks)),
        ("cilindro", gen_cilindro(r=1.0, h=2.0, sectors=sectors, stacks=1)[0]),
        ("pera_corpo", gen_pera(r=1.0, sectors=sectors, stacks=stacks,
                                topo=PERA_CORPO,  eixo="z")),
        ("pera_cabeca", gen_pera(r=1.0, sectors=sectors, stacks=stacks,
                                 topo=PERA_CABECA, eixo="y")),
    ]

def mat_base_rato(tx, ty, tz, escala, giro, ang_x=0.0, ang_y=0.0):
    # ajuste do rato para a cena

    return compor(
        mat_translacao(tx, ty, tz),
        mat_rotacao_y(ang_y), # inclinacao global da cena
        mat_rotacao_x(ang_x),
        mat_escala(escala, escala, escala),
        mat_rotacao_y(giro), # quanto que rato rotacionara no eixo y
        mat_rotacao_x(-PI / 2), # blender e z-up, opengl y-up
    )

def partes_rato(mat_base):
    # retorna [(grupo, matriz, cor)] de cada primitiva posicionada
    saida = []

    for tipo, loc, rot, esc, cor in PARTES:
        # posiciona a parte do rato (rotacao em x, y, z nessa ordem)
        mat = compor(
            mat_base,
            mat_translacao(*loc),
            mat_rotacao_x(math.radians(rot[0])),
            mat_rotacao_y(math.radians(rot[1])),
            mat_rotacao_z(math.radians(rot[2])),
            mat_escala(*esc),
        )

        if tipo == "cilindro":
            # translada cilindro para encaixe adequado (falta compatibilidade dos dados do blender)
            mat = compor(mat, mat_translacao(0.0, 0.0, -1.0))

        saida.append((tipo, mat, cor))
    return saida

def draw_rato(draw_triangles, loc_transf, loc_color, off, mat_base):
    # desenha o rato inteiro, off sendo o dict de offsets para vbo
    for grupo, mat, cor in partes_rato(mat_base):
        o, c = off["rato/" + grupo]
        draw_triangles(loc_transf, loc_color, mat, cor, o, c)

    return
