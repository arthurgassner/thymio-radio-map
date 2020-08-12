import click
import imageio
import numpy as np
from os import listdir
from os.path import join

CE_FOLDERNAME = 'ce'

@click.command()
@click.option('--src_folderpath', prompt='Folder where the ce, else and info folder are located', default='')
@click.option('--frame_duration', help='Frame duration [s]', default='0.3')
@click.option('--last_fingerprint_id', help='Last fingerprint ID to add to the gif (including)', default=-1)
def plot_fingerprints_lineplot_gif(src_folderpath, frame_duration, last_fingerprint_id):
    src_ce_folderpath = join(src_folderpath, CE_FOLDERNAME)
    lineplots_filenames = [f for f in listdir(src_ce_folderpath) if f.endswith('_lineplot.png')] # list all *_lineplot.png file in ce_folderpath

    # Order the filenames in ascending ID
    fingerprint_ids = [int(f.split('_')[-2]) for f in lineplots_filenames]
    fingerprint_ids = np.array(sorted(fingerprint_ids))

    if last_fingerprint_id > 0:
        fingerprint_ids = fingerprint_ids[fingerprint_ids <= last_fingerprint_id]
    
    lineplots_filenames = ['_'.join(['ce', str(fingerprint_id), 'lineplot.png']) for fingerprint_id in fingerprint_ids]

    print('')
    print('Combine {} *_lineplot.png files into a .GIF in {}/\n'.format(len(lineplots_filenames), src_ce_folderpath))
    with imageio.get_writer(join(src_ce_folderpath, 'lineplots.gif'), mode='I', duration=frame_duration) as writer:
        for f in lineplots_filenames:
            image = imageio.imread(join(src_ce_folderpath, f))
            writer.append_data(image)
    
    print('lineplots.gif created')


if __name__ == '__main__':
    plot_fingerprints_lineplot_gif() # pylint: disable=no-value-for-parameter