import pandas as pd
import numpy as np
from regex import YT_LINK, TC, URL


def guess_lost_indexes(df, field="index_in_file"):
    """My idea is that if comment was not found
    (highly likely if content in document was slightly changed after commenting)
    we can guess that author added comments in some ordered way
    so we can take mean of this comments neighbours by placing time "index_in_file"
    and god bless here is it. Right?"""
    not_found = df[df[field] < 0].index.to_list()
    for i in not_found:
        if i == 0:
            df.loc[i, field] = 0
        elif i == len(df[field]) - 1:
            df.loc[i, field] = df[field].max() + 1
        else:
            neighbours = df.loc[i + 1, field] + df.loc[i - 1, field]
            df.loc[i, field] = neighbours // 2


def empty_lists_to_nan(df,fields):
    df[fields] = df[fields].applymap(lambda l: np.nan if type(l) is list and len(l) < 1 else l)


def extract_links(df):
    # Lets extract all links, youtube links and timecodes
    df["link"] = df.content.str.findall(URL)
    df["yt_link"] = df[df.link.map(len, na_action="ignore") > 0].content.str.findall(YT_LINK)
    df["timecodes"] = df[df.yt_link.map(len, na_action="ignore") > 0].content.str.findall(TC)
    # Get rid of empty lists
    empty_lists_to_nan(df, ["yt_link", "timecodes", "link"])


class DataFrame(pd.DataFrame):
    def cleanup(self):
        # CLEANUP TIME
        # Flatten unnecessary dictionaries (if dict contains just 1 article)
        self.author = self.author.map(lambda d: d[list(d.keys())[0]] if type(d) is dict and len(d) == 1 else d)
        self.quotedFileContent = self.quotedFileContent.map(lambda d: d[list(d.keys())[0]] if type(d) is dict and len(d) == 1 else d)
        # Drop deleted and resolved comments
        self.drop(self.loc[self.deleted | self.resolved].index, inplace=True)
        # And drop deleted and resolved cols. We got everything we wanted
        self.drop(["deleted", "resolved"], axis=1, inplace=True)