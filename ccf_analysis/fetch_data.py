import requests
import subprocess


def download_file(url, outfilename):
    """
    Download file from url, and save to outfilename
    :param url:
    :param outfilename:
    :return:
    """
    r = requests.get(url, stream=True)
    with open(outfilename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
    return

DATA_URL = 'http://www.as.utexas.edu/~kgulliks/media/data/ccf_data.tar.gz'
outfile = 'ccf_data.tar'
print('Downloading data from server')
download_file(DATA_URL, outfile)
print('Un-packing data')
subprocess.check_call(['tar', '-xvf', outfile])
print('Done!')
