#!/usr/bin/env python3
"""Gráficos ilustrativos e tabela de sensibilidade do modelo eleitoral 2026.

Uso: python graficos.py [--as-of 2026-10-23]
Lê dados/brutos/pesquisas_2026.csv, recalcula o modelo em memória e grava
PNGs em graficos/ e dados/resultados/sensibilidade.csv.
"""
import argparse
import csv
from datetime import date, timedelta

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker

from modelo_vies import PASTA_PROJETO, TSE_FLAVIO, TSE_LULA, RESULTADO_MARGEM, calcular, ler, d

DADOS = PASTA_PROJETO/'dados'/'brutos'/'pesquisas_2026.csv'
SAIDA = PASTA_PROJETO/'graficos'/'analises preliminares'
RESULTADOS = PASTA_PROJETO/'dados'/'resultados'

# Paleta de referência (modo claro): identidade fixa por candidato.
FLAVIO = '#2a78d6'
LULA = '#e34948'
NEUTRO = '#8a8984'
TEXTO = '#0b0b0b'
TEXTO_2 = '#52514e'
GRADE = '#e4e3df'
FUNDO = '#fcfcfb'

plt.rcParams.update({
    'figure.facecolor': FUNDO, 'axes.facecolor': FUNDO, 'savefig.facecolor': FUNDO,
    'font.size': 10, 'axes.edgecolor': GRADE, 'axes.labelcolor': TEXTO_2,
    'xtick.color': TEXTO_2, 'ytick.color': TEXTO_2, 'text.color': TEXTO,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.grid': True, 'grid.color': GRADE, 'grid.linewidth': .8,
    'axes.titlesize': 13, 'axes.titleweight': 'bold', 'axes.titlelocation': 'left',
    'legend.frameon': False, 'axes.axisbelow': True,
})


def br(x, n=1):
    return f'{x:.{n}f}'.replace('.', ',')


def fecha(fig, nome, fonte='Fonte: pesquisas registradas no TSE (catálogo E26 e imprensa); TSE. Elaboração própria.', y=-.02):
    fig.text(.01, y, fonte, fontsize=8, color=TEXTO_2, va='top')
    fig.savefig(SAIDA/nome, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print('  ', nome)


def grafico_primeiro_turno(um):
    """Margem Flávio−Lula de cada pesquisa no 1º turno contra o resultado da urna."""
    fig, ax = plt.subplots(figsize=(9, 4.8))
    pts = [r for r in um if r['margem_f_menos_l'] is not None]
    ax.axhline(0, color=TEXTO_2, lw=.8)
    ax.scatter([r['ultimo_dia'] for r in pts], [r['margem_f_menos_l'] for r in pts],
               s=28, color=NEUTRO, edgecolor=FUNDO, linewidth=1, zorder=3, label='Pesquisa (votos válidos)')
    ult = [r for r in pts if r['ultima_rodada']]
    ax.scatter([r['ultimo_dia'] for r in ult], [r['margem_f_menos_l'] for r in ult],
               s=42, color=FLAVIO, edgecolor=FUNDO, linewidth=1, zorder=4, label='Última rodada do instituto (usada na calibração)')
    eleicao = date(2026, 10, 4)
    ax.scatter([eleicao], [RESULTADO_MARGEM], marker='D', s=70, color=TEXTO, zorder=5, label='Resultado nas urnas')
    ax.annotate(f'Urna: Flávio +{br(RESULTADO_MARGEM, 2)}', (eleicao, RESULTADO_MARGEM),
                xytext=(-12, -4), textcoords='offset points', ha='right', va='top', fontsize=9, fontweight='bold')
    ax.set_title('1º turno: as pesquisas subestimaram Flávio')
    ax.set_ylabel('Margem Flávio − Lula (pp, votos válidos)')
    ax.set_xlim(date(2026, 8, 15), date(2026, 10, 8))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
    ax.legend(loc='lower right', fontsize=8.5)
    fecha(fig, '01_primeiro_turno_margem.png')


def grafico_erro_institutos(vies, resumo):
    """Erro de cada instituto (urna − pesquisa) e o efeito encolhido usado no 2º turno."""
    v = sorted(vies, key=lambda r: r['erro_observado'])
    fig, ax = plt.subplots(figsize=(9, 5.4))
    y = range(len(v))
    ax.barh(y, [r['erro_observado'] for r in v], height=.6, color=FLAVIO, alpha=.35, label='Erro observado na última rodada')
    ax.scatter([r['erro_shrunk'] for r in v], y, s=40, color=FLAVIO, zorder=3, label='Erro encolhido (shrink 0,25)')
    ax.axvline(resumo['erro_comum_ponderado'], color=TEXTO, lw=1.2, ls='--')
    ax.text(resumo['erro_comum_ponderado'], len(v) - .4, f" erro comum ponderado {br(resumo['erro_comum_ponderado'], 2)} pp",
            fontsize=8.5, va='bottom')
    ax.axvline(0, color=TEXTO_2, lw=.8)
    ax.set_yticks(list(y)); ax.set_yticklabels([r['instituto'] for r in v])
    ax.set_xlabel('Erro na margem (pp). Positivo = pesquisa subestimou Flávio')
    ax.set_title('Erro de cada instituto no 1º turno')
    ax.grid(axis='y', visible=False)
    ax.legend(loc='lower right', fontsize=8.5)
    fecha(fig, '02_erro_por_instituto_1t.png')


def grafico_segundo_turno(dois, resumo):
    """Série do 2º turno pós-eleição em votos válidos, com a média agregada."""
    pos = [r for r in dois if r['ultimo_dia'] >= date(2026, 10, 5)]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.axhline(50, color=TEXTO_2, lw=.8)
    for cand, chave, cor in (('Flávio', 'flavio_validos', FLAVIO), ('Lula', 'lula_validos', LULA)):
        ativos = [r for r in pos if r['ultimo_2t']]
        antigos = [r for r in pos if not r['ultimo_2t']]
        ax.scatter([r['ultimo_dia'] for r in antigos], [r[chave] for r in antigos], s=26, facecolor=FUNDO,
                   edgecolor=cor, linewidth=1.5, zorder=3)
        ax.scatter([r['ultimo_dia'] for r in ativos], [r[chave] for r in ativos], s=34, color=cor,
                   edgecolor=FUNDO, linewidth=1, zorder=4, label=f'{cand}')
    fim = max(r['ultimo_dia'] for r in pos)
    for valor, cor in ((resumo['media_2t_bruta_f'], FLAVIO), (resumo['media_2t_bruta_l'], LULA)):
        ax.plot([date(2026, 10, 5), fim], [valor, valor], color=cor, lw=2, alpha=.8)
        ax.annotate(f'{br(valor, 1)}%', (fim, valor), xytext=(6, 0), textcoords='offset points',
                    va='center', fontsize=9, fontweight='bold', color=TEXTO)
    ax.set_xlim(date(2026, 10, 4), fim + timedelta(days=1.2))
    ax.set_ylim(44, 56)
    ax.set_title('2º turno: pesquisas após a eleição (votos válidos)')
    ax.set_ylabel('% dos votos válidos')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
    ax.legend(loc='upper left', fontsize=8.5, ncol=2, title='Ponto cheio = rodada atual do instituto; vazado = rodada anterior',
              title_fontsize=8)
    fig.text(.01, -.06, 'Linhas: média ponderada sem correção de viés (recência, amostra, método).', fontsize=8, color=TEXTO_2, va='top')
    fecha(fig, '03_segundo_turno_serie.png')


def grafico_ativas(dois):
    """Rodada corrente de cada instituto: Flávio bruto x ajustado (alfa central)."""
    a = sorted([r for r in dois if r['ultimo_2t']], key=lambda r: r['flavio_validos'])
    fig, ax = plt.subplots(figsize=(9, 5.4))
    y = list(range(len(a)))
    for i, r in zip(y, a):
        ax.plot([r['flavio_validos'], r['flavio_ajustado']], [i, i], color=GRADE, lw=2, zorder=2)
    ax.scatter([r['flavio_validos'] for r in a], y, s=40, facecolor=FUNDO, edgecolor=FLAVIO, linewidth=1.6, zorder=3, label='Flávio, como publicado')
    ax.scatter([r['flavio_ajustado'] for r in a], y, s=40, color=FLAVIO, zorder=4, label='Flávio, corrigido (alfa 0,5)')
    ax.axvline(50, color=TEXTO_2, lw=.8)
    ax.set_yticks(y); ax.set_yticklabels([f"{r['instituto']}  ({r['fim_campo'][8:]}/{r['fim_campo'][5:7]}, peso {br(r['peso_total'], 2)})" for r in a])
    ax.set_xlabel('% de Flávio nos votos válidos')
    ax.set_title('Rodada mais recente de cada instituto no 2º turno')
    ax.grid(axis='y', visible=False)
    ax.legend(loc='lower right', fontsize=8.5)
    fecha(fig, '04_institutos_2t_bruto_vs_ajustado.png')


def grafico_cenarios(cenarios):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    al = [c['alpha'] for c in cenarios]
    ax.plot(al, [c['flavio_validos'] for c in cenarios], color=FLAVIO, lw=2, marker='o', ms=7, label='Flávio')
    ax.plot(al, [c['lula_validos'] for c in cenarios], color=LULA, lw=2, marker='o', ms=7, label='Lula')
    for c in cenarios:
        ax.annotate(br(c['flavio_validos'], 1), (c['alpha'], c['flavio_validos']), xytext=(0, 8), textcoords='offset points', ha='center', fontsize=8.5)
        ax.annotate(br(c['lula_validos'], 1), (c['alpha'], c['lula_validos']), xytext=(0, -14), textcoords='offset points', ha='center', fontsize=8.5)
    ax.axhline(50, color=TEXTO_2, lw=.8)
    ax.set_xticks(al); ax.set_xticklabels(['0\nsem correção', '0,25', '0,5\ncentral', '0,75', '1\nerro integral'])
    ax.set_xlabel('Alfa: fração do erro do 1º turno que se repete no 2º')
    ax.set_ylabel('% dos votos válidos')
    ax.set_ylim(45, 56)
    ax.set_title('Cenários condicionais do 2º turno')
    ax.legend(loc='center right', fontsize=9)
    fecha(fig, '05_cenarios_alfa.png')


ELEICAO_1T = date(2026, 10, 4)
DIA_2T = date(2026, 10, 25)
MARCADOR = {'telefone': 'o', 'presencial': '^', 'online': 's', 'nao_informado': 'D'}
NOME_METODO = {'telefone': 'Telefone', 'presencial': 'Presencial', 'online': 'Online', 'nao_informado': 'Não informado'}
# Hipóteses ILUSTRATIVAS da tendência e da projeção, em pp na fatia de Flávio nos válidos.
BANDA_DIAS = 3.0      # largura do kernel da regressão local
DERIVA_DIA = 0.35     # desvio-padrão da mudança de opinião por dia (passeio aleatório)
ERRO_SISTEMICO = 2.0  # erro comum a todas as pesquisas (no 1T, Flávio foi subestimado em ~3,7)


def tendencia(t, y, n, grade, h=BANDA_DIAS):
    """Regressão local linear: kernel gaussiano de largura h dias, peso proporcional à amostra.
    Devolve nível, dispersão das pesquisas em torno dele e erro-padrão do nível."""
    import numpy as np
    nivel, disp, ep = [], [], []
    for g in grade:
        w = np.minimum(n, 4000) / 2000 * np.exp(-.5 * ((t - g) / h) ** 2)
        X = np.column_stack([np.ones_like(t), t - g])
        beta = np.linalg.solve(X.T @ (X * w[:, None]) + 1e-9 * np.eye(2), X.T @ (w * y))
        res = y - X @ beta
        s = np.sqrt((w * res ** 2).sum() / w.sum())
        neff = w.sum() ** 2 / (w ** 2).sum()
        nivel.append(beta[0]); disp.append(s); ep.append(s / np.sqrt(neff))
    return np.array(nivel), np.array(disp), np.array(ep)


def grafico_tendencia(dois, inicio, nome, titulo):
    """Pesquisas do 2º turno com tendência, faixa de 95% e projeção para 25/10.
    A tendência é estimada separadamente antes e depois do 1º turno."""
    import numpy as np
    base = date(2026, 1, 1)
    num = lambda dt: float((dt - base).days)
    pts = [r for r in dois if r['ultimo_dia'] >= inicio and r['flavio_validos'] is not None]
    fig, ax = plt.subplots(figsize=(11.5, 5.4))
    ultimo = max(r['ultimo_dia'] for r in pts)
    inicio = min(r['ultimo_dia'] for r in pts)
    x_proj = num(DIA_2T)
    x_fim = x_proj + 1.6

    # Zona de projeção
    ax.axvspan(num(ultimo) + .5, x_fim, color='#efeeea', zorder=0, lw=0)
    ax.text((num(ultimo) + .5 + x_fim) / 2, 64.2, 'PROJEÇÃO', ha='center', va='top', fontsize=8, color=TEXTO_2)
    ax.axvline(num(ultimo) + .5, color='#c9c8c3', lw=1, ls='--', zorder=1)
    if inicio < ELEICAO_1T:
        ax.axvline(num(ELEICAO_1T), color=TEXTO_2, lw=1, ls='--', zorder=1)
        ax.text(num(ELEICAO_1T) + .2, 64.2, '1º turno\n04/10', va='top', fontsize=8, color=TEXTO_2)

    segmentos = [[r for r in pts if r['ultimo_dia'] < ELEICAO_1T], [r for r in pts if r['ultimo_dia'] >= ELEICAO_1T]]
    proj = None
    for seg in segmentos:
        if len(seg) < 4:
            continue
        t = np.array([num(r['ultimo_dia']) for r in seg]); y = np.array([r['flavio_validos'] for r in seg])
        n = np.array([r['amostra'] for r in seg], float)
        grade = np.linspace(t.min(), t.max(), 120)
        nivel, disp, ep = tendencia(t, y, n, grade)
        for cor, nv in ((FLAVIO, nivel), (LULA, 100 - nivel)):
            ax.fill_between(grade, nv - 1.96 * disp, nv + 1.96 * disp, color=cor, alpha=.13, lw=0, zorder=2)
            ax.plot(grade, nv, color=cor, lw=2.2, zorder=4)
        proj = (grade[-1], nivel[-1], ep[-1])

    for r in pts:
        mk = MARCADOR.get(r['metodo'], 'D')
        for cor, v in ((FLAVIO, r['flavio_validos']), (LULA, r['lula_validos'])):
            ax.scatter(num(r['ultimo_dia']), v, marker=mk, s=34, color=cor, edgecolor=FUNDO, linewidth=.9, zorder=5, alpha=.9)

    out = {}
    if proj and segmentos[1]:
        x0, nv, e = proj
        dias = x_proj - num(ultimo)
        dp = float(np.sqrt(e ** 2 + DERIVA_DIA ** 2 * dias + ERRO_SISTEMICO ** 2))
        sep = max(0, 1.6 - abs(2 * nv - 100)) / 2  # afasta os rótulos se estiverem colados
        for cand, cor, v, dx, dy in (('Flávio', FLAVIO, nv, -.35, sep), ('Lula', LULA, 100 - nv, .35, -sep)):
            ax.plot([x0, x_proj + dx], [v, v], color=cor, lw=1.2, ls=':', zorder=3)
            ax.errorbar(x_proj + dx, v, yerr=1.96 * dp, fmt='o', color=cor, ms=6, capsize=5, capthick=1.6,
                        elinewidth=1.6, ls='--', zorder=6)
            ax.annotate(f'{cand} {br(v, 1)}%', (x_fim, v + dy), xytext=(6, 0), textcoords='offset points',
                        va='center', fontsize=10, fontweight='bold', color=cor, annotation_clip=False)
            out[cand] = (v, v - 1.96 * dp, v + 1.96 * dp)

    # Eixos
    dias_tick = []
    dt = inicio
    passo = 1 if (ultimo - inicio).days <= 10 else 2
    while dt <= ultimo:
        dias_tick.append(dt); dt += timedelta(days=passo)
    dias_tick.append(DIA_2T)
    ax.set_xticks([num(x) for x in dias_tick])
    ax.set_xticklabels([x.strftime('%d/%m') for x in dias_tick])
    ax.set_xlim(num(inicio) - .8, x_fim)
    ax.set_ylim(35, 65)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f'{v:.0f}%'))
    ax.grid(axis='x', visible=False)
    ax.set_title(titulo)

    from matplotlib.lines import Line2D
    h = [Line2D([], [], color=FLAVIO, lw=2.2, label='Flávio Bolsonaro'), Line2D([], [], color=LULA, lw=2.2, label='Lula')]
    metodos = sorted({r['metodo'] for r in pts}, key=list(MARCADOR).index)
    h += [Line2D([], [], marker=MARCADOR[m], color=NEUTRO, ls='', ms=6, label=NOME_METODO[m]) for m in metodos]
    ax.legend(handles=h, loc='lower left', ncol=len(h), fontsize=8.5)
    fig.text(.01, -.02, 'Votos válidos (só os dois candidatos). Linha: regressão local ponderada pela amostra (janela ~3 dias); '
             'faixa: onde cairiam 95% das pesquisas.\nProjeção: tendência atual sem correção de viés, com incerteza de '
             f'mudança de opinião ({br(DERIVA_DIA, 2)} pp/dia) e erro comum das pesquisas ({br(ERRO_SISTEMICO, 1)} pp); barras = 95%.',
             fontsize=8, color=TEXTO_2, va='top')
    fecha(fig, nome, fonte='Fonte: pesquisas registradas no TSE (catálogo E26 e imprensa). Elaboração própria.', y=-.075)
    return out


def sensibilidade(data, asof):
    variantes = [
        ('Central (alfa 0,5; shrink 0,25)', dict()),
        ('Sem correção (alfa 0)', dict(alpha=0)),
        ('Erro integral (alfa 1)', dict(alpha=1)),
        ('Sem fator de método', dict(neutral=True)),
        ('Válidos publicados Datafolha/Quaest no 1T', dict(publicados=True)),
        ('Só erro comum (shrink 0)', dict(shrink=0)),
        ('Erro próprio do instituto (shrink 1)', dict(shrink=1)),
        ('Recorte de ontem (as-of 15/10)', dict(asof=asof - timedelta(days=1))),
    ]
    out = []
    for nome, kw in variantes:
        args = dict(alpha=.5, shrink=.25, neutral=False, publicados=False)
        args.update(kw)
        a = args.pop('asof', asof)
        res = calcular(data, a, **args)[0]
        out.append({'variante': nome, 'erro_comum_1t': res['erro_comum_ponderado'],
                    'institutos_2t': res['institutos_agregados_2t'],
                    'flavio_validos': res['media_2t_ajustada_f'], 'lula_validos': res['media_2t_ajustada_l'],
                    'margem_f_menos_l': res['margem_ajustada']})
    with (RESULTADOS/'sensibilidade.csv').open('w', encoding='utf-8-sig', newline='') as h:
        w = csv.DictWriter(h, fieldnames=list(out[0].keys())); w.writeheader()
        for r in out: w.writerow({k: round(v, 4) if isinstance(v, float) else v for k, v in r.items()})

    fig, ax = plt.subplots(figsize=(9, 4.8))
    y = list(range(len(out)))[::-1]
    ax.barh(y, [r['margem_f_menos_l'] for r in out], height=.55, color=FLAVIO)
    for i, r in zip(y, out):
        ax.text(r['margem_f_menos_l'] + .08, i, f"Flávio {br(r['flavio_validos'], 1)} × Lula {br(r['lula_validos'], 1)}",
                va='center', fontsize=8.5, color=TEXTO)
    ax.set_yticks(y); ax.set_yticklabels([r['variante'] for r in out])
    ax.set_xlim(0, max(r['margem_f_menos_l'] for r in out) * 1.45)
    ax.set_xlabel('Margem Flávio − Lula no 2º turno (pp, votos válidos)')
    ax.set_title('Sensibilidade: quanto o resultado muda com cada hipótese')
    ax.grid(axis='y', visible=False)
    fecha(fig, '06_sensibilidade.png')
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--as-of', default='2026-10-23')
    args = ap.parse_args()
    SAIDA.mkdir(parents=True, exist_ok=True)
    data = ler(DADOS)
    asof = d(args.as_of)
    resumo, um, vies, dois, cenarios = calcular(data, asof)
    print('Gráficos em', SAIDA)
    grafico_primeiro_turno(um)
    # Gráfico 2 (erro por instituto) agora sai de graficos_ps.py, no estilo P&S.
    grafico_segundo_turno(dois, resumo)
    grafico_ativas(dois)
    grafico_cenarios(cenarios)
    p = grafico_tendencia(dois, date(2026, 10, 5), '07_tendencia_2t_pos_eleicao.png',
                          'Lula × Flávio no 2º turno: pesquisas após o 1º turno')
    # Gráfico 8 (todas as pesquisas do 2T) agora sai de graficos_ps.py, no estilo P&S.
    for c, (v, lo, hi) in p.items():
        print(f'   projeção 25/10 {c}: {v:.1f}% (95%: {lo:.1f}–{hi:.1f})')
    for r in sensibilidade(data, asof):
        print(f"   {r['variante']:<45} F {r['flavio_validos']:.2f}  L {r['lula_validos']:.2f}  margem {r['margem_f_menos_l']:+.2f}  ({r['institutos_2t']} inst.)")


if __name__ == '__main__':
    main()
