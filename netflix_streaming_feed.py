#!/usr/bin/env python3
import sys
import requests
from argparse import ArgumentParser
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
import cfgreader
import csv
import urllib
import logging
import time


class Show:
    def __init__(self, title, url, guid, date):
        self.title = title
        self.url = url
        self.guid = guid
        self.date = time.strptime(date, "%m/%d/%y")

    def __lt__(self, other):
        return self.date < other.date

    def __str__(self):
        return f"title:{self.title}, date:{time.strftime('%Y-%m-%d', self.date)}"

    def rss(self):
        date = time.strftime("%a, %d %b %Y %H:%M:%S -0700", self.date)
        return (f"<item>"
                f"<title>{escape(self.title)}</title>"
                f"<pubDate>{date}</pubDate>"
                f"<link>{self.url}</link>"
                f"<guid isPermaLink=\"false\">{self.guid}</guid>"
                f"<description><![CDATA[{self.title} on {date}]]></description>"
                f"</item>\n")


def get_auth_url():
    """"TODO: Get the auth URL param from Netflix's /viewingactivity viewingActivityClient.js"""
    return "NOTREALLYANAUTHURL"


def download(cfg):
    """Downloads a custom CSV file from Netflix"""
    post_data = {
        "userLoginId": cfg.main.email,
        "password": cfg.main.password,
        "rememberMe": "true",
        "flow": "websiteSignUp",
        "mode": "login",
        "action": "loginAction",
        "withFields": "rememberMe,nextPage,userLoginId,password,countryCode,countryIsoCode",
        "countryCode": "+1",
        "countryIsoCode": "US"}

    url_base = "https://www.netflix.com/"
    with requests.Session() as session:
        # Login
        r = session.post(url_base + "login", data=post_data)
        if not r.ok:
            raise Exception("Could not login. " + r.reason)

        # Select a User Profile
        get_params = { 'tkn': cfg.main.profile_token }
        r = session.get(url_base + 'SwitchProfile', params=get_params)
        if not r.ok:
            raise Exception("Could not set profile. " + r.reason)

        # Get your viewing activity history
        get_params = {
            'guid': cfg.main.user_guid,
            '_': int(time.time() * 1000),
            'authURL': get_auth_url()}
        csv_response = session.get(url_base + 'api/shakti/va61a784d/viewingactivitycsv',
                                   params=get_params)
        if not csv_response.ok:
            raise Exception("Could not get csv. " + csv_response.reason)
    return csv_response.text


def write_feed(shows, cfg):
    update_status = "OK"
    now = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
    with open(cfg.feed.filename, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n'
                '<rss xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">\n')
        f.write(f'<channel>\n'
                f'<atom:link href="{cfg.feed.href}" rel="self" type="application/rss+xml" />'
                f'<title>{cfg.feed.title}</title>'
                f'<link>https://www.netflix.com/</link><pubDate>{now}</pubDate>'
                f'<description>{cfg.feed.title}</description><language>en-us</language>\n')
        for e in shows:
            f.write(e.rss())
        f.write("</channel></rss>\n")
    return update_status


def main(do_download):
    """The main function, does the whole thing."""
    start_time = time.time()
    cfg = cfgreader.CfgReader(__file__.replace('.py', '.cfg'))
    cache = __file__.replace('.py', '.csv')
    if do_download:
        csv_data = download(cfg)
        logging.debug("Downloaded latest streaming activity.")
        with open(cache, "w", encoding="utf-8") as f:
            f.write(csv_data)
    else:
        logging.debug("Using cached streaming activity.")

    shows = list()
    with open(cache, newline='') as f:
        reader = csv.reader(f)
        t, d = next(reader)
        assert(t == 'Title' and d == 'Date')
        guid = 1000
        for title, show_date in reader:
            url = 'https://www.netflix.com/search?q=' + urllib.parse.quote(title)
            shows.append(Show(title, url, title + str(guid), show_date))
            guid += 1
    shows.sort(reverse=True)
    update_status = write_feed(shows[:20], cfg)
    logging.info(f"{time.time() - start_time:2.0f}s {update_status}")


if __name__ == '__main__':
    parser = ArgumentParser(description="Make a streaming activity feed.")
    parser.add_argument('-n', '--nodownload', action='store_true')
    parser.add_argument('-o', '--outfile')
    args = parser.parse_args()
    if args.outfile is None:
        handler = logging.StreamHandler(sys.stdout)
    else:
        handler = logging.FileHandler(args.outfile)
    logging.basicConfig(handlers=(handler,),
                        format='%(asctime)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M',
                        level=logging.INFO)
    main(not args.nodownload)
