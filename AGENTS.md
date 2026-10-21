# AGENTS.md

Orientações para agentes de código (Claude Code, Codex, Gemini CLI etc.) que trabalham neste projeto.

## O que é

Agregador das pesquisas da eleição presidencial de 2026 (Lula x Flávio Bolsonaro). O projeto calibra o erro das pesquisas no 1º turno (04/10/2026) contra o resultado do TSE (Flávio 47,03% x Lula 45,16% dos válidos, margem +1,87 pp) e aplica parte desse erro ao agregado do 2º turno (25/10/2026). O resultado são **cenários condicionais**, não probabilidades de vitória.

- **Documentação técnica** (fórmulas, fontes e limitações): `codigos/LEIA-ME.md`.
- **Resumo dos resultados para leitura:** `resultado.md`.
- **Versão interativa:** `agregador.html`.

Python 3.9 (Anaconda); não há testes nem lint. O usuário escreve em português, e textos, nomes, gráficos e mensagens de commit seguem em português.

## Estado atual (revisão de 21/10/2026)

- **Base:** 87 pesquisas, 46 do 1º turno e 41 do 2º. 13 institutos calibrados no 1T e 15 ativos no 2T.
- **Erro do 1T, na margem:** média ponderada +3,37 pp e média simples +3,45 pp.
- **Cenários do modelo (Flávio x Lula):** alfa 0 dá 51,01 x 48,99; alfa 0,5 dá 51,86 x 48,14; alfa 1 dá 52,70 x 47,30.
- **Tendência (gráfico 2):** Flávio 51,4 em 20/10, ou 53,1 x 46,9 com a correção de viés.
- **Arquivos em dia com 21/10:** `agregador.html`, CSVs de `dados/resultados/`, `resultado.md` e `LEIA-ME.md`.
- **Arquivos parados em 20/10:** PNGs e SVGs finais (`graficos_ps.py` e `graficos_ps_st.py` não foram rodados).
- **Arquivos parados em 16/10:** `graficos/analises preliminares/` e `dados/resultados/sensibilidade.csv`, porque o `graficos.py` não foi rodado.

## Estrutura

```
agregador.html                 página interativa (GERADA por codigos/gerar_html.py; não editar)
resultado.md                   resumo para leitura
modelo_pesquisas_eleitorais_2026.zip   pacote original; intocado
codigos/
  construir_base.py            FONTE DA VERDADE dos dados -> dados/brutos/pesquisas_2026.csv
  modelo_vies.py               modelo (só biblioteca padrão) -> dados/resultados/*.csv, resultado_modelo.json
  graficos.py                  análises preliminares + tendencia(), MARCADOR, NOME_METODO
  graficos_ps.py               gráficos finais 1 e 2 (estilo P&S) em PNG + SVG PT/EN
  graficos_ps_st.py            os mesmos SVGs sem título (_st, _st_en)
  template.py                  cópia da skill estilo-ps
  gerar_html.py                calcula os dados e injeta no molde -> agregador.html
  html_molde.html              HTML/CSS/JS dos gráficos interativos (editar AQUI)
  LEIA-ME.md                   documentação técnica
dados/brutos/pesquisas_2026.csv
dados/resultados/              saídas do modelo
dados/agregador_eleitoral_2026_auditavel.xlsx   retrato estático anterior a 16/10; nenhum script gera
graficos/1_*.png, 2_*.png      gráficos finais; graficos/svg/ (PT, _en, _st, _st_en)
graficos/analises preliminares/   gráficos antigos (o 2 e o 8 são retratos estáticos com média ponderada)
```

## Comandos (rodar de dentro de `codigos/`)

```bash
python construir_base.py    # regrava o CSV bruto a partir da transcrição no próprio script
python modelo_vies.py       # recalcula dados/resultados/ (padrão: --as-of 2026-10-20 --alpha 0.5 --shrink 0.25)
python gerar_html.py        # agregador.html na raiz
python graficos_ps.py       # PNG finais 1 e 2 na raiz de graficos/ + SVG PT e _en em graficos/svg/
python graficos_ps_st.py    # SVG sem título (_st, _st_en)
python graficos.py          # análises preliminares + sensibilidade.csv (só quando pedido)
```

Opções do modelo: `--alpha` (fração do erro do 1T transferida, de 0 a 1), `--shrink` (peso do erro próprio de cada instituto em relação ao comum), `--metodo-neutro`, `--validos-publicados` (usa no 1T os válidos divulgados por Datafolha e Quaest) e `--as-of AAAA-MM-DD`. O `--as-of` padrão aparece em **quatro lugares** (`modelo_vies.py`, `graficos.py`, `graficos_ps.py` e `gerar_html.py`, nos argparse e nas docstrings). Ao mudar a data de referência, mude nos quatro.

## Rotina de atualização (pesquisas novas)

1. **Buscar as pesquisas** divulgadas desde a última revisão. A data da última revisão está no docstring de `construir_base.py`. Fontes que funcionaram:
   - **Poder360:** o agregado diário "Saiba como estão Lula e Flávio nas pesquisas a N dias…" lista instituto, campo, registro, amostra e válidos.
   - **Catálogo E26** (`https://e26.cog.ia.br/eleicoes/pesquisas?cargo=presidente`): tem os registros, mas as rodadas recentes costumam aparecer só como "só registro", sem números.
   - **Matérias dos institutos ou da imprensa:** Gazeta do Povo, CNN, Folha etc.
   
   Prefira os votos totais (com BN e NS) quando a fonte trouxer. Se só houver válidos, use `base=validos`.
2. **Editar `construir_base.py`:**
   - acrescente a linha em `DATA_2T` (ou `DATA_1T`), no formato `Instituto|inicio|fim|n|Lula|Flavio|registro|base|BN|NS|metodo`. Use o nome do instituto igual ao das rodadas anteriores (ex.: "Nexus", não "BTG/Nexus"), porque o modelo agrupa por nome;
   - inclua a data em `DIVULGACAO_2T`. Sem ela, o recorte `--as-of` usa o fim do campo;
   - preencha `fonte` e `observacao` no laço de ajustes. Registre ali quando os números vierem de agregador (totais não conferidos) ou quando a data de divulgação for aproximada.
3. **Rodar** `construir_base.py`, `modelo_vies.py` e `gerar_html.py`, e regenerar os PNGs/SVGs (`graficos_ps.py` e `graficos_ps_st.py`) se o usuário pedir. Se a data de referência mudar, atualize o `--as-of` padrão nos quatro scripts.
4. **Atualizar os textos:**
   - em `resultado.md`, o cabeçalho, a tabela de cenários e o parágrafo da atualização;
   - em `codigos/LEIA-ME.md`, a seção "Principais resultados";
   - em `AGENTS.md`, a seção "Estado atual".
5. **Conferir:** abra o PNG do gráfico 2 (sobreposição de rótulos) e o HTML no navegador (ver Armadilhas).

## Arquitetura

### Dados (`construir_base.py`)
- **Fonte da verdade:** as strings `DATA_1T`/`DATA_2T`, o dict `DIVULGACAO_2T` e o laço de ajustes de `fonte`/`observacao`, e não o CSV. Editar só o CSV se perde quando o `construir_base.py` roda de novo.
- **Asserts:** o script exige exatamente 46 pesquisas de 1T e nenhuma duplicata de (turno, instituto, registro, fim).
- **BN no 2T:** às vezes soma brancos, nulos e "nenhum"/indecisos. Isso não afeta o 2T, que normaliza só pelos dois candidatos.

### Modelo (`modelo_vies.py`)
Usa só a biblioteca padrão. `calcular(data, asof, alpha, shrink, neutral, publicados)` devolve `(resumo, primeiro_out, instituto_out, seg_out, cenarios)`. `graficos.py`, `graficos_ps.py` e `gerar_html.py` importam essa função e recalculam o modelo em memória, sem ler os CSVs de resultado. Pontos sutis:
- **Válidos:** no 1T, `votos_validos` normaliza os totais por `100-BN-NS`. No 2T, normaliza por `L/(L+F)`, o que vale tanto para `totais` quanto para `validos`.
- **Palver:** `OVERRIDE_PRIMEIRO` define os válidos da Palver no 1T. `VALIDOS_PUBLICADOS` só é usado com `--validos-publicados`.
- **Rodada usada no 1T:** a última de cada instituto que tem válidos calculáveis. Se a mais recente não tiver denominador, usa a anterior.
- **Rodada usada no 2T:** a última de cada instituto com campo terminado a partir de 05/10.
- **Recorte `--as-of`:** usa `data_divulgacao` quando existe, para não haver lookahead.
- **Pesos:** recência (meia-vida de 14 dias), amostra (`sqrt(min(n,4000)/2000)`) e método (`FATORES_METODO`). Campo iniciado antes de 05/10 leva ainda o peso `misto=0.7`.
- **Erro:** é sempre de **margem** (Flávio − Lula), com sinal urna − pesquisa (positivo = pesquisa subestimou Flávio). Na participação de um candidato, a correção é `alpha*erro/2`. O erro por instituto é encolhido para o comum: `comum + shrink*(próprio − comum)`.

### Gráficos estáticos
- **`graficos.py`:**
  - contém `tendencia(t, y, n, grade)`, uma regressão local linear com kernel gaussiano de cerca de 3 dias ponderada pela amostra, que devolve nível, dispersão e erro-padrão;
  - contém as constantes `MARCADOR`/`NOME_METODO` e `ELEICAO_1T`;
  - a tendência é estimada **separadamente** antes e depois de 04/10;
  - para usar `tendencia()` em outro script, importe o `graficos.py` **antes** de `template.py`, para que o rcParams do template prevaleça.
- **`graficos_ps.py` + `template.py`:**
  - o `template.py` é uma cópia da skill `estilo-ps` (`C:/Users/Laercio/.claude/skills/estilo-ps/`);
  - `save_chart` nomeia os arquivos como `{n}_{slug}.png`, sem zero à esquerda;
  - `salvar()` grava também os SVGs, com os textos PT/EN no dict `TEXTOS` e texto editável no SVG;
  - os gráficos finais usam a **média simples** do erro do 1T (`erro_comum_simples`). A ponderada está "na geladeira" e só aparece no modelo e nas análises preliminares.

  Os gráficos finais receberam ajustes pedidos explicitamente pelo usuário, que se sobrepõem às regras gerais da skill:
  - **Gráfico 1 (erro por instituto, ex-2):** o sinal é invertido (pesquisa − urna), o eixo X também é invertido, os valores positivos levam `+` e o rótulo é "média:".
  - **Gráfico 2 (tendência, ex-8):**
    - segue o layout do gráfico de tendência anterior, com cores e fontes P&S;
    - grade em 45/47,5/50/52,5/55 e eixo Y de 42 a 57;
    - legenda dos candidatos à esquerda da linha do 1º turno e dos métodos à direita;
    - ponto final "com correção de viés" = tendência atual + erro comum simples/2, posicionado 2,5 dias depois do último dado.
  - **Os dois:** fonte "Fonte: pesquisas registradas no TSE. Elaboração P&S.".
- **`graficos_ps_st.py`:** troca `graficos_ps.salvar` por uma versão que remove os títulos e grava `_st`/`_st_en`. Grava também PNGs de conferência no diretório temporário do sistema.

### Página interativa (`gerar_html.py` + `html_molde.html` → `agregador.html`)
- **Geração:** `gerar_html.py` monta um dict com `barras` (gráfico 1), `pontos` (todas as pesquisas do 2T), `segmentos` (grade da tendência: `t`, `nivel`, `disp`), `atual`, `corrigido`, `cenarios`, `modelo` etc. O tempo `t` é contado em dias desde 01/01/2026. O dict é serializado em JSON e substitui o placeholder `/*__DADOS__*/null` do molde.
- **Onde editar:** todo o desenho está no JS/CSS do molde, em SVG desenhado à mão, sem bibliotecas nem CDN, e funciona offline. **Edite o molde, nunca o `agregador.html`.**
- **Fidelidade aos PNGs:**
  - é uma réplica visual dos gráficos finais 1 e 2, com as mesmas cores (`#4a7fb5` Flávio, `#cd6252` Lula), eixos, textos e posições;
  - os tamanhos são convertidos de pontos do matplotlib para unidades do viewBox (`pt = 1.39` no gráfico 2 e `2.1` no gráfico 1);
  - diferença pedida pelo usuário: embaixo de "com correção de viés" aparece o ajuste por candidato entre parênteses, `(+1,7 pp)` e `(-1,7 pp)`.
- **Interações:**
  - hover nos pontos mostra os detalhes da pesquisa;
  - hover na área do gráfico mostra a tendência na data, com a faixa de 95%;
  - hover nos pontos corrigidos mostra a conta da correção;
  - clicar num ponto, ou usar o seletor, destaca as rodadas do instituto;
  - a legenda clicável esconde candidato ou método;
  - clicar numa barra do gráfico 1 ou numa linha da tabela foca o instituto no gráfico 2.
- **Outros elementos da página:**
  - indicadores no topo: tendência, com correção, erro do 1T e cenário central do modelo;
  - tabela ordenável com a rodada atual de cada instituto;
  - tabela de cenários por alfa;
  - notas de leitura.

## Armadilhas

- **Encoding no Windows:** no console cp1252, defina `PYTHONIOENCODING=utf-8` ao rodar `graficos*.py` e `gerar_html.py`. O `modelo_vies.py` já reconfigura o stdout por conta própria.
- **Unidade de rede:** `P:` é um compartilhamento de rede (`\\192.168.235.41\acpastore\...`). Os caminhos impressos pelos scripts aparecem em UNC, e é normal.
- **matplotlib antigo:** `set_xticks(pos, labels)` não aceita o segundo argumento, então use `set_xticks` seguido de `set_xticklabels`.
- **Edições por heredoc/Python no Bash:** `\n` dentro de strings Python costuma virar uma quebra de linha literal no arquivo. Prefira a ferramenta Edit ou `chr(10)`.
- **Conferir o HTML no navegador:** a extensão do Chrome não abre `file://`. Sirva a raiz com `python -m http.server 8765 --bind 127.0.0.1` (em segundo plano), abra `http://127.0.0.1:8765/agregador.html` e encerre o servidor depois.
- **Rótulos sobrepostos:** depois de mudar um gráfico, abra o PNG e confira.
- **Válidos tirados de agregador:** às vezes o Poder360 arredonda ou recalcula (ex.: Palver, Quaest). Quando houver números do próprio instituto, prefira-os e registre a origem em `observacao`.
- **Commits:** não adicione "Co-Authored-By" nem menções a Claude/Anthropic (preferência global do usuário).
