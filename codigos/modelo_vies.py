#!/usr/bin/env python3
"""Modelo auditável de erros do 1º turno e cenários do 2º turno de 2026.

Uso: python modelo_vies.py --alpha 0.50 --shrink 0.25 --as-of 2026-10-21
Sem dependências externas. As hipóteses estão explícitas e podem ser modificadas.
Este modelo não estima probabilidades confiáveis de vitória.
"""
import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

TSE_FLAVIO=47.03
TSE_LULA=45.16
RESULTADO_MARGEM=TSE_FLAVIO-TSE_LULA  # Flávio menos Lula, em p.p. nos válidos
URL_E26='https://e26.cog.ia.br/eleicoes/pesquisas?cargo=presidente'
# O acervo E26 não publicou a decomposição do denominador da Palver de 03/10;
# votos válidos disponíveis em https://www.placardaspesquisas.com.br/presidente .
# Utilizam-se os dois números divulgados, NÃO os votos totais como se fossem válidos.
OVERRIDE_PRIMEIRO={'BR-00198/2026':(43.4,47.5)}
# Válidos (Lula, Flávio) publicados pelos próprios institutos e que diferem da
# normalização aritmética dos totais. Usados apenas com --validos-publicados.
# Atenção: o da Quaest vem de um modelo de eleitor provável (likely voter).
VALIDOS_PUBLICADOS={'BR-01708/2026':(45.,42.),'BR-02197/2026':(46.,45.)}
PASTA_PROJETO=Path(__file__).resolve().parent.parent
# fatores de método refletem APENAS um exercício de sensibilidade; não são notas empíricas.
# Troque por 1.0 para comparação sem penalização por método.
FATORES_METODO={'presencial':1.,'telefone':0.90,'online':0.70,'misto':0.85,'nao_informado':0.75}


def f(x):
    try: return float(str(x).replace(',','.'))
    except (ValueError,TypeError): return None

def d(s): return date.fromisoformat(s)

def ler(arq):
    with arq.open(encoding='utf-8-sig',newline='') as h: data=list(csv.DictReader(h))
    for r in data:
        r['amostra']=int(r['amostra'])
        r['lula_reportado_pct']=f(r['lula_reportado_pct'])
        r['flavio_reportado_pct']=f(r['flavio_reportado_pct'])
        r['brancos_nulos_pct']=f(r['brancos_nulos_pct'])
        r['indecisos_pct']=f(r['indecisos_pct'])
        r['ultimo_dia']=d(r['fim_campo'])
        r['primeiro_dia']=d(r['inicio_campo'])
        # Recorte temporal pela divulgação; sem ela, pelo fim do campo.
        r['conhecido_em']=d(r['data_divulgacao']) if r.get('data_divulgacao') else r['ultimo_dia']
    return data

def votos_validos(r,publicados=False):
    L,F=r['lula_reportado_pct'],r['flavio_reportado_pct']
    if r['turno']=='2':
        # Só restaram os dois candidatos. Divide-se pelas intenções de votos nos dois;
        # impede que arredondamentos em BN/NS causem inconsistências.
        if L+F<=0: return (None,None,'faltante')
        return (100*L/(L+F),100*F/(L+F),'normalizado_do_confronto')
    if r['base_original']=='validos': return (L,F,'reportado_validos')
    if publicados and r['registro_tse'] in VALIDOS_PUBLICADOS:
        return (*VALIDOS_PUBLICADOS[r['registro_tse']],'validos_publicados_instituto')
    if r['registro_tse'] in OVERRIDE_PRIMEIRO:
        return (*OVERRIDE_PRIMEIRO[r['registro_tse']],'validos_publicados_externos')
    BN,NS=r['brancos_nulos_pct'],r['indecisos_pct']
    if BN is None or NS is None: return (None,None,'sem_denominador')
    den=100-BN-NS
    if den<=0: return (None,None,'denominador_invalido')
    return (100*L/den,100*F/den,'normalizado_de_totais')

def ultimo_por_instituto(rows):
    items={}
    for r in rows:
        nome=r['instituto']
        if nome not in items or (r['ultimo_dia'],r['registro_tse'])>(items[nome]['ultimo_dia'],items[nome]['registro_tse']):
            items[nome]=r
    return items

def peso(r,referencia,meia_vida=14,neutral=False,penaliza_misto=False):
    dias=max(0,(referencia-r['ultimo_dia']).days)
    recencia=2**(-dias/meia_vida)
    amostral=math.sqrt(min(r['amostra'],4000)/2000)
    coleta=1 if neutral else FATORES_METODO.get(r['metodo'],FATORES_METODO['nao_informado'])
    misto=.70 if penaliza_misto and r['primeiro_dia']<date(2026,10,5) else 1.
    return recencia*amostral*coleta*misto,recencia,amostral,coleta,misto

def media_ponderada(pares):
    den=sum(w for value,w in pares if value is not None)
    if not den: raise ValueError('Nenhuma observação elegível para média ponderada')
    return sum(value*w for value,w in pares if value is not None)/den

def arred(x,n=4): return None if x is None else round(x,n)

def grava(path,rows,columns):
    with path.open('w',encoding='utf-8-sig',newline='') as h:
        w=csv.DictWriter(h,fieldnames=columns,extrasaction='ignore');w.writeheader()
        for r in rows:
            w.writerow({k:(round(r[k],6) if isinstance(r.get(k),float) else r.get(k,'')) for k in columns})


def calcular(data,asof,alpha=.5,shrink=.25,neutral=False,publicados=False):
    if not (0<=alpha<=1): raise ValueError('alpha precisa estar entre 0 e 1')
    if not (0<=shrink<=1): raise ValueError('shrink precisa estar entre 0 e 1')
    primeiro=[r for r in data if r['turno']=='1' and r['ultimo_dia']<date(2026,10,4)]
    segundo=[r for r in data if r['turno']=='2' and r['conhecido_em']<=asof]
    # Última rodada de cada instituto entre as que têm votos válidos calculáveis:
    # se a mais recente não tiver denominador, usa-se a anterior em vez de descartar o instituto.
    ultimo1=ultimo_por_instituto([r for r in primeiro if votos_validos(r,publicados)[0] is not None])
    primeiro_out=[]
    for r in sorted(primeiro,key=lambda r:(r['ultimo_dia'],r['instituto'])):
        L,F,criterio=votos_validos(r,publicados)
        p,p_rec,p_n,p_m,p_mix=peso(r,date(2026,10,4),neutral=neutral)
        ultimo=(ultimo1.get(r['instituto']) is r)
        margem=F-L if F is not None else None
        erro=RESULTADO_MARGEM-margem if margem is not None else None
        primeiro_out.append({**r,'lula_validos':L,'flavio_validos':F,'criterio_validos':criterio,
            'margem_f_menos_l':margem,'erro_retro_urna':erro,'ultima_rodada':int(ultimo),
            'peso_calibracao':p if ultimo and erro is not None else 0})
    ativos1=[r for r in primeiro_out if r['ultima_rodada'] and r['erro_retro_urna'] is not None]
    if len(ativos1)<5: raise ValueError('Amostra insuficiente para calibrar viés comum')
    erro_comum=media_ponderada([(r['erro_retro_urna'],r['peso_calibracao']) for r in ativos1])
    # Comparação sem pesos, útil como controle metodológico.
    erro_simples=sum(r['erro_retro_urna'] for r in ativos1)/len(ativos1)
    efeitos={r['instituto']:r for r in ativos1}
    instituto_out=[]
    for inst,r in sorted(efeitos.items()):
        # Encolhimento dos erros particulares para o erro comum; um pleito NÃO identifica
        # com segurança o house effect permanente. A magnitude shrink é ajustável.
        estimativa=erro_comum+shrink*(r['erro_retro_urna']-erro_comum)
        instituto_out.append({'instituto':inst,'registro_1t':r['registro_tse'],
            'fim_1t':r['fim_campo'],'n_1t':r['amostra'],
            'lula_validos_1t':r['lula_validos'],'flavio_validos_1t':r['flavio_validos'],
            'margem_1t':r['margem_f_menos_l'],'margem_urna':RESULTADO_MARGEM,
            'erro_observado':r['erro_retro_urna'],'peso_1t':r['peso_calibracao'],
            'erro_shrunk':estimativa,'ajuste_2t_por_candidato':alpha*estimativa/2,
            'criterio_validos_1t':r['criterio_validos']})
    ultimo2=ultimo_por_instituto([r for r in segundo if r['ultimo_dia']>=date(2026,10,5)])
    seg_out=[]
    for r in sorted(segundo,key=lambda r:(r['ultimo_dia'],r['instituto'])):
        L,F,criterio=votos_validos(r)
        valid_post=(r['ultimo_dia']>=date(2026,10,5))
        active=valid_post and ultimo2.get(r['instituto']) is r
        p,pr,pn,pm,pmix=peso(r,asof,neutral=neutral,penaliza_misto=True)
        ec=erro_comum+shrink*((efeitos[r['instituto']]['erro_retro_urna']-erro_comum) if r['instituto'] in efeitos else 0)
        correcao=alpha*ec/2
        seg_out.append({**r,'lula_validos':L,'flavio_validos':F,'criterio_validos':criterio,
            'ultimo_2t':int(active),'peso_total':p if active else 0,
            'peso_recencia':pr,'peso_amostra':pn,'peso_metodo':pm,'peso_misto':pmix,
            'margem_f_menos_l':F-L,'erro_1t_shrunk':ec,'correcao_em_f':correcao,
            'flavio_ajustado':F+correcao,'lula_ajustado':L-correcao,
            'presenca_no_1t':int(r['instituto'] in efeitos)})
    ativos2=[r for r in seg_out if r['ultimo_2t']]
    if not ativos2: raise ValueError('Nenhuma pesquisa posterior ao 1º turno na data consultada')
    bruto=media_ponderada([(r['flavio_validos'],r['peso_total']) for r in ativos2])
    simples=sum(r['flavio_validos'] for r in ativos2)/len(ativos2)
    cenarios=[]
    for a in (0,0.25,0.5,0.75,1.):
        fl=media_ponderada([(r['flavio_validos']+a*r['erro_1t_shrunk']/2,r['peso_total']) for r in ativos2])
        cenarios.append({'alpha':a,'flavio_validos':fl,'lula_validos':100-fl,'margem_f_menos_l':2*fl-100})
    ajustado=media_ponderada([(r['flavio_ajustado'],r['peso_total']) for r in ativos2])
    summary={'data_referencia':asof.isoformat(),'voto_urna_flavio':TSE_FLAVIO,
         'voto_urna_lula':TSE_LULA,'margem_urna':RESULTADO_MARGEM,
         'pesquisas_historico_1t':len(primeiro),'institutos_calibrados':len(ativos1),
         'pesquisas_historico_2t':len(segundo),'institutos_agregados_2t':len(ativos2),
         'erro_comum_ponderado':erro_comum,'erro_comum_simples':erro_simples,
         'media_2t_bruta_f':bruto,'media_2t_bruta_l':100-bruto,
         'media_2t_simples_f':simples,'media_2t_simples_l':100-simples,
         'alpha_central':alpha,'shrink_house':shrink,'meia_vida_dias':14,
         'metodo_neutro':neutral,'validos_publicados':publicados,'media_2t_ajustada_f':ajustado,'media_2t_ajustada_l':100-ajustado,
         'margem_ajustada':2*ajustado-100,'margem_bruta':2*bruto-100,
         'cenario_4_07_mecanico_f':bruto+4.07/2,'cenario_4_07_mecanico_l':100-(bruto+4.07/2)}
    return summary,primeiro_out,instituto_out,seg_out,cenarios


def main():
    ap=argparse.ArgumentParser(description='Viés de pesquisas, primeiro para segundo turno 2026')
    ap.add_argument('--dados',type=Path,default=PASTA_PROJETO/'dados'/'brutos'/'pesquisas_2026.csv')
    ap.add_argument('--as-of',default='2026-10-21',help='AAAA-MM-DD, recorte sem lookahead')
    ap.add_argument('--alpha',type=float,default=0.50,help='fração do erro transferida do 1º para o 2º turno; 0 a 1')
    ap.add_argument('--shrink',type=float,default=0.25,help='fração preservada da diferença particular do instituto em relação ao erro comum')
    ap.add_argument('--metodo-neutro',action='store_true',help='desativa penalizações por método de coleta')
    ap.add_argument('--validos-publicados',action='store_true',help='usa no 1º turno os válidos divulgados por Datafolha e Quaest em vez da normalização dos totais')
    ap.add_argument('--saida',type=Path,default=PASTA_PROJETO/'dados'/'resultados')
    args=ap.parse_args()
    # Console do Windows (cp1252) não imprime '→'; força UTF-8 na saída.
    if hasattr(sys.stdout,'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    args.saida.mkdir(parents=True,exist_ok=True)
    resumo,um,vies,dois,cenarios=calcular(ler(args.dados),d(args.as_of),args.alpha,args.shrink,args.metodo_neutro,args.validos_publicados)
    # Deixa apenas campos serializáveis nas planilhas CSV; o arquivo original não é alterado.
    col_1=['instituto','inicio_campo','fim_campo','registro_tse','amostra','base_original','lula_reportado_pct','flavio_reportado_pct','brancos_nulos_pct','indecisos_pct','lula_validos','flavio_validos','margem_f_menos_l','erro_retro_urna','ultima_rodada','peso_calibracao','criterio_validos','fonte']
    col_2=['instituto','inicio_campo','fim_campo','data_divulgacao','registro_tse','amostra','metodo','base_original','lula_reportado_pct','flavio_reportado_pct','lula_validos','flavio_validos','margem_f_menos_l','ultimo_2t','peso_recencia','peso_amostra','peso_metodo','peso_misto','peso_total','erro_1t_shrunk','correcao_em_f','flavio_ajustado','lula_ajustado','presenca_no_1t','fonte']
    grava(args.saida/'primeiro_turno_calculado.csv',um,col_1)
    grava(args.saida/'vies_institutos.csv',vies,list(vies[0].keys()))
    grava(args.saida/'segundo_turno_calculado.csv',dois,col_2)
    grava(args.saida/'cenarios.csv',cenarios,list(cenarios[0].keys()))
    (args.saida/'resultado_modelo.json').write_text(json.dumps(resumo,ensure_ascii=False,indent=2),encoding='utf8')
    print('MODELO ELEITORAL 2026',resumo['data_referencia'])
    print(f"Histórico: {resumo['pesquisas_historico_1t']} pesquisas 1T, {resumo['institutos_calibrados']} institutos com erro calculado; {resumo['institutos_agregados_2t']} institutos ativos no 2T")
    print(f"Margem nas urnas (Flávio-Lula): {RESULTADO_MARGEM:+.2f} pp")
    print(f"Erro comum ponderado do 1T: {resumo['erro_comum_ponderado']:+.2f} pp (média simples {resumo['erro_comum_simples']:+.2f} pp)")
    print(f"Segundo turno sem correção: Flávio {resumo['media_2t_bruta_f']:.2f}%, Lula {resumo['media_2t_bruta_l']:.2f}%")
    print(f"Segundo turno com alfa={args.alpha}, shrink={args.shrink}: Flávio {resumo['media_2t_ajustada_f']:.2f}%, Lula {resumo['media_2t_ajustada_l']:.2f}%")
    print('Cenários (alfa → Flávio %, Lula %):')
    for r in cenarios:print(f"  {r['alpha']:0.2f} → {r['flavio_validos']:0.2f}%, {r['lula_validos']:0.2f}%")
    print('Atenção: diferenças são exercícios condicionais, NÃO probabilidades eleitorais.')

if __name__=='__main__':main()
