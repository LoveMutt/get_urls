import argparse
import csv
import logging
import random
import urllib.request as request
from io import StringIO
from pprint import pprint
import os

from lxml import html

log = logging.getLogger(__name__)


def get_csvs(fp_csv_list: str = 'csv_url.cache', download=False, persist: bool = False, cleanup: bool=False):
    csv_url = 'https://github.com/citizenlab/test-lists/tree/master/lists'
    csvs = []
    if not download:
        log.info('Opening {} for csv files'.format(fp_csv_list))
        try:
            with open(fp_csv_list) as f:
                csvs = f.readlines()
        except (OSError, FileNotFoundError):
            download = True
    if download:
        log.info('downloading csv cache from {} to [{}]'.format(csv_url, fp_csv_list))
        web_obj = request.urlopen(csv_url)
        root = html.fromstring(web_obj.read())
        csv_links = [link for link in root.xpath('//a/@href') if link.endswith('.csv') and '00-' not in link]
        log.debug('Identified {} target csv links'.format(len(csv_links)))
        for link in csv_links:
            full_url = request.urljoin(csv_url, link)
            full_url = get_raw_github_file_url(full_url)
            csvs.append(full_url)
        if persist and fp_csv_list:
            list_to_file(csvs, fp_csv_list)
    if cleanup:
        delete_file(fp_csv_list)
    return csvs


def get_urls(fp_url_list: str = '', download=False, persist: bool = False, shuffle: bool = False, cleanup: bool=False):
    list_of_urls = []
    if not download:
        log.info('Opening {} for list of URLs'.format(fp_url_list))
        try:
            with open(fp_url_list) as f:
                list_of_urls = f.readlines()
        except (OSError, FileNotFoundError):
            download = True
    if download:
        csvs = get_csvs(persist=persist)
        if not csvs:
            raise RuntimeError('No sources found to download URLs from')
        for file_url in csvs:
            log.info('Reading URLs from {}...'.format(file_url))
            csv_obj = request.urlopen(file_url)
            list_of_urls.extend(parse_cl_csv_for_urls(csv_obj.read().decode()))
        if persist and fp_url_list:
            list_to_file(list_of_urls, fp_url_list)
    if cleanup:
        delete_file(fp_url_list)
    if shuffle:
        random.shuffle(list_of_urls)
    return list_of_urls


def parse_cl_csv_for_urls(s):
    content_io = StringIO(s)
    reader = csv.DictReader(content_io)
    urls = []
    for row in reader:
        urls.append(row['url'])
    return urls


def get_raw_github_file_url(s: str):
    """convert an embedded github file to the raw file"""
    new_s = s.replace('github.com', 'raw.githubusercontent.com').replace('/blob', '')
    log.debug('Converting url [{}] to [{}] for raw file'.format(s, new_s))
    return new_s


def list_to_file(lst: list, out_file: str):
    log.info('Writing list to [{}]'.format(out_file))
    with open(out_file, 'w') as f:
        f.write('\n'.join(lst))


def delete_file(fp: str):
    if not os.path.isfile(fp):
        log.error('Could not find file [{}] to delete'.format(fp))
        return
    os.remove(fp)


def _main(args):
    pprint(get_urls(fp_url_list=args.input_file, download=args.download, persist=args.persist, cleanup=args.cleanup))


def getargs():
    p = argparse.ArgumentParser()
    p.add_argument('-i', '--input-file', default='',
                   help='File of URLs to read and return. (will download if doesn\'t exist')
    p.add_argument('-d', '--download', action='store_true', default=False, help='Download lists from citizenlab')
    p.add_argument('-r', '--random-shuffle', action='store_true', default=False, help='Shuffle results before output')
    persist_grp = p.add_mutually_exclusive_group()
    persist_grp.add_argument('-p', '--persist', action='store_true', default=False,
                   help='Write the results of downloads to files')
    persist_grp.add_argument('-c', '--cleanup', action='store_true', default=False, help='Delete cache files after running')
    return p.parse_args()


if __name__ == '__main__':
    _main(getargs())
