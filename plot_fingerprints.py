import click 
import seaborn as sns 
import pandas as pd 
import matplotlib.pyplot as plt

from os.path import join
from os import listdir

CE_FOLDERNAME = 'ce'
CE_FILENAME = 'ce'

N_TTI_TO_PLOT = 5 # # of TTIs to plot

@click.command()
@click.option('--src_folderpath', prompt='Folder where the ce, else and info folder are located', default='')
@click.option('--force', '-f', is_flag=True, help='Whether to replot already plotted files')
def plot_fingerprints(src_folderpath, force):
    """Plot a sample of the channel estimates located in src_folderpath/CE_FOLDERNAME
    The plot is saved in src_folderpath 

    If --force is set, then the already plotted .parquet are replotted

    Arguments:
        src_folderpath {str} -- Source folder where the CE_FOLDERNAME, ELSE_FOLDERNAME and INFO_FOLDERNAME folder are located
    """

    src_ce_folderpath = join(src_folderpath, CE_FOLDERNAME)

    cleaned_ce_files = [f.split('.')[0] for f in listdir(src_ce_folderpath) if f.split('.')[-1] == 'parquet'] # list all .parquet file in ce_folderpath
    
    if not force:
        ce_pngs = [f.split('.')[0] for f in listdir(src_ce_folderpath) if f.split('.')[-1] == 'png'] # list all .png file in ce_folderpath
        cleaned_ce_files = sorted(list(set(cleaned_ce_files) - set(ce_pngs)))

    print('')
    print('Plot {} .parquet files in {}/\n'.format(len(cleaned_ce_files), src_ce_folderpath))
    for f in cleaned_ce_files:
        print('\t {}.parquet: '.format(f), end='')
        ce_df = pd.read_parquet(join(src_ce_folderpath, '{}.parquet'.format(f)))
        ttis = sorted(ce_df.TTI.unique())[:N_TTI_TO_PLOT] # list of TTIs to plot
        
        # Plot
        _, axes = plt.subplots(4, 1, figsize=(5, 15), sharex=True)

        for ax, y in zip(axes, ['CE_0_AMPLITUDE', 'CE_1_AMPLITUDE', 'CE_2_AMPLITUDE', 'CE_3_AMPLITUDE']):
            sns.lineplot(x='SC_ID', y=y, hue='TTI', data=ce_df[ce_df.TTI.apply(lambda tti: tti in ttis)], legend=False, ax=ax)

        plt.suptitle('{}\n {} TTIs'.format(f, len(ttis)))

        plot_filename = '{}.png'.format(f.split('.')[0])
        plt.savefig(join(src_ce_folderpath, plot_filename))
        print('Plotted')

if __name__ == '__main__':
    plot_fingerprints() # pylint: disable=no-value-for-parameter