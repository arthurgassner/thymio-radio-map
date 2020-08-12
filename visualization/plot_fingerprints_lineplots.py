import click 
import seaborn as sns 
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt

from os.path import join
from os import listdir

CE_FOLDERNAME = 'ce'
CE_FILENAME = 'ce'

N_TTI_TO_PLOT = 50 # # of TTIs to plot

@click.command()
@click.option('--src_folderpath', prompt='Folder where the ce, else and info folder are located', default='')
@click.option('--force', '-f', is_flag=True, help='Whether to replot already plotted files')
def plot_fingerprints_lineplots(src_folderpath, force):
    """Plot a sample of the channel estimates located in src_folderpath/CE_FOLDERNAME
    The plot is saved in src_folderpath 

    If --force is set, then the already plotted .parquet are replotted

    Arguments:
        src_folderpath {str} -- Source folder where the CE_FOLDERNAME, ELSE_FOLDERNAME and INFO_FOLDERNAME folder are located
    """

    src_ce_folderpath = join(src_folderpath, CE_FOLDERNAME)

    cleaned_ce_files = [f.split('.')[0] for f in listdir(src_ce_folderpath) if f.split('.')[-1] == 'parquet'] # list all .parquet file in ce_folderpath
    
    print('')
    print('Plot {} .parquet files in {}/\n'.format(len(cleaned_ce_files), src_ce_folderpath))
   
    if not force:
        ce_pngs = [f.split('.')[0][:-9] for f in listdir(src_ce_folderpath) if f.endswith('_lineplot.png')] # list all *_lineplot.png file in ce_folderpath
        print('{}/{} fingerprints already plotted\n'.format(len(ce_pngs), len(cleaned_ce_files)))
        cleaned_ce_files = sorted(list(set(cleaned_ce_files) - set(ce_pngs)))

    # put the fingerprints in ascending order of IDs (i.e. ['ce_0', 'ce_1', ...])
    fingerprint_ids = list(map(lambda x: int(x.split('_')[1]), cleaned_ce_files))
    argsort = np.argsort(fingerprint_ids)
    fingerprint_ids = np.sort(fingerprint_ids)
    cleaned_ce_files = list(np.array(cleaned_ce_files)[argsort])   

    for f in cleaned_ce_files:
        print('\t {}.parquet: '.format(f), end='')
        ce_df = pd.read_parquet(join(src_ce_folderpath, '{}.parquet'.format(f)))

        ce_df[['CE_0_AMPLITUDE', 'CE_1_AMPLITUDE', 'CE_2_AMPLITUDE', 'CE_3_AMPLITUDE']] = 20 * np.log10(ce_df[['CE_0_AMPLITUDE', 'CE_1_AMPLITUDE', 'CE_2_AMPLITUDE', 'CE_3_AMPLITUDE']])
        
        # Plot
        _, axes = plt.subplots(4, 1, figsize=(5, 15), sharex=True)

        if not ce_df.empty: # the fingerprint might be empty if the gathering timed out
            mean_df = ce_df.groupby('SC_ID').mean().reset_index()
            std_df = ce_df.groupby('SC_ID').std().reset_index()
            
            for ax, col in zip(axes, ['CE_0_AMPLITUDE', 'CE_1_AMPLITUDE', 'CE_2_AMPLITUDE', 'CE_3_AMPLITUDE']):
                sns.lineplot(x='SC_ID', y=col, data=mean_df, legend=False, ax=ax)
                ax.fill_between(x=std_df['SC_ID'], y1=mean_df[col] - std_df[col], y2=mean_df[col] + std_df[col], alpha=0.2)
                
        plt.suptitle('{}\n {} TTIs \n ||CSI|| [dB]'.format(f, ce_df.TTI.nunique()))

        plot_filename = '{}_lineplot.png'.format(f.split('.')[0])
        plt.savefig(join(src_ce_folderpath, plot_filename))
        plt.close()
        print('Plotted')

if __name__ == '__main__':
    plot_fingerprints_lineplots() # pylint: disable=no-value-for-parameter