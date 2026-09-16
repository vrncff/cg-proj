# primitivas: geram listas de vertices (tuplas x,y,z) prontas pra desenhar
import math

PI = math.pi

def gen_cubo():
    # 6 faces, cada uma com 4 vertices (triangle strip)
    # vai de -0.5 a +0.5 em cada eixo

    verts = [
        # frente
        (-0.5, -0.5,  0.5), ( 0.5, -0.5,  0.5),
        (-0.5,  0.5,  0.5), ( 0.5,  0.5,  0.5),
        # direita
        ( 0.5, -0.5,  0.5), ( 0.5, -0.5, -0.5),
        ( 0.5,  0.5,  0.5), ( 0.5,  0.5, -0.5),
        # tras
        ( 0.5, -0.5, -0.5), (-0.5, -0.5, -0.5),
        ( 0.5,  0.5, -0.5), (-0.5,  0.5, -0.5),
        # esquerda
        (-0.5, -0.5, -0.5), (-0.5, -0.5,  0.5),
        (-0.5,  0.5, -0.5), (-0.5,  0.5,  0.5),
        # baixo
        (-0.5, -0.5, -0.5), ( 0.5, -0.5, -0.5),
        (-0.5, -0.5,  0.5), ( 0.5, -0.5,  0.5),
        # cima
        (-0.5,  0.5,  0.5), ( 0.5,  0.5,  0.5),
        (-0.5,  0.5, -0.5), ( 0.5,  0.5, -0.5),
    ]

    return verts  # 24 vertices, 6 strips de 4

def gen_esfera(r=0.5, sectors=24, stacks=24):
    # igual ao codigo do professor
    verts = []
    ss = (PI * 2) / sectors
    ts = PI / stacks
    def F(u, v):
        return (r*math.sin(v)*math.cos(u),
                r*math.sin(v)*math.sin(u),
                r*math.cos(v))
    for i in range(sectors):
        for j in range(stacks):
            u  = i * ss
            v  = j * ts
            un = PI*2 if i+1 == sectors else (i+1)*ss
            vn = PI   if j+1 == stacks  else (j+1)*ts
            p0, p1, p2, p3 = F(u,v), F(u,vn), F(un,v), F(un,vn)
            verts += [p0, p2, p1,  p3, p1, p2]
    return verts

def gen_pera(r=1.0, sectors=24, stacks=24, topo=0.6, eixo="z"):
    # esfera deformada nao linearmente: 
    # o raio em xy encolhe subindo em z, com fator 1 no equador
    # eixo: pra onde aponta a ponta fina, "z" (padrao) ou "y"

    verts = []
    for (x, y, z) in gen_esfera(r=r, sectors=sectors, stacks=stacks):
        t = max(z / r, 0.0) # 0 na metade de baixo, 1 no polo de cima
        f = 1.0 - (1.0 - topo) * t
        if eixo == "y":
            # gira em x pra ponta sair em +y
            verts.append((x*f, z, -y*f))
        else:
            verts.append((x*f, y*f, z))

    return verts

def gen_cilindro(r=0.5, h=1.0, sectors=24, stacks=1):
    # corpo + tampas
    # retorna (verts, n_corpo, n_tampa_base, n_tampa_topo)
    corpo = []
    tampa_base = []
    tampa_topo = []

    ss = (PI * 2) / sectors
    sh = h / stacks

    def C(t, z):
        return (r*math.cos(t), r*math.sin(t), z)

    centro_base = (0.0, 0.0, 0.0)
    centro_topo = (0.0, 0.0, h)

    for j in range(stacks):
        for i in range(sectors):
            u  = i * ss
            v  = j * sh
            un = PI*2 if i+1 == sectors else (i+1)*ss
            vn = h     if j+1 == stacks  else (j+1)*sh
            p0,p1,p2,p3 = C(u,v), C(u,vn), C(un,v), C(un,vn)
            corpo += [p0, p2, p1,  p3, p1, p2]
            if j == 0:
                tampa_base += [p0, p2, centro_base]
            if j+1 == stacks:
                tampa_topo += [p1, p3, centro_topo]

    verts = corpo + tampa_base + tampa_topo

    return verts, len(corpo), len(tampa_base), len(tampa_topo)

def gen_quadrado_2d(w=0.1, h=0.1):
    # dois triangulos formando um quadrado no plano z=0

    hw, hh = w/2, h/2
    return [
        (-hw, -hh, 0.0), ( hw, -hh, 0.0), ( hw,  hh, 0.0),
        (-hw, -hh, 0.0), ( hw,  hh, 0.0), (-hw,  hh, 0.0),
    ]

def gen_triangulo_2d(base=0.08, altura=0.10):

    # triangulo isoceles no plano z=0
    hb = base / 2
    return [
        (-hb, 0.0,    0.0),
        ( hb, 0.0,    0.0),
        (0.0, altura, 0.0),
    ]

def gen_circulo_2d(r=0.5, sectors=20):
    # circulo no plano z=0 com leque de triangulos do centro
    verts = []
    passo = (PI * 2) / sectors

    for i in range(sectors):
        u  = i * passo
        un = PI*2 if i+1 == sectors else (i+1) * passo
        verts += [(0.0, 0.0, 0.0),
                  (r*math.cos(u),  r*math.sin(u),  0.0),
                  (r*math.cos(un), r*math.sin(un), 0.0)]

    return verts

def gen_aba_carta(w=1.0, h=1.0, fundo=0.0):
    # tres pontos em V (para GL_LINE_STRIP)
    # a aba do envelope, de um canto de cima ate o meio e de volta p/ o canto oposto
    return [(-w/2, h/2, 0.0), (0.0, fundo, 0.0), (w/2, h/2, 0.0)]

def gen_ponteiro(largura=0.02, comprimento=0.3):
    # retangulo fino no plano z=0, base na origem, estende em +y
    # deve girar em z pra apontar a hora
    hw = largura / 2

    return [
        (-hw, 0.0,0.0), ( hw, 0.0,0.0), ( hw, comprimento, 0.0),
        (-hw, 0.0,0.0), ( hw, comprimento, 0.0), (-hw, comprimento, 0.0),
    ]
