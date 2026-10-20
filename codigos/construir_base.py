"""Transcrição rastreável das pesquisas nacionais da eleição presidencial de 2026.
Catálogo: https://e26.cog.ia.br/eleicoes/pesquisas?cargo=presidente
Revisão de 16/10/2026: conferência com E26, Poder360, CNN e Brasil de Fato; +1 pesquisa (Futura BR-03764).
Histórico suplementar: Agregador eleitoral 2026.pdf, enviado pelo usuário.
Valores são percentuais divulgados, não extrapolações do autor deste arquivo.
"""
import csv
from pathlib import Path

OUT=Path(__file__).resolve().parent.parent/'dados'/'brutos'
OUT.mkdir(parents=True,exist_ok=True)
CAT='https://e26.cog.ia.br/eleicoes/pesquisas?cargo=presidente'
# formato: Instituto|inicio|fim|n|Lula|Flavio|registro|base|brancos/nulos|indecisos|método
# registros e números conforme o catálogo de 46 pesquisas E26, 16/10/2026.
DATA_1T='''
Datafolha|2026-08-18|2026-08-20|2058|39|33|BR-04496/2026|totais|7|4|presencial
Indexa|2026-08-20|2026-08-23|2000|39|34|BR-06366/2026|totais|6|6|telefone
PoderData|2026-08-23|2026-08-26|2400|38|35|BR-04974/2026|totais|5|2|telefone
Vox Brasil|2026-08-25|2026-08-27|2100|37.1|34.8|BR-05519/2026|totais|||presencial
AtlasIntel|2026-08-25|2026-08-30|5000|43.4|33.7|BR-07972/2026|totais|||online
Nexus|2026-08-28|2026-08-30|2000|39|33|BR-08900/2026|totais|3|3|telefone
Real Time Big Data|2026-08-27|2026-08-31|2000|38|30|BR-03490/2026|totais|3|3|telefone
Quaest|2026-08-30|2026-09-01|2004|37|29|BR-07065/2026|totais|7|11|presencial
Futura|2026-08-28|2026-09-01|2000|38.7|33.6|BR-02793/2026|totais|2|4.1|telefone
Datafolha|2026-09-01|2026-09-03|2002|38|33|BR-03669/2026|totais|||presencial
Quaest|2026-09-03|2026-09-06|2004|36|29|BR-01720/2026|totais|||presencial
Nexus|2026-09-04|2026-09-07|2000|39|35|BR-06790/2026|totais|3|2|telefone
Ideia|2026-09-04|2026-09-07|1500|38.4|37.3|BR-07935/2026|totais|2.5|2.8|telefone
Gerp|2026-09-03|2026-09-08|2400|34|37|BR-00251/2026|totais|4|8|telefone
Palver|2026-09-04|2026-09-08|5000|40|40|BR-05420/2026|totais|||online
AtlasIntel|2026-09-04|2026-09-09|5000|43|37.4|BR-01452/2026|totais|||online
PoderData|2026-09-06|2026-09-09|3000|38|36|BR-04914/2026|totais|||telefone
Datafolha|2026-09-08|2026-09-11|2002|39|35|BR-01833/2026|totais|6|4|presencial
Quaest|2026-09-10|2026-09-13|2004|36|31|BR-03607/2026|totais|7|10|presencial
Indexa|2026-09-10|2026-09-13|2000|38|34|BR-03482/2026|totais|||telefone
MDA|2026-09-09|2026-09-13|2002|40.5|30.4|BR-06902/2026|totais|6|7.5|presencial
Gerp|2026-09-14|2026-09-16|2400|37|40|BR-00535/2026|totais|4|4|telefone
AtlasIntel|2026-09-11|2026-09-16|5000|44.1|41.7|BR-06221/2026|totais|||online
Futura|2026-09-11|2026-09-17|2000|38.3|37.7|BR-00749/2026|totais|||telefone
Datafolha|2026-09-15|2026-09-17|2002|39|36|BR-04029/2026|totais|6|3|presencial
Nexus|2026-09-18|2026-09-20|2000|40|37|BR-00485/2026|totais|4|2|telefone
Quaest|2026-09-17|2026-09-20|2004|37|33|BR-06004/2026|totais|7|8|presencial
AtlasIntel|2026-09-17|2026-09-22|5000|45.8|43.4|BR-04739/2026|totais|0.7|0.5|online
PoderData|2026-09-20|2026-09-23|3000|41|39|BR-01739/2026|totais|||telefone
Real Time Big Data|2026-09-19|2026-09-23|2000|41|37|BR-04202/2026|totais|3|3|telefone
Palver|2026-09-20|2026-09-23|5000|43|43|BR-09587/2026|totais|1|1|online
Datafolha|2026-09-22|2026-09-24|2002|40|36|BR-00304/2026|totais|5|2|presencial
Futura|2026-09-18|2026-09-24|2000|38.4|40.4|BR-05268/2026|totais|2.1|3.2|telefone
Nexus|2026-09-25|2026-09-27|2000|42|37|BR-07557/2026|totais|3|2|telefone
Ideia|2026-09-25|2026-09-28|2000|39.4|38.4|BR-08706/2026|totais|0.7|1.5|telefone
Indexa|2026-09-27|2026-09-29|2000|39|34|BR-00698/2026|totais|8|7|telefone
Futura|2026-09-24|2026-09-29|2000|39.4|42.2|BR-01122/2026|totais|2.4|2.6|telefone
Real Time Big Data|2026-09-26|2026-09-30|2000|43|39|BR-09503/2026|totais|3|3|telefone
Vox Brasil|2026-09-29|2026-10-01|2100|40.4|41.2|BR-00148/2026|totais|3.2|7|presencial
Gerp|2026-09-30|2026-10-02|2400|44|46|BR-00509/2026|validos|||telefone
AtlasIntel|2026-09-27|2026-10-02|5000|46.7|43.8|BR-00999/2026|totais|0.3|0.3|online
PoderData|2026-09-30|2026-10-02|4000|42|41|BR-03519/2026|totais|4|2|telefone
MDA|2026-09-29|2026-10-02|2002|43.1|38|BR-04756/2026|totais|5|4.7|presencial
Palver|2026-09-30|2026-10-03|5000|43|47|BR-00198/2026|totais|||online
Datafolha|2026-10-03|2026-10-03|4006|42|40|BR-01708/2026|totais|4|3|presencial
Quaest|2026-10-02|2026-10-03|3702|40|38|BR-02197/2026|totais|10|3|presencial
'''
# Segundo turno: pesquisas do acervo público e novas divulgações até 16/10.
# Evita linhas duplicadas com a mesma combinação instituto/registro, inclusive revisões do chat.
# método poderá ser desconhecido; não se infere precisão estatística da amostra digital.
DATA_2T='''
Nexus|2026-09-25|2026-09-27|2000|46|44|BR-07557/2026|totais|8|1|telefone
Ideia|2026-09-25|2026-09-28|2000|48.5|48|BR-08706/2026|totais|2.1|1.5|telefone
Futura|2026-09-24|2026-09-29|2000|43.5|49|BR-01122/2026|totais|6.2|1.3|telefone
Indexa|2026-09-27|2026-09-29|2000|43|42|BR-00698/2026|totais|11|4|telefone
Real Time Big Data|2026-09-26|2026-09-30|2000|45|46|BR-09503/2026|totais|5|4|telefone
Vox Brasil|2026-09-29|2026-10-01|2100|45.2|48.2|BR-00148/2026|totais|2.5|4.1|presencial
MDA|2026-09-29|2026-10-02|2002|47.3|43.1|BR-04756/2026|totais|7.6|1.9|presencial
PoderData|2026-09-30|2026-10-02|4000|46|46|BR-03519/2026|totais|7|1|telefone
AtlasIntel|2026-09-27|2026-10-02|5000|47.6|47.4|BR-00999/2026|totais|5||online
Palver|2026-09-30|2026-10-03|5000|44|49|BR-00198/2026|totais|6|1|online
Datafolha|2026-10-03|2026-10-03|4006|47|46|BR-01708/2026|totais|6|2|presencial
Quaest|2026-10-02|2026-10-03|3702|42|44|BR-02197/2026|totais|13|1|presencial
PoderData|2026-10-05|2026-10-07|3000|47|53|BR-08134/2026|validos|||telefone
Datafolha|2026-10-06|2026-10-08|2520|45|49|BR-02949/2026|totais|5|1|presencial
Vox Brasil|2026-10-05|2026-10-07|2100|44.2|42.7|BR-09623/2026|totais|3.4|9.7|presencial
Ipespe|2026-10-06|2026-10-08|1500|44|49|BR-00933/2026|totais|5|3|telefone
AtlasIntel|2026-10-03|2026-10-08|5026|45.7|51.1|BR-03663/2026|totais|3.2||online
DataTrends|2026-10-07|2026-10-09|2000|46.9|53.1|BR-03576/2026|validos|||nao_informado
Futura|2026-10-07|2026-10-10|2000|46.6|50|BR-00650/2026|totais|1.7|1.7|telefone
Gerp|2026-10-08|2026-10-12|2400|44|53|BR-07877/2026|totais|1|3|telefone
Nexus|2026-10-10|2026-10-12|2002|45|48|BR-07997/2026|totais|||telefone
PoderData|2026-10-10|2026-10-12|3000|49|51|BR-01209/2026|validos|||telefone
Quaest|2026-10-10|2026-10-13|2154|44|46|BR-08729/2026|totais|9|1|presencial
Indexa|2026-10-13|2026-10-14|2000|42|44|BR-04629/2026|totais|12|2|telefone
Datafolha|2026-10-13|2026-10-14|2520|45|47|BR-00466/2026|totais|||presencial
Palver|2026-10-10|2026-10-14|5000|49|50|BR-08028/2026|totais|1|0|online
PoderData|2026-10-13|2026-10-15|3000|50|50|BR-04258/2026|validos|||telefone
MDA|2026-10-13|2026-10-15|2014|49.5|50.5|BR-00652/2026|validos|||presencial
Futura|2026-10-14|2026-10-15|2000|47.5|49|BR-03764/2026|totais|3.6||telefone
'''

def number(s): return float(s) if s.strip() else ''

def parse(text,turno):
  rows=[]
  for line in text.strip().splitlines():
    a=line.strip().split('|')
    if len(a)!=11: raise ValueError((len(a),line))
    instit,ini,fim,n,l,f,reg,base,bn,ns,modo=a
    rows.append({'turno':turno,'instituto':instit,'inicio_campo':ini,'fim_campo':fim,
      'data_divulgacao':'', 'amostra':int(n),'lula_reportado_pct':float(l),'flavio_reportado_pct':float(f),
      'registro_tse':reg,'base_original':base,'brancos_nulos_pct':number(bn),
      'indecisos_pct':number(ns),'metodo':modo,'fonte':CAT,'observacao':''})
  return rows

rows=parse(DATA_1T,'1')+parse(DATA_2T,'2')
assert len([r for r in rows if r['turno']=='1'])==46
# Datas de divulgação do 2º turno pós-eleição (revisão de 16/10/2026: catálogo E26,
# Poder360 "a 9 dias do 2º turno", CNN Brasil, Brasil de Fato). Usadas pelo modelo
# para o recorte --as-of sem lookahead.
DIVULGACAO_2T={'BR-08134/2026':'2026-10-08','BR-02949/2026':'2026-10-08','BR-09623/2026':'2026-10-09',
  'BR-00933/2026':'2026-10-10','BR-03663/2026':'2026-10-09','BR-03576/2026':'2026-10-11',
  'BR-00650/2026':'2026-10-13','BR-07877/2026':'2026-10-13','BR-07997/2026':'2026-10-13',
  'BR-01209/2026':'2026-10-13','BR-08729/2026':'2026-10-14','BR-04629/2026':'2026-10-15',
  'BR-00466/2026':'2026-10-15','BR-08028/2026':'2026-10-15','BR-04258/2026':'2026-10-16',
  'BR-00652/2026':'2026-10-16','BR-03764/2026':'2026-10-16'}
for r in rows:
  if r['turno']=='2': r['data_divulgacao']=DIVULGACAO_2T.get(r['registro_tse'],'')
assert len(set((r['turno'],r['instituto'],r['registro_tse'],r['fim_campo']) for r in rows))==len(rows)
for r in rows:
  if r['turno']=='1' and r['registro_tse']=='BR-00198/2026':
    r['observacao']='Brancos/nulos e indecisos não quantificados (<1% cada); percentuais em votos totais; usar aproximação validada separadamente.'
  if r['turno']=='1' and r['registro_tse']=='BR-01708/2026':
    r['observacao']='Datafolha publicou 45% Lula e 42% Flávio em votos válidos; conversão aritmética dos votos totais difere devido a arredondamentos/metodologia.'
  if r['turno']=='1' and r['registro_tse']=='BR-02197/2026':
    r['observacao']='Quaest publicou votos válidos com modelo likely voter (Lula 46% / Flávio 45%); normalização direta dos totais gera resultado diferente.'
  if r['turno']=='2' and r['registro_tse']=='BR-03663/2026':
    r['observacao']='Coleta começa ANTES do primeiro turno em 04/10; aplicar penalidade para campo misto. BN 3,2% inclui indecisos.'
  if r['turno']=='2' and r['registro_tse']=='BR-04629/2026':
    r['observacao']='BN 4%, NS 2%, não votar 8%; base de válidos deve ser F/(F+L), não 100-BN-NS.'
  if r['turno']=='2' and r['registro_tse']=='BR-08028/2026':
    r['observacao']='Cadastro TSE mostra campo até 14/10; fonte de divulgação informa até 13/10; nova calibragem por região x voto do 1º turno.'
  if r['turno']=='2' and r['registro_tse']=='BR-00466/2026':
    r['fonte']='https://www1.folha.uol.com.br/poder/2026/10/datafolha-flavio-bolsonaro-tem-51-e-lula-49-dos-votos-validos-um-empate-tecnico.shtml'
  if r['turno']=='2' and r['registro_tse']=='BR-00652/2026':
    r['fonte']='https://noticias.uol.com.br/eleicoes/2026/10/16/cntmda-pesquisa-presidencial-2-turno.ghtm'
  if r['turno']=='2' and r['registro_tse']=='BR-03764/2026':
    r['fonte']='https://www.cnnbrasil.com.br/eleicoes/futura-flavio-tem-508-dos-votos-validos-no-2o-turno-lula-492/'
    r['observacao']='Incluída em 16/10. BN 3,6% soma brancos, nulos e indecisos; válidos publicados 50,8% Flávio x 49,2% Lula.'
  if r['turno']=='2' and r['registro_tse']=='BR-02949/2026':
    r['fonte']='https://www.brasildefato.com.br/2026/10/08/datafolha-segundo-turno-flavio-bolsonaro-49-lula-45/'
    r['observacao']='Fim do campo corrigido de 07/10 para 08/10 (revisão de 16/10).'
  if r['turno']=='2' and r['registro_tse']=='BR-00466/2026':
    r['observacao']='Poder360 informa campo 13-14/10; cadastro no catálogo E26 indica até 15/10.'
  if r['turno']=='2' and r['registro_tse']=='BR-04258/2026':
    r['fonte']='https://www.poder360.com.br/poderdata/pesquisa-poderdata-aya-leia-resultados-de-lula-e-flavio-no-2o-turno/'
fields=['turno','instituto','inicio_campo','fim_campo','data_divulgacao','amostra','lula_reportado_pct','flavio_reportado_pct','registro_tse','base_original','brancos_nulos_pct','indecisos_pct','metodo','fonte','observacao']
with (OUT/'pesquisas_2026.csv').open('w',newline='',encoding='utf-8-sig') as h:
 w=csv.DictWriter(h,fieldnames=fields);w.writeheader();w.writerows(rows)
print(f'Gravado em {OUT/"pesquisas_2026.csv"}')
print(f'Pesquisas: {len(rows)} ({sum(r["turno"]=="1" for r in rows)} de 1º turno e {sum(r["turno"]=="2" for r in rows)} de 2º turno)')
