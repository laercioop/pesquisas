# Agregador Eleitoral 2026 — acervo local e modelo auditável

**Data de corte:** 23 de outubro de 2026. **Unidade:** votos percentuais válidos,
salvo quando especificado `totais`. O arquivo `dados/brutos/pesquisas_2026.csv` é o banco primário
editável; não depende de uma conversa do ChatGPT.

## Estrutura

```
agregador de pesquisas/
├── resultado.md                       resumo do que foi feito e dos resultados
├── modelo_pesquisas_eleitorais_2026.zip   pacote original (versão de 16/10, antes da revisão)
├── dados/
│   ├── brutos/pesquisas_2026.csv      banco primário editável (96 pesquisas: 46 do 1T, 50 do 2T)
│   ├── resultados/                    saídas geradas pelos scripts
│   │   ├── primeiro_turno_calculado.csv   normalização e erro de cada pesquisa do 1T
│   │   ├── vies_institutos.csv            erro da última rodada de cada instituto e efeito encolhido
│   │   ├── segundo_turno_calculado.csv    todas as rodadas do 2T; ultimo_2t=1 entra no agregado
│   │   ├── cenarios.csv                   agregado do 2T para alfa = 0; 0,25; 0,5; 0,75; 1
│   │   ├── sensibilidade.csv              resultado sob hipóteses alternativas
│   │   └── resultado_modelo.json          resumo numérico
│   └── agregador_eleitoral_2026_auditavel.xlsx   painel Excel (retrato ANTERIOR à revisão de 16/10)
├── codigos/
│   ├── LEIA-ME.md                     este arquivo
│   ├── construir_base.py              transcrição documentada que gera dados/brutos/pesquisas_2026.csv
│   ├── modelo_vies.py                 modelo (só biblioteca padrão)
│   └── graficos.py                    gráficos e tabela de sensibilidade (requer matplotlib)
└── graficos/                          1 e 2 (PNG; svg/ PT+EN) de graficos_ps.py; analises preliminares/ de graficos.py
```

## Como executar

Python 3; `graficos.py` precisa de matplotlib. Dentro de `codigos/`:

```bash
python construir_base.py          # só se alterar a transcrição; regrava o CSV bruto
python modelo_vies.py             # padrão: --as-of 2026-10-23 --alpha 0.5 --shrink 0.25
python graficos.py                # PNGs em ../graficos e sensibilidade.csv
```

Variações úteis:

```bash
python modelo_vies.py --alpha 0
python modelo_vies.py --alpha 1
python modelo_vies.py --metodo-neutro
python modelo_vies.py --validos-publicados   # válidos divulgados por Datafolha e Quaest no 1T
python modelo_vies.py --as-of 2026-10-15     # recorte por data de DIVULGAÇÃO (sem lookahead)
```

Os scripts regravam os arquivos de `dados/resultados/` e não alteram o CSV bruto
(exceto `construir_base.py`, que o gera). Para incluir pesquisas novas, acrescente
a linha em `construir_base.py` (fonte da verdade; o CSV é regravado) e rode os scripts (`construir_base.py`, `modelo_vies.py`, `gerar_html.py`).

**Excel:** é um retrato estático. `Painel!B7` (alfa) recalcula B11, B13 e B14
(agregado com viés); a aba `Cenarios` usa alfas fixos e não depende de B7. As
linhas importadas não acompanham alterações no CSV. A planilha não inclui a
revisão de 16/10 (Futura BR-03764 e correções de campo/amostra).

## Definições matemáticas

Nas eleições de 4/10/2026, o resultado oficial utilizado foi 47,03% dos votos
válidos para Flávio e 45,16% para Lula. Portanto, a margem **Flávio − Lula**
foi **+1,87 ponto percentual**.

Para a última pesquisa comparável do instituto `i` no primeiro turno:

    margem_pesquisa_i = flavio_validos_i - lula_validos_i
    erro_i = 1.87 - margem_pesquisa_i

Peso da rodada na calibração:

    peso_i = 2 ** (-dias_ate_04_10/14) * sqrt(min(n_i, 4000)/2000) * fator_metodo_i

Fatores ilustrativos de método: presencial 1, telefone 0,9,
online 0,7, misto 0,85, não informado 0,75. São hipóteses,
não classificações empiricamente comprovadas de qualidade.

    erro_comum = sum(peso_i * erro_i) / sum(peso_i)
    erro_encolhido_i = erro_comum + shrink * (erro_i - erro_comum)
    flavio_2t_ajustado_i = flavio_2t_validos_i + alpha * erro_encolhido_i / 2
    lula_2t_ajustado_i = 100 - flavio_2t_ajustado_i

Padrões adotados: `alpha = 0.5` e `shrink = 0.25`.
Alfa é a hipótese de **quantos % do erro histórico da margem** ainda prevalecem
no segundo turno; não confundir com probabilidade de vitória. O efeito específico
de cada instituto sofre encolhimento, dado que há apenas um pleito de referência.

O agregado do segundo turno usa a última rodada **após a eleição** de cada
instituto, pesos de recência (meia-vida de 14 dias), amostra e método. A
Atlas com entrevistas iniciadas antes da eleição recebe desconto de
amostra mista temporal. Percentuais de dois candidatos são normalizados para
somarem 100%.

## Principais resultados (23/10/2026, com 9 pesquisas adicionais divulgadas de 20 a 23/10)

- Calibração: 13 institutos; erro comum ponderado de **+3,37 pp na margem** (média simples +3,45 pp).
- Segundo turno, 17 institutos, sem transferir erro (`alpha=0`): **Flávio 50,92% × Lula 49,08%**.
- Metade do erro (`alpha=0.5`): **Flávio 51,76% × Lula 48,24%**.
- Erro integral (`alpha=1`): **Flávio 52,60% × Lula 47,40%**.
- Estes são **cenários condicionais**, não probabilidades de vitória. Ver `resultado.md` e `agregador.html` na raiz.

## Proveniência e limitações

O histórico original em `Agregador eleitoral 2026.pdf` (não incluído nesta pasta) descreve o agregador,
a metodologia de ponderação e uma conta curta de erro de +4,07 pp de margem,
mas **não contém um script original completo salvo nem os bytes das planilhas
Excel anteriores**. O presente `modelo_vies.py` é uma **nova implementação
reprodutível** inspirada no histórico, não um resgate literal do código anterior.

Fonte principal para a transcrição das 46 rodadas históricas de primeiro turno
e parte das pesquisas de segundo turno:
https://e26.cog.ia.br/eleicoes/pesquisas?cargo=presidente

Outros resultados e documentos, inclusive:
https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/flavio-bolsonaro-e-lula-vao-disputar-o-2o-turno-para-a-presidencia-da-republica
https://www.poder360.com.br/poderdata/pesquisa-poderdata-aya-leia-resultados-de-lula-e-flavio-no-2o-turno/
https://www.placardaspesquisas.com.br/presidente

As fontes estão vinculadas linha a linha ao banco bruto e aos CSVs calculados.
A transcrição é uma reconstrução preliminar e deve ser confrontada com os
relatórios originais de cada pesquisa e com os respectivos registros do TSE
antes de utilização acadêmica ou publicação.

**Cobertura:** as 46 pesquisas do primeiro turno compreendem agosto a outubro
de 2026. Não são todas as pesquisas do ano ou todas as pesquisas regionais.
Uma pesquisa sem a base necessária para conversão em votos válidos
fica registrada mas **não entra na calibração**, em vez de se imputar denominador.

O erro de uma pesquisa perto do dia da eleição combina possíveis efeitos
de instituto, não resposta, mudança tardia de preferência e comparecimento.
Não há identificação causal nem evidência de que ele se repetirá na mesma
magnitude no segundo turno. A Palver mudou sua calibração após o primeiro
turno; sua comparação requer cuidado adicional. Pesquisas de partidos,
candidatos, métodos e momentos distintos podem ter relações diferentes
entre erro de primeiro e segundo turno.

O modelo não calcula intervalos probabilísticos calibrados, nem probabilidades
de vitória. Altere alfa e fatores para testar a sensibilidade, não para
declarar que existe viés estável estabelecido.
