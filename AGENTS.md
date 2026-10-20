# AGENTS.md

Orientações para agentes de código (Claude Code, Codex, Gemini CLI etc.) que trabalham neste projeto.

## O que é

Agregador das pesquisas da eleição presidencial de 2026 (Lula x Flávio Bolsonaro). O projeto calibra o erro das pesquisas no 1º turno (04/10/2026) contra o resultado do TSE e aplica parte desse erro ao agregado do 2º turno (25/10/2026). O resultado são **cenários condicionais**, não probabilidades de vitória. A documentação técnica completa (fórmulas, fontes e limitações) está em `codigos/LEIA-ME.md`, e o resumo dos resultados para leitura está em `resultado.md`.

Python 3.9 (Anaconda); não há testes nem lint. O usuário escreve em português, e textos, nomes e gráficos seguem em português.

## Versionamento (git)

O projeto é versionado com git nesta pasta (`P:\Atualização\Modelos\Política\Pesquisas Eleitorais`), sem remote. A branch principal é `main`. Para experimentos, crie uma branch e faça o merge na `main` quando o resultado for aprovado.

## Comandos (rodar de dentro de `codigos/`)

```bash
python construir_base.py    # regrava dados/brutos/pesquisas_2026.csv a partir da transcrição no próprio script
python modelo_vies.py       # recalcula dados/resultados/ (padrão: --as-of 2026-10-16 --alpha 0.5 --shrink 0.25)
python graficos.py          # PNGs 01,03-07 em graficos/analises preliminares/ + dados/resultados/sensibilidade.csv
python graficos_ps.py       # gráficos finais 1 e 2: PNG na raiz de graficos/, SVG PT e _en em graficos/svg/
```

Opções do modelo: `--alpha` (fração do erro do 1T transferida, de 0 a 1), `--shrink` (peso do erro próprio de cada instituto em relação ao comum), `--metodo-neutro`, `--validos-publicados` (usa no 1T os válidos divulgados por Datafolha e Quaest) e `--as-of AAAA-MM-DD`.

## Arquitetura

- **Fonte da verdade dos dados:** são as strings `DATA_1T`/`DATA_2T` (formato `Instituto|inicio|fim|n|Lula|Flavio|registro|base|BN|NS|metodo`) e os dicts de ajuste em `construir_base.py`, e não o CSV. Para incluir ou corrigir uma pesquisa, edite ali (observações, fontes e `DIVULGACAO_2T`) e rode os quatro scripts em ordem. Editar só o CSV é perdido quando o `construir_base.py` roda de novo.
- **`modelo_vies.py`** usa só a biblioteca padrão. `calcular()` devolve `(resumo, primeiro_out, instituto_out, seg_out, cenarios)` e é importado por `graficos.py` e `graficos_ps.py`, que recalculam o modelo em memória em vez de ler os CSVs de resultado. Pontos sutis:
  - No 1T, `votos_validos` normaliza os totais por `100-BN-NS`. No 2T, normaliza por `L/(L+F)`.
  - `OVERRIDE_PRIMEIRO` define os válidos da Palver.
  - Usa a última rodada de cada instituto que tem válidos calculáveis.
  - O recorte `--as-of` usa `data_divulgacao` quando existe, para não haver lookahead.
  - A AtlasIntel com campo iniciado antes de 05/10 leva o peso `misto=0.7`.
  - O erro é sempre de **margem** (Flávio − Lula). Na participação de um candidato, a correção é `alpha*erro/2`.
- **`graficos.py`** contém `tendencia()`, uma regressão local linear com kernel gaussiano de cerca de 3 dias ponderada pela amostra, e as constantes `MARCADOR`/`NOME_METODO`. Ambas são reutilizadas por `graficos_ps.py`. Para usar `tendencia()` em outro script, importe-o **antes** de `template.py`, para que o rcParams do template prevaleça.
- **`graficos_ps.py` + `template.py`:** o `template.py` é uma cópia da skill `estilo-ps` (`C:/Users/Laercio/.claude/skills/estilo-ps/`). `save_chart` nomeia os arquivos como `{n}_{slug}.png`, sem zero à esquerda; `salvar()` grava também os SVGs em `graficos/svg/` (`{n}_{slug}.svg` em PT e `{n}_{slug}_en.svg` em EN; textos em `TEXTOS`, texto editável). Os gráficos finais 1 (erro por instituto, ex-2) e 2 (tendência, ex-8) usam a **média simples** do erro do 1T (`erro_comum_simples`); a ponderada está "na geladeira" e só aparece no modelo e nas análises preliminares. `graficos/analises preliminares/` guarda os 8 gráficos antigos (o 2 e o 8 de lá são retratos estáticos com a média ponderada, que nenhum script regrava). Os gráficos finais receberam ajustes pedidos explicitamente pelo usuário, que se sobrepõem às regras gerais da skill:
  - **Gráfico 1 (ex-2):** o sinal é invertido (pesquisa − urna), o eixo X também é invertido, os valores positivos levam `+` e o rótulo é "média:".
  - **Gráfico 2 (ex-8):** segue o layout do gráfico de tendência anterior, com cores e fontes P&S, grade em 45/47,5/50/52,5/55, eixo Y de 42 a 57, legenda dos candidatos à esquerda da linha do 1º turno e dos métodos à direita, e ponto final "com correção de viés" = atual + erro comum/2.
  - **Os dois:** fonte "Fonte: pesquisas registradas no TSE. Elaboração P&S.".
- **Excel** (`dados/agregador_eleitoral_2026_auditavel.xlsx`): é um retrato estático **anterior** à revisão de 16/10, e nenhum script o gera.
- **ZIP na raiz:** é o pacote original, e deve ficar intocado.

## Armadilhas

- No console do Windows (cp1252), defina `PYTHONIOENCODING=utf-8` ao rodar `graficos*.py`. O `modelo_vies.py` já reconfigura o stdout por conta própria.
- O matplotlib é antigo: `set_xticks(pos, labels)` não aceita o segundo argumento, então use `set_xticks` seguido de `set_xticklabels`.
- Em edições por heredoc/Python no Bash, `\n` dentro de strings Python costuma virar uma quebra de linha literal no arquivo. Prefira a ferramenta Edit ou `chr(10)`.
- Depois de mudar um gráfico, abra o PNG e confira se há sobreposição de rótulos.
