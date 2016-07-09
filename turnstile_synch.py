__author__ = 'sam.royston'
from bs4 import BeautifulSoup
import urllib
import os
from subprocess import call


class UpdateManager(object):
    def __init__(self, start_yr=14, url="http://web.mta.info/developers/turnstile.html"):
        self.list_url = url
        self.start_yr = start_yr
        self.links = UpdateManager.__read_page(url)


    @staticmethod
    def __read_page(url):
        page = urllib.urlopen(url)
        soup = BeautifulSoup(page.read())
        section = soup.find('div', class_="span-84 last")
        links = section.find_all('a')
        return links

    @staticmethod
    def get_year(href_str):
        return int(href_str.split("_")[1][:2])

    @staticmethod
    def get_filename(href_str):
        return href_str.split("/")[-1]

    @staticmethod
    def clean_empties():
        for f in os.listdir("turnstile_data"):
            fp = "turnstile_data/" + f
            if ".gz" != fp[-3:]:
                os.system("rm " + fp)

    def synch_dir(self, ls):
        ls = filter(lambda x: self.get_year(x['href']) > self.start_yr, ls)
        fns = map(lambda x: UpdateManager.get_filename(x['href']), ls)
        links_for_fns = {}
        for link in ls:
            links_for_fns[UpdateManager.get_filename(link['href'])] = link['href']
        files = os.listdir("turnstile_data")
        diff = set(fns) - set([f.replace(".gz", "") for f in files])
        for d in diff:
            dl_call = "wget -O turnstile_data/{0} http://web.mta.info/developers/{1}".format(d, links_for_fns[d])
            compress_call = "gzip turnstile_data/" + d
            call(dl_call.split(" "))
            call(compress_call.split(" "))

