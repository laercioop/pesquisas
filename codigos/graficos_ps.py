#!/usr/bin/env python3
"""Gráficos finais 1 e 2 no estilo P&S (template.py).

Uso: python graficos_ps.py [--as-of 2026-10-20]
Gera, na raiz de graficos/, 1_erro_por_instituto_1t.png e 2_tendencia_2t_todas.png, e em
graficos/svg/ os mesmos em SVG, em português e em inglês (_en).
Usa a média SIMPLES do erro do 1º turno (a ponderada fica só no modelo/análises preliminares).
"""
import argparse
from datetime import date, timedelta

import numpy as np
import matplotlib.ticker

from graficos import DADOS, ELEICAO_1T, tendencia
from modelo_vies import PASTA_PROJETO, calcular, ler, d
from template import *

SAIDA = PASTA_PROJETO / 'graficos'
MESES_EN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

TEXTOS = {
    'pt': {
        'fonte': 'Fonte: pesquisas registradas no TSE. Elaboração P&S.',
        'media': 'média: {} pp',
        'comentario_erro': 'pp na margem Flávio - Lula;\npositivo = pesquisa\nsuperestimou Flávio',
        'titulo_erro': 'Erro das pesquisas no 1º turno, por instituto',
        'turno': '1º turno\n04/10',
        'atual': 'atual {}%',
        'correcao': 'com correção de viés',
        'nota_correcao': 'atual + erro médio\ndo 1º turno\n(+{} pp na margem)',
        'metodo': {'telefone': 'Telefone', 'presencial': 'Presencial', 'online': 'Online', 'nao_informado': 'Não informado'},
        'titulo_tend': 'Lula x Flávio no 2º turno - agregado das pesquisas',
        'rodape': 'Votos válidos (só os dois candidatos). Linha: regressão local ponderada pela amostra (janela ~3 dias); '
                  'faixa: onde cairiam 95% das pesquisas.',
        'data': lambda t: t.strftime('%d/%m'),
    },
    'en': {
        'fonte': 'Source: polls registered with the TSE. Prepared by P&S.',
        'media': 'average: {} pp',
        'comentario_erro': 'pp on the Flávio - Lula margin;\npositive = poll\noverstated Flávio',
        'titulo_erro': 'Polling error in the 1st round, by pollster',
        'turno': '1st round\nOct 4',
        'atual': 'current {}%',
        'correcao': 'bias-corrected',
        'nota_correcao': 'current + average\n1st-round error\n(+{} pp on the margin)',
        'metodo': {'telefone': 'Phone', 'presencial': 'Face-to-face', 'online': 'Online', 'nao_informado': 'Not reported'},
        'titulo_tend': 'Lula vs. Flávio in the 2nd round - poll aggregate',
        'rodape': 'Valid votes (two candidates only). Line: local regression weighted by sample size (~3-day window); '
                  'band: where 95% of polls would fall.',
        'data': lambda t: f'{MESES_EN[t.month - 1]} {t.day}',
    },
}


def br(x, n=1, lang='pt'):
    s = f'{x:.{n}f}'
    return s if lang == 'en' else s.replace('.', ',')


def fonte(ax, T, y=-0.13):
    ax.text(0, y, T['fonte'], transform=ax.transAxes, ha='left', va='top', fontsize=6.5, color=GRAY)


def salvar(fig, n, slug, lang):
    """PT: PNG na raiz de graficos/ (save_chart) + SVG em graficos/svg/. EN: só o SVG _en."""
    pasta_svg = SAIDA / 'svg'
    pasta_svg.mkdir(parents=True, exist_ok=True)
    sufixo = '' if lang == 'pt' else '_' + lang
    svg = pasta_svg / f'{n}_{slug}{sufixo}.svg'
    fig.savefig(svg, facecolor='white', bbox_inches='tight', pad_inches=0.025)
    if lang == 'pt':
        return save_chart(fig, SAIDA, n, slug)
    import matplotlib.pyplot as plt
    plt.close(fig)
    return svg


def grafico_erro(vies, erro_comum, lang='pt'):
    T = TEXTOS[lang]
    # Sinal: margem da pesquisa menos margem da urna (positivo = pesquisa favoreceu Flávio).
    erro_comum = -erro_comum
    v = sorted(vies, key=lambda r: -r['erro_observado'], reverse=True)
    fig, ax = make_figure()
    style_axes(ax)
    y = np.arange(len(v))
    erros = [-r['erro_observado'] for r in v]
    ax.barh(y, erros, height=.62, color=[BLUE if e >= 0 else TERRACOTTA for e in erros], zorder=2)
    for i, e in zip(y, erros):
        ax.text(e + (.12 if e >= 0 else -.12), i, ('+' if e > 0 else '') + br(e, 1, lang), va='center', ha='right' if e >= 0 else 'left',
                fontsize=6.3, color='#404040', zorder=4,
                bbox=dict(facecolor='white', edgecolor='none', pad=.6))
    ax.axvline(0, color=GRAY, lw=.75, zorder=3)
    ax.axvline(erro_comum, color=GRAY_DARK, lw=1, ls=DOTTED, zorder=1)
    ax.text(erro_comum - .15, 3.0, T['media'].format(br(erro_comum, 2, lang)), fontsize=6.5,
            color=GRAY_DARK, va='center', ha='left')
    ax.set_yticks(y)
    ax.set_yticklabels([r['instituto'] for r in v])
    ax.tick_params(axis='y', length=0)
    ax.set_ylim(-.6, len(v) - .1)
    ax.set_xlim(max(erros) + 1.2, min(erros) - 1.2)  # eixo invertido: erro negativo à direita
    ax.xaxis.set_major_locator(MultipleLocator(2))
    add_comment(ax, T['comentario_erro'], xy=(.99, .02), ha='right')
    fonte(ax, T, -.13)
    add_title_aligned(fig, ax, T['titulo_erro'], fontsize=11)
    return salvar(fig, 1, 'erro_por_instituto_1t', lang)


def grafico_tendencia_ps(dois, erro_comum, lang='pt'):
    """Layout do gráfico de tendência anterior, com cores e fontes P&S e sem zona de projeção.
    No fim, a tendência atual somada ao erro médio do 1º turno (margem +erro_comum)."""
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from graficos import MARCADOR
    T = TEXTOS[lang]
    base = date(2026, 1, 1)
    num = lambda dt: float((dt - base).days)
    pts = [r for r in dois if r['flavio_validos'] is not None]
    inicio = min(r['ultimo_dia'] for r in pts)
    ultimo = max(r['ultimo_dia'] for r in pts)
    fig, ax = plt.subplots(figsize=(11.5, 5.4))
    fig.patch.set_facecolor('white'); ax.set_facecolor('white')
    for lado in ('top', 'right', 'left'):
        ax.spines[lado].set_visible(False)
    ax.spines['bottom'].set_color(GRAY); ax.spines['bottom'].set_linewidth(.75)
    ax.yaxis.grid(True, color='#e6e6e6', lw=.8); ax.xaxis.grid(False); ax.set_axisbelow(True)
    ax.tick_params(axis='both', length=3.5, width=.65, color=GRAY, labelsize=10, labelcolor='#404040')
    ax.tick_params(axis='y', length=0)

    ax.axvline(num(ELEICAO_1T), color=GRAY, lw=1, ls='--', zorder=1)
    ax.text(num(ELEICAO_1T) + .2, 56.8, T['turno'], va='top', fontsize=9, color=GRAY)

    fim = None
    for seg in ([r for r in pts if r['ultimo_dia'] < ELEICAO_1T], [r for r in pts if r['ultimo_dia'] >= ELEICAO_1T]):
        t = np.array([num(r['ultimo_dia']) for r in seg]); yv = np.array([r['flavio_validos'] for r in seg])
        n = np.array([r['amostra'] for r in seg], float)
        grade = np.linspace(t.min(), t.max(), 120)
        nivel, disp, _ = tendencia(t, yv, n, grade)
        for cor, nv in ((BLUE, nivel), (TERRACOTTA, 100 - nivel)):
            ax.fill_between(grade, nv - 1.96 * disp, nv + 1.96 * disp, color=cor, alpha=.13, lw=0, zorder=2)
            ax.plot(grade, nv, color=cor, lw=LW_MAIN, solid_capstyle=CAP, zorder=4)
        fim = (grade[-1], nivel[-1])

    for r in pts:
        mk = MARCADOR.get(r['metodo'], 'D')
        for cor, v in ((BLUE, r['flavio_validos']), (TERRACOTTA, r['lula_validos'])):
            ax.scatter(num(r['ultimo_dia']), v, marker=mk, s=34, color=cor, edgecolor='white', linewidth=.9, zorder=5, alpha=.9)

    # Atual + erro médio do 1º turno: margem +erro_comum, ou seja, Flávio +erro_comum/2
    x0, f0 = fim
    xc = x0 + 2.5
    fc, lc = f0 + erro_comum / 2, 100 - f0 - erro_comum / 2
    for cor, v0, dy in ((BLUE, f0, 1), (TERRACOTTA, 100 - f0, -1)):
        ax.annotate(T['atual'].format(br(v0, 1, lang)), (x0, v0), xytext=(0, 26 * dy), textcoords='offset points',
                    ha='center', va='center', fontsize=9.5, color=cor, fontweight='bold', zorder=7)
    for cor, v0, vc, nome in ((BLUE, f0, fc, 'Flávio'), (TERRACOTTA, 100 - f0, lc, 'Lula')):
        ax.plot([x0, xc], [v0, vc], color=cor, lw=1.4, ls=DOTTED, zorder=3)
        ax.scatter(xc, vc, s=60, color=cor, edgecolor='white', linewidth=1, zorder=6)
        ax.text(xc + .35, vc + .08, f'{nome} {br(vc, 1, lang)}%', fontsize=11, color=cor, va='bottom', fontweight='bold')
        ax.text(xc + .35, vc - .08, T['correcao'], fontsize=8, color=cor, va='top')
    ax.text(xc + .35, 54.0, T['nota_correcao'].format(br(erro_comum, 2, lang)),
            fontsize=8.5, color=GRAY, ha='left', va='bottom', fontstyle='italic')

    ticks = []
    dt = inicio
    while dt <= ultimo:
        ticks.append(dt); dt += timedelta(days=2)
    ax.set_xticks([num(t) for t in ticks])
    ax.set_xticklabels([T['data'](t) for t in ticks])
    ax.set_xlim(num(inicio) - .8, xc + 3.2)
    ax.set_ylim(42, 57)
    ax.set_yticks([45, 47.5, 50, 52.5, 55])
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
        lambda v, _: f'{v:g}%' if lang == 'en' else f'{v:g}%'.replace('.', ',')))

    h = [Line2D([], [], color=BLUE, lw=LW_MAIN, label='Flávio Bolsonaro'), Line2D([], [], color=TERRACOTTA, lw=LW_MAIN, label='Lula')]
    metodos = sorted({r['metodo'] for r in pts}, key=list(MARCADOR).index)
    h += [Line2D([], [], marker=MARCADOR[m], color=GRAY, ls='', ms=6, label=T['metodo'][m]) for m in metodos]
    # Candidatos logo à esquerda da linha do 1º turno; métodos logo à direita.
    x0l, x1l = ax.get_xlim()
    frac = (num(ELEICAO_1T) - x0l) / (x1l - x0l)
    leg = ax.legend(handles=h[:2], loc='center right', bbox_to_anchor=(frac - .012, .045), ncol=2, frameon=False, prop=LEGEND_FONT, columnspacing=1.2)
    ax.add_artist(leg)
    ax.legend(handles=h[2:], loc='center left', bbox_to_anchor=(frac + .012, .045), ncol=len(h) - 2, frameon=False, prop=LEGEND_FONT4,
              columnspacing=1.0, handletextpad=.3, markerscale=.8)
    ax.text(0, 1.03, T['titulo_tend'], transform=ax.transAxes, ha='left', va='bottom',
            family='Segoe UI', weight='bold', fontsize=19, color=TITLE_GRAY)
    fig.text(.125, .03, T['rodape'] + '\n' + T['fonte'], fontsize=8.5, color=GRAY, va='top')
    return salvar(fig, 2, 'tendencia_2t_todas', lang), (f0, fc, lc)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--as-of', default='2026-10-20')
    args = ap.parse_args()
    resumo, _, vies, dois, _ = calcular(ler(DADOS), d(args.as_of))
    erro = resumo['erro_comum_simples']
    print(f'Erro médio simples do 1T: {erro:+.2f} pp na margem')
    for lang in TEXTOS:
        print(grafico_erro(vies, erro, lang))
        caminho, (f0, fc, lc) = grafico_tendencia_ps(dois, erro, lang)
        print(caminho)
    print(f'Tendência atual Flávio {f0:.2f}; com erro do 1T: Flávio {fc:.2f} x Lula {lc:.2f}')


if __name__ == '__main__':
    main()
