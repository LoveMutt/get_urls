def get_urls(from_file=False):
    csv_cache_file = r'F:\TIG\Projects\tie\baryon\baryoncore2\tests\csv_urls.txt'
    urls_cache_file = r'F:\TIG\Projects\tie\baryon\baryoncore2\tests\list_of_urls.txt'
    if from_file and os.path.exists(csv_cache_file):
        log.info('Opening {} for csv files'.format(csv_cache_file))
        with open(csv_cache_file) as f:
            csvs = f.readlines()
    else:
        csv_url = 'https://github.com/citizenlab/test-lists/tree/master/lists'
        raw_url = csv_url.replace('github.com', 'raw.githubusercontent.com')
        log.info('reading csv files from {}'.format(csv_url))
        web_obj = request.urlopen(csv_url)
        root = html.fromstring(web_obj.read())
        csvs = []
        for link in root.xpath('//a/@href'):
            if link.endswith('.csv') and '00-' not in link:
                link = link.replace('/blob', '')
                full_url = request.urljoin(raw_url, link)
                csvs.append(full_url)
        with open(csv_cache_file, 'w') as f:
            f.write('\n'.join(csvs))
    if from_file and os.path.exists(urls_cache_file):
        with open(urls_cache_file) as f:
            list_of_urls = f.readlines()
    else:
        list_of_urls = []
        for file_url in csvs:
            log.info('Reading URLs from {}...'.format(file_url))
            csv_obj = request.urlopen(file_url)
            list_of_urls.extend(parse_cl_csv_for_urls(csv_obj.read().decode()))
        with open(urls_cache_file, 'w') as f:
            f.write('\n'.join(list_of_urls))
    return list_of_urls


def parse_cl_csv_for_urls(s):
    content_io = StringIO(s)
    reader = csv.DictReader(content_io)
    urls = []
    for row in reader:
        urls.append(row['url'])
    return urls
