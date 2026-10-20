"""Exporta os gráficos finais 1 e 2 sem título, em SVG PT e EN."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import graficos_ps as graficos


def salvar_sem_titulo(fig, n, slug, lang):
    titulos = {t[chave] for t in graficos.TEXTOS.values()
               for chave in ('titulo_erro', 'titulo_tend')}
    for ax in fig.axes:
        for texto in list(ax.texts):
            if texto.get_text() in titulos:
                texto.remove()
    sufixo = '_st' if lang == 'pt' else '_st_en'
    pasta = graficos.SAIDA / 'svg'
    pasta.mkdir(parents=True, exist_ok=True)
    destino = pasta / '{}_{}{}.svg'.format(n, slug, sufixo)
    fig.savefig(destino, facecolor='white', bbox_inches='tight', pad_inches=0.025)
    from pathlib import Path
    import tempfile
    fig.savefig(Path(tempfile.gettempdir()) / destino.with_suffix('.png').name,
                dpi=150, facecolor='white', bbox_inches='tight', pad_inches=0.025)
    plt.close(fig)
    return destino


if __name__ == '__main__':
    graficos.salvar = salvar_sem_titulo
    graficos.main()
