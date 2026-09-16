# matrizes 4x4
# vao pro vertex shader como mat_transformation
import math
import numpy as np

def mat_identidade():
    return np.eye(4, dtype=np.float32)

def mat_translacao(tx, ty, tz):
    m = mat_identidade()

    m[0,3], m[1,3], m[2,3] = tx, ty, tz
    return m

def mat_escala(sx, sy, sz):
    m = mat_identidade()
    m[0,0], m[1,1], m[2,2] = sx, sy, sz

    return m

def mat_rotacao_x(ang):
    c, s = math.cos(ang), math.sin(ang)
    m = mat_identidade()
    m[1,1],m[1,2] = c, -s
    m[2,1],m[2,2] = s,  c

    return m

def mat_rotacao_y(ang):
    c, s = math.cos(ang), math.sin(ang)
    m = mat_identidade()
    m[0,0],m[0,2] = c, s
    m[2,0],m[2,2] = -s, c

    return m

def mat_rotacao_z(ang):
    c, s = math.cos(ang), math.sin(ang)
    m = mat_identidade()
    m[0,0],m[0,1] = c, -s
    m[1,0],m[1,1] = s, c

    return m

def compor(*mats):
    # multiplicacao da esquerda para a direita, compor(A, B, C) = A @ B @ C
    result = mat_identidade()
    for m in mats:
        result = result @ m

    return result
