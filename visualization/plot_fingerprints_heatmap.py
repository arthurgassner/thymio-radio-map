import click 
import seaborn as sns 
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt

from os.path import join
from os import listdir

CE_FOLDERNAME = 'ce'
CE_FILENAME = 'ce'

N_TTI_TO_PLOT = 5 # # of TTIs to plot
N_SUBCARRIERS = 400 

@click.command()
@click.option('--src_folderpath', prompt='Folder where the ce, else and info folder are located', default='')
@click.option('--n_fingerprints', prompt='How many fingerprints to plot', default=10)
def plot_fingerprints_heatmap(src_folderpath, n_fingerprints):
    """Plot a {N_TTI_TO_PLOT} samples of the channel estimates' amplitude located in src_folderpath/CE_FOLDERNAME as a heatmap
    The plot is saved in src_folderpath 

    Arguments:
        src_folderpath {str} -- Source folder where the CE_FOLDERNAME, ELSE_FOLDERNAME and INFO_FOLDERNAME folder are located
        n_fingerprints {int} -- How many fingerprints to plot
    """

    src_ce_folderpath = join(src_folderpath, CE_FOLDERNAME)

    cleaned_ce_files = [f.split('.')[0] for f in listdir(src_ce_folderpath) if f.split('.')[-1] == 'parquet'] # list all .parquet file in ce_folderpath
 
    # put the fingerprints in ascending order of IDs (i.e. ['ce_0', 'ce_1', ...])
    fingerprint_ids = list(map(lambda x: int(x.split('_')[1]), cleaned_ce_files))
    argsort = np.argsort(fingerprint_ids)
    fingerprint_ids = np.sort(fingerprint_ids)
    cleaned_ce_files = list(np.array(cleaned_ce_files)[argsort])   

    cleaned_ce_files = cleaned_ce_files[:n_fingerprints] # only keep n_fingerprints
    fingerprint_ids = fingerprint_ids[:n_fingerprints]
    
    # Average each fingerprint over its recording time
    ce_space = np.full((N_SUBCARRIERS, 4, len(cleaned_ce_files)), np.nan) # will hold the ce as it changes through space
    for i, f in enumerate(cleaned_ce_files):
        ce_df = pd.read_parquet(join(src_ce_folderpath, '{}.parquet'.format(f)))
        ce_mean_amplitude = ce_df.groupby('SC_ID').mean()[['CE_0_AMPLITUDE', 'CE_1_AMPLITUDE', 'CE_2_AMPLITUDE', 'CE_3_AMPLITUDE']].to_numpy() # shape [400, 4]
        ce_space[:,:,i] = 20 * np.log10(ce_mean_amplitude)
    
    # Plot one heatmap per port
    _, axes = plt.subplots(4, 1, figsize=(25, 10), sharex=True)
    for port, ax in enumerate(axes):
        sns.heatmap(ce_space[:,port,:], cbar_kws={'label': 'CSI amplitude [dB]'}, ax=ax, center=0)
        ax.set_ylabel(f'Port #{port+1}', fontsize=14)
        step = 1
        if len(fingerprint_ids) > 20:
            step = int(len(fingerprint_ids)/10)
        plt.xticks(np.arange(len(fingerprint_ids), step=step), fingerprint_ids[::step])
        
    plt.suptitle('Heatmap of the average CSI amplitude for consecutive fingerprint IDs', fontsize=18)
    axes[3].set_xlabel('Fingerprint ID', fontsize=14)

    plot_filename = 'heatmap.png'
    plt.savefig(join(src_ce_folderpath, plot_filename))
    plt.close()
    print('Plotted {}'.format(plot_filename))

if __name__ == '__main__':
    plot_fingerprints_heatmap() # pylint: disable=no-value-for-parameter