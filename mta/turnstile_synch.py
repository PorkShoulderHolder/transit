__author__ = 'sam.royston'
from bs4 import BeautifulSoup
import urllib
import os
from subprocess import call
from utils import default_data_dir

class UpdateManager(object):
    def __init__(self, start_yr=14, url="http://web.mta.info/developers/turnstile.html", data_dir=None, verbose=False):
        self.verbose = verbose
        self.list_url = url
        self.start_yr = start_yr
        self.links = UpdateManager.__read_page(url)
        if data_dir is None:
            data_dir = default_data_dir()
        else:
            print "using custom data directory: " + data_dir
        if not os.path.isdir(data_dir):
            os.makedirs(data_dir)
        self.data_dir = data_dir

    @staticmethod
    def __read_page(url):
        page = urllib.urlopen(url)
        soup = BeautifulSoup(page.read())
        section = soup.find('div', class_="span-84 last")
        links = section.find_all('a')
        return links

    @staticmethod
    def get_most_recent(data_dir):
        print data_dir
        files = filter(lambda x: "turnstile_" in x, os.listdir(data_dir))
        files_dates = zip(files, [f.split("_")[-1][:6] for f in files])
        files_dates = sorted(files_dates, key=lambda x: x[1], reverse=True)
        return data_dir + "/" + files_dates[0][0]

    @staticmethod
    def get_year(href_str):
        return int(href_str.split("_")[1][:2])

    @staticmethod
    def get_filename(href_str):
        return href_str.split("/")[-1]

    def clean_empties(self):
        for f in os.listdir(self.data_dir):
            fp = self.data_dir + f
            if ".gz" != fp[-3:]:
                os.system("rm " + fp)

    def synch_turnstiles(self):
        ls = filter(lambda x: self.get_year(x['href']) > self.start_yr, self.links)
        fns = map(lambda x: UpdateManager.get_filename(x['href']), ls)
        links_for_fns = {}
        for link in ls:
            links_for_fns[UpdateManager.get_filename(link['href'])] = link['href']
        files = os.listdir(self.data_dir)
        diff = set(fns) - set([f.replace(".gz", "") for f in files])
        for d in diff:
            dl_call = "wget -O {0}/{1} http://web.mta.info/developers/{2}".format(self.data_dir, d, links_for_fns[d])
            compress_call = "gzip {0}/".format(self.data_dir) + d
            call(dl_call.split(" "))
            call(compress_call.split(" "))

    def synch_locations(self):
        dl_call = "wget -O {0}/StationEntrances.csv " \
                  "http://web.mta.info/developers/data/nyct/subway/StationEntrances.csv".format(self.data_dir)
        call(dl_call.split(" "))

    def synch_gtfs(self):
        dl_call = "wget -O {0}/google_transit.zip " \
                  "http://web.mta.info/developers/data/nyct/subway/google_transit.zip".format(self.data_dir)
        unzip_call = "unzip -o {0}/google_transit.zip -d {0}/google_transit".format(self.data_dir)
        call(dl_call.split(" "))
        call(unzip_call.split(" "))