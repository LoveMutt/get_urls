import urllib.request as request
import logging
import csv
from io import StringIO

from lxml import html

log = logging.getLogger(__name__)


def get_urls(fp_url_list: str=None, persist: bool=False):
    csv_cache_file = r'csv_url.cache'
    csv_url = 'https://github.com/citizenlab/test-lists/tree/master/lists'
    csvs = []
    list_of_urls = []
    download_csvs = True
    download_urls = True
    if fp_url_list:
        download_csvs = False
        download_urls = False
    if not download_csvs:
        log.info('Opening {} for csv files'.format(csv_cache_file))
        try:
            with open(csv_cache_file) as f:
                csvs = f.readlines()
        except (OSError, FileNotFoundError):
            download_csvs = True
    if download_csvs:
        log.info('downloading csv cache from {} to [{}]'.format(csv_url, csv_cache_file))
        web_obj = request.urlopen(csv_url)
        root = html.fromstring(web_obj.read())
        for link in root.xpath('//a/@href'):
            if link.endswith('.csv') and '00-' not in link:
                full_url = request.urljoin(csv_url, link)
                full_url = get_raw_github_file_url(full_url)
                csvs.append(full_url)
        if persist and csv_cache_file:
            list_to_file(csvs, csv_cache_file)
    if not download_urls:
        log.info('Opening {} for list of URLs'.format(fp_url_list))
        try:
            with open(fp_url_list) as f:
                list_of_urls = f.readlines()
        except (OSError, FileNotFoundError):
            download_urls = True
    if download_urls:
        if not csvs:
            raise RuntimeError('No sources found to download URLs from')
        for file_url in csvs:
            log.info('Reading URLs from {}...'.format(file_url))
            csv_obj = request.urlopen(file_url)
            list_of_urls.extend(parse_cl_csv_for_urls(csv_obj.read().decode()))
        if persist and fp_url_list:
            list_to_file(list_of_urls, fp_url_list)
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
