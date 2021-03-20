import random
from models import Monoplano
from avl import criar_arquivo

n_candidatos = 100
n_selecionados = 50

b_min_w = 1.5
c_min_w = 0.2
b_max_w = 3.0
c_max_w = 0.6

b_min_h = 0.1
c_min_h = 0.1
b_max_h = 2
c_max_h = 0.3
ht_max = 0.6

b_min_v = 0.1
c_min_v = 0.1
b_max_v = 0.5
c_max_v = 0.3
lambda_min_v = 0.4
lambda_max_v = 0.95

iw_max = 5
ih_max = -5

mtow_min = 16
mtow_max = 16

offset_max = 0.4
n_sect = 3
dist_nariz = 0.295
soma_dims = 3.2 - dist_nariz

#perfis_asa = ['FX 74-Cl5-140 MOD (smoothed)', 'S1223 RTL', 'CH10 (smoothed)', 'DAE-21 AIRFOIL', 'WORTMANN FX 63-137 AIRFOIL']
#perfis_eh = ['e168', 'e169', 'e479', 'n0012', 'naca0015']
perfis_asa = ['s1223']
perfis_eh = ['e168']
perfis_ev = ['e169']

def gerar_inicial():
    aeronaves = []
    for i in range(n_candidatos):
        cr = random.uniform(c_min_w, c_max_w)
        ct = random.uniform(c_min_w, cr)
        br = random.uniform(b_min_w/2, b_max_w/2 - 0.1)
        bt = random.uniform(0.1, b_max_w/2 - br)
        o1 = random.uniform(0, offset_max)
        b = br + bt
        geometria_asa = [(0, cr, 0), (br, cr, 0), (b, ct, o1)]

        bh = random.uniform(b_min_h/2, b_max_h/2)
        ch = random.uniform(c_min_h, c_max_h)
        
        geometria_eh = [(0, ch, 0), (bh, ch, 0)]

        crv = random.uniform(ch, c_max_v)
        lambda_v = random.uniform(lambda_min_v, lambda_max_v)
        ctv = lambda_v*crv
        bv = random.uniform(b_min_v, b_max_v)
        
        geometria_ev = [(0, crv, 0), (bv, ctv, crv-ctv)]

        iw =  random.uniform(0, iw_max)
        ih =  random.uniform(ih_max, 0)
        
        ht = random.uniform(0, ht_max)

        mtow = random.uniform(mtow_min, mtow_max)

        posicoes = { 'asa' : (0,0), 'eh' : (soma_dims - ch - b*2, ht), 'ev' : (soma_dims - crv - b*2, ht) }
        perfil_asa = random.choice(perfis_asa)
        perfil_eh = random.choice(perfis_eh)
        perfil_ev = random.choice(perfis_ev)
        aeronaves.append(Monoplano(geometria_asa, perfil_asa, iw, geometria_eh, perfil_eh, ih, geometria_ev, perfil_ev, posicoes, mtow))
    return aeronaves

def variar(aeronave, sigma):
    geometria_asa = aeronave.geometria_asa.copy()
    geometria_eh = aeronave.geometria_eh.copy()
    geometria_ev = aeronave.geometria_ev.copy()

    br, cr, o1 = geometria_asa[1]
    b, ct, o2 = geometria_asa[2]
    bt = b - br
    
    ch = geometria_eh[0][1]
    bh = geometria_eh[1][0]

    crv = geometria_ev[0][1]
    ctv = geometria_ev[1][1]
    bv  = geometria_ev[1][0]
    
    br = trunc_gauss(br, sigma, b_min_w/2, b_max_w/2 - 0.1)
    bt = trunc_gauss(bt, sigma, 0.1, b_max_w/2 - bt)
    cr = trunc_gauss(cr, sigma, ct, c_max_w)
    o1 = trunc_gauss(o1, sigma, 0, offset_max)
    ct = trunc_gauss(ct, sigma, c_min_w, cr)
    b = bt + br

    ch = trunc_gauss(ch, sigma, c_min_h, c_max_h)
    bh = trunc_gauss(bh, sigma, b_min_h/2, b_max_h/2)

    ctv = trunc_gauss(ctv, sigma, c_min_v, crv)
    bv = trunc_gauss(bv, sigma, b_min_v, b_max_v)
    lambda_v = ctv/crv
    lambda_v = trunc_gauss(lambda_v, sigma, lambda_min_v, lambda_max_v)
    ctv = lambda_v*crv

    iw = trunc_gauss(aeronave.iw, sigma*10, 0, iw_max)
    ih = trunc_gauss(aeronave.ih, sigma, ih_max, 0)
    
    ht = aeronave.posicoes['eh'][1]
    ht = trunc_gauss(ht, sigma, 0, ht_max)

    mtow = trunc_gauss(aeronave.mtow, sigma, mtow_min, mtow_max)

    geometria_asa = [(0, cr, 0), (br, cr, 0), (b, ct, o1)]
    geometria_eh = [(0, ch, 0), (bh, ch, 0)]
    geometria_ev = [(0, crv, 0), (bv, ctv, crv-ctv)]

    posicoes = { 'asa' : (0,0), 'eh' : (soma_dims - ch - b*2, ht), 'ev' : (soma_dims - crv - b*2, ht) }

    return Monoplano(geometria_asa, aeronave.perfil_asa, iw, geometria_eh, aeronave.perfil_eh, ih, geometria_ev, aeronave.perfil_ev, posicoes, mtow)

def reproducao(gerados, sigma):
    pais = sorted(gerados, key= lambda a : a.nota, reverse=True)[:n_selecionados]
    filhos = []
    for pai in pais:
        for i in range(int(len(gerados)/len(pais))):
            filhos.append(variar(pai, sigma))
    return filhos

def trunc_gauss(mu, sigma, bottom, top):
    a = random.gauss(mu,sigma)
    if a >= top:
        return top
    if a <= bottom:
        return bottom
    return a
