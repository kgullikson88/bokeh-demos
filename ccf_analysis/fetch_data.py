import requests
import subprocess

DATA_URL = 'http://www.as.utexas.edu/~kgulliks/media/data/ccf_data.tar.gz'

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

outfile = 'ccf_data.tar'
download_file(DATA_URL, outfile)
subprocess.check_call(['tar', '-xvf', outfile])
