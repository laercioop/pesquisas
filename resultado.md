# Agregador Eleitoral 2026 — resultado

**Recorte:** 23/10/2026 · **Unidade:** % dos votos válidos · 2º turno em 25/10/2026 ·
**Versão interativa:** [`agregador.html`](agregador.html)

## Resumo

Com base em **17 institutos** e na rodada mais recente de cada um, o 2º turno está assim:

| Cenário | Flávio | Lula | Margem |
|---|---|---|---|
| Pesquisas como publicadas (alfa 0) | **50,9%** | **49,1%** | +1,8 pp |
| Central: repete metade do erro do 1º turno (alfa 0,5) | **51,8%** | **48,2%** | +3,5 pp |
| Repete todo o erro do 1º turno (alfa 1) | **52,6%** | **47,4%** | +5,2 pp |

No 1º turno (04/10), as pesquisas subestimaram Flávio em **3,4 pp na margem** (média ponderada
da última rodada de cada instituto; Flávio teve 47,03% e Lula 45,16% nas urnas). O modelo pergunta
quanto desse erro se repete no 2º turno. Isso é uma **hipótese**, não uma probabilidade de vitória.

**Atualização de 23/10.** Entraram 9 pesquisas divulgadas de 20 a 23/10: Alfa Inteligência,
Veritá, Futura, Palver, Gerp, Indexa, PoderData, Datafolha e Vox Brasil. A base tem 96 pesquisas
(46 do 1º turno e 50 do 2º) e 17 institutos ativos no agregado. A tendência em 22/10 ficou em
Flávio 50,7 × Lula 49,3; com a correção de viés, 52,5 × 47,5. O cenário central é 51,76 × 48,24.
Foram usados os totais quando disponíveis: Datafolha e PoderData publicam válidos arredondados
que diferem da normalização aritmética dos totais. Campos divergentes de Gerp e Palver e o método
não informado da Veritá estão documentados em `observacao`. A Vox foi publicada pela CNN em 23/10
às 00h. Registros com divulgação prevista, sem resultados localizados, não foram incluídos.
Fontes: [CNN/Vox](https://www.cnnbrasil.com.br/eleicoes/vox-lula-tem-506-dos-votos-validos-no-2o-turno-flavio-494/),
[UOL/Datafolha](https://noticias.uol.com.br/eleicoes/2026/10/22/pesquisa-datafolha-hoje-2210-veja-numeros-de-lula-x-flavio-no-segundo-turno.ghtm)
e links individuais no CSV e em `construir_base.py`.

**Atualização de 21/10.** Entraram 3 pesquisas: Gerp (tracking de 15 a 19/10, 53×47 nos válidos),
Meio/Ideia (15 a 19/10, 51,1×48,9) e Quaest (17 a 20/10, 45×44 nos totais, ou 50,6×49,4 nos válidos).
A Ideia volta ao agregado do 2º turno, que passa a ter 15 institutos. A tendência ficou em Flávio 51,4 × Lula 48,6
em 20/10, ou 53,1 × 46,9 com a correção de viés. O cenário central do modelo segue em 51,9%. O registro TSE
da rodada da Gerp não foi localizado nas matérias; ver `observacao` no CSV.

**Atualização de 20/10.** Entraram 9 pesquisas divulgadas entre 16 e 20/10: Gerp (52×48 nos válidos),
Ipespe (51,2×48,8), Vox Brasil (49×51, a única com Lula à frente), AtlasIntel (51,1×48,9), PoderData
(52×48), Nexus (50,3×49,7), Futura (50,4×49,6), DataTrends (51,5×48,5) e Real Time Big Data (52×48).
A tendência, que vinha convergindo para 50×50, parou de cair: Flávio 51,2 × Lula 48,8 em 19/10, ou
52,9 × 47,1 somando metade do erro médio do 1º turno. O cenário central do modelo foi de 52,1% (16/10)
para 51,9%. Os válidos de sete delas vêm do agregado do Poder360 (totais não conferidos) e a data de
divulgação de algumas é aproximada; ver `observacao` no CSV.

Os gráficos preliminares em PNG abaixo são o retrato de 16/10; os PNGs/SVGs finais locais seguem em 20/10. Os números atualizados estão em `agregador.html`.

## O que foi feito

1. **Revisão do projeto.** Os números do LEIA-ME e do Excel reproduzem a partir do código. Os
   problemas encontrados foram corrigidos:
   - o script quebrava no console do Windows (caractere `→`);
   - a última rodada do 1º turno sem denominador descartava o instituto inteiro, e agora usa
     a rodada anterior;
   - o recorte `--as-of` usava o fim do campo e passou a usar a **data de divulgação**, sem lookahead;
   - o LEIA-ME descrevia errado o que `Painel!B7` recalcula no Excel.
2. **Atualização da base**, conferida com o catálogo E26, o agregado do Poder360 (16/10), CNN Brasil
   e Brasil de Fato:
   - **pesquisa nova:** Futura/100% Cidades (BR-03764/2026, 14–15/10, divulgada em 16/10), com
     Flávio 49% × Lula 47,5% nos totais e 50,8 × 49,2 nos válidos;
   - **Datafolha BR-02949:** o fim do campo foi corrigido de 07/10 para 08/10;
   - **AtlasIntel BR-03663** passou a ter amostra de 5.026, e **Nexus BR-07997**, de 2.002;
   - foram preenchidas as datas de divulgação de todas as pesquisas do 2º turno pós-eleição;
   - **conferidas e sem mudança:** PoderData 13–15/10 (50×50), MDA 13–15/10, Datafolha, Indexa e
     Palver (divulgadas em 15/10) e Quaest (14/10).
   - Até a revisão, nenhuma outra pesquisa nacional tinha sido divulgada em 15–16/10. A AtlasIntel
     (BR-02418, campo 13–18/10) deve sair em 19/10.
3. **Nova opção `--validos-publicados`.** Ela usa os válidos divulgados por Datafolha e Quaest no
   1º turno em vez de recalculá-los a partir dos totais. O efeito é pequeno: o erro comum vai de
   3,37 para 3,32 pp.
4. **Reorganização** em `dados/`, `codigos/` e `graficos/`. O ZIP original foi mantido intacto na
   raiz. A documentação técnica completa está em `codigos/LEIA-ME.md`.

## Gráficos

**1. O erro do 1º turno.** Quase todas as últimas rodadas mostravam Lula à frente; Flávio venceu por 1,87 pp.

![Margem no 1º turno](graficos/analises%20preliminares/01_primeiro_turno_margem.png)

**2. Erro por instituto.** Indexa, MDA e Nexus erraram mais de 7 pp. Palver, Futura e Gerp
superestimaram Flávio.

![Erro por instituto](graficos/analises%20preliminares/2_erro_por_instituto_1t.png)

**3. Pesquisas do 2º turno.** A vantagem de Flávio caiu de cerca de 53% logo após o 1º turno para
cerca de 50,5% nas rodadas mais recentes.

![Série do 2º turno](graficos/analises%20preliminares/03_segundo_turno_serie.png)

**3b. Tendência com projeção para 25/10.** A linha é uma regressão local ponderada pela amostra,
com janela de cerca de 3 dias. A faixa sombreada mostra onde cairiam 95% das pesquisas. A projeção
congela a tendência atual (Flávio 50,5 × Lula 49,5), **sem correção de viés**, e soma duas fontes de
incerteza: mudança de opinião até a eleição (0,35 pp/dia) e um erro comum das pesquisas (2 pp). O
intervalo de 95% resultante vai de 46 a 55% para Flávio. Esses parâmetros são hipóteses ilustrativas,
definidas em `codigos/graficos.py`.

![Tendência pós-eleição](graficos/analises%20preliminares/07_tendencia_2t_pos_eleicao.png)

O gráfico abaixo inclui também as pesquisas de 2º turno feitas antes do 1º turno (27/09 a 03/10),
com a tendência estimada separadamente em cada período. Antes da eleição havia empate (~50×50).
Depois de 04/10, Flávio salta para cerca de 52% e volta a convergir para 50%. Os pontos à direita
somam à tendência atual o erro médio do 1º turno (+3,37 pp na margem, ou seja, +1,7 pp para Flávio):
**Flávio 52,2% × Lula 47,8%**.

![Tendência com todas as pesquisas](graficos/analises%20preliminares/8_tendencia_2t_todas.png)

**4. Rodada atual de cada instituto,** como publicada e corrigida. Só a Vox Brasil (de 07/10) tem
Lula à frente.

![Institutos no 2º turno](graficos/analises%20preliminares/04_institutos_2t_bruto_vs_ajustado.png)

**5. Cenários por alfa.**

![Cenários](graficos/analises%20preliminares/05_cenarios_alfa.png)

**6. Sensibilidade.** A hipótese que mais pesa é o **alfa**, ou seja, quanto do erro se repete.
Fator de método, shrink e critério de válidos mudam a margem em menos de 0,1 pp.

![Sensibilidade](graficos/analises%20preliminares/06_sensibilidade.png)

## Limitações

- O modelo foi calibrado com **um único pleito**. Não há evidência de que o erro do 1º turno se
  repita no 2º com a mesma magnitude. A Palver, por exemplo, mudou sua calibração depois do 1º turno.
- O modelo não produz intervalos de confiança nem probabilidades de vitória.
- A base é uma transcrição de catálogos e imprensa. Antes de uso acadêmico ou publicação, confira
  com os relatórios originais e os registros no TSE.
- O Excel (`dados/agregador_eleitoral_2026_auditavel.xlsx`) é um retrato **anterior** a esta
  revisão. Os números atualizados estão nos CSVs de `dados/resultados/`.

## Como reproduzir

```bash
cd codigos
python modelo_vies.py      # recalcula dados/resultados/
python graficos.py         # regenera graficos/ e sensibilidade.csv
python graficos_ps.py      # gráficos 2 e 8 no estilo P&S
python gerar_html.py       # agregador.html (interativo)
```
