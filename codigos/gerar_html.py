#!/usr/bin/env python3
"""Página interativa com os gráficos finais 1 e 2 (agregador.html, na raiz do projeto).

Uso: python gerar_html.py [--as-of 2026-10-20]
Recalcula o modelo e a tendência em memória e injeta os dados (JSON) no molde
html_molde.html, que desenha os gráficos em SVG com JavaScript puro, sem dependências.
Mesmos cálculos de graficos_ps.py: média SIMPLES do erro do 1º turno.
"""
import argparse
import json
from datetime import date

import numpy as np

from graficos import DADOS, ELEICAO_1T, tendencia
from modelo_vies import PASTA_PROJETO, TSE_FLAVIO, TSE_LULA, RESULTADO_MARGEM, calcular, ler, d

MOLDE = PASTA_PROJETO / 'codigos' / 'html_molde.html'
SAIDA = PASTA_PROJETO / 'agregador.html'
BASE = date(2026, 1, 1)


def num(dt):
    return float((dt - BASE).days)


def r2(x, n=3):
    return None if x is None else round(float(x), n)


def montar(as_of):
    resumo, um, vies, dois, cenarios = calcular(ler(DADOS), d(as_of))
    erro = resumo['erro_comum_simples']
    metodo_1t = {r['registro_tse']: r for r in um}

    barras = []
    for v in vies:
        r = metodo_1t[v['registro_1t']]
        barras.append({'instituto': v['instituto'], 'erro': r2(-v['erro_observado']),
                       'registro': v['registro_1t'], 'inicio': r['inicio_campo'], 'fim': v['fim_1t'],
                       'amostra': v['n_1t'], 'metodo': r['metodo'],
                       'flavio': r2(v['flavio_validos_1t']), 'lula': r2(v['lula_validos_1t']),
                       'margem': r2(v['margem_1t']), 'criterio': v['criterio_validos_1t']})

    pts = [r for r in dois if r['flavio_validos'] is not None]
    pontos = [{'instituto': r['instituto'], 't': num(r['ultimo_dia']), 'inicio': r['inicio_campo'],
               'fim': r['fim_campo'], 'divulgacao': r['data_divulgacao'], 'amostra': r['amostra'],
               'metodo': r['metodo'], 'registro': r['registro_tse'], 'base': r['base_original'],
               'flavio': r2(r['flavio_validos']), 'lula': r2(r['lula_validos']),
               'flavio_rep': r['flavio_reportado_pct'], 'lula_rep': r['lula_reportado_pct'],
               'atual': bool(r['ultimo_2t']), 'peso': r2(r['peso_total']), 'fonte': r['fonte']}
              for r in pts]

    segmentos = []
    for seg in ([r for r in pts if r['ultimo_dia'] < ELEICAO_1T], [r for r in pts if r['ultimo_dia'] >= ELEICAO_1T]):
        t = np.array([num(r['ultimo_dia']) for r in seg])
        y = np.array([r['flavio_validos'] for r in seg])
        n = np.array([r['amostra'] for r in seg], float)
        grade = np.linspace(t.min(), t.max(), 120)
        nivel, disp, _ = tendencia(t, y, n, grade)
        segmentos.append({'t': [r2(g, 4) for g in grade], 'nivel': [r2(v) for v in nivel], 'disp': [r2(v) for v in disp]})

    f0 = segmentos[-1]['nivel'][-1]
    return {
        'as_of': as_of, 'base': BASE.isoformat(), 'eleicao_1t': num(ELEICAO_1T),
        'urna': {'flavio': TSE_FLAVIO, 'lula': TSE_LULA, 'margem': r2(RESULTADO_MARGEM)},
        'erro_simples': r2(erro, 4), 'erro_ponderado': r2(resumo['erro_comum_ponderado'], 4),
        'institutos_2t': resumo['institutos_agregados_2t'], 'pesquisas_2t': len(pontos),
        'atual': {'t': segmentos[-1]['t'][-1], 'flavio': f0},
        'corrigido': {'flavio': r2(f0 + erro / 2), 'lula': r2(100 - f0 - erro / 2)},
        'modelo': {'bruto': r2(resumo['media_2t_bruta_f']), 'ajustado': r2(resumo['media_2t_ajustada_f']),
                   'alpha': resumo['alpha_central'], 'shrink': resumo['shrink_house']},
        'cenarios': [{'alpha': c['alpha'], 'flavio': r2(c['flavio_validos']), 'lula': r2(c['lula_validos'])} for c in cenarios],
        'barras': barras, 'pontos': pontos, 'segmentos': segmentos,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--as-of', default='2026-10-20')
    args = ap.parse_args()
    dados = montar(args.as_of)
    html = MOLDE.read_text(encoding='utf-8')
    html = html.replace('/*__DADOS__*/null', json.dumps(dados, ensure_ascii=False))
    SAIDA.write_text(html, encoding='utf-8')
    print(f'Gravado em {SAIDA}')
    print(f"Tendência atual Flávio {dados['atual']['flavio']:.2f}; com correção: "
          f"Flávio {dados['corrigido']['flavio']:.2f} x Lula {dados['corrigido']['lula']:.2f}")


if __name__ == '__main__':
    main()
