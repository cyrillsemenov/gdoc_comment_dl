from __future__ import unicode_literals
import youtube_dl
import time
import sys


FMT = "bestvideo[ext=mp4][vcodec!*=av01]+bestaudio[ext=m4a]"
alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "n", "m", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]


def clearln():
    print('\r\x1b[K', end='')


class MyLogger(object):
    def debug(self, msg):
        # print(msg)
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


class SingleDownload(youtube_dl.YoutubeDL):

    def __init__(self, url, name):
        self.i = 0
        self.filename = ""
        self.params = {
            "format": FMT,
            "outtmpl": name,
            "logger": MyLogger(),
            # "progress_hooks": [self.status],
        }
        super().__init__(self.params)
        self.add_progress_hook(self.status)
        self.afterpass = []
        self.download(url)

    def download(self, url):
        url_list = [url]
        self.filename = url
        super().download(url_list)

    def process_info(self, info_dict):
        super().process_info(info_dict)
        self.status({"status": "DONE"})

    def status(self, d):
        # print(d)

        if d["status"] == "downloading":
            timer = int(str(round(time.time()))[-1])
            if timer % 5 == 0:
                pts = " "
            else:
                pts = "."*(timer % 5)

            # sys.stdout.write('\033[2K\033[1G')
            clearln()
            print(f"Downloading{pts}\t\t{self.filename}\t{''.join(self.afterpass)}{d['_percent_str']}", end="\r")
            #  {d['_total_bytes_estimate_str']}
        elif d["status"] == "finished":
            # self.afterpass.append("100.0%\t")
            clearln()
        elif d["status"] == "DONE":
            # sys.stdout.write('\033[2K\033[1G')
            clearln()
            print(f"Done\t\t\t{self.filename}\t{''.join(self.afterpass)}")
        else:
            # pass
            print(d)
        self.i += 1


class Downloader:
    def __init__(self, dataframe, links, numbers, timecodes, text, path="~/"):
        self.df = dataframe
        self.links = links
        self.numbers = numbers
        self.timecodes = timecodes
        self.text = text
        self.path = path
        for index, row in dataframe[dataframe[links].map(type) == list].iterrows():
            self.download_row(row)

    def download_row(self, row):
        for i in range(len(row[self.links])):
            suffix = alphabet[i] if len(row[self.links]) > 1 else ""
            try:
                tc = row[self.timecodes][i]+" "
            except IndexError:
                tc = ""
            url = row[self.links][i]
            name = f"{row[self.numbers]}{suffix} {tc}{row[self.text]}"
            try:
                SingleDownload(url, self.path+name)
            except:
                pass
