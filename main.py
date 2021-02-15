from gdoc import GDoc, LinkChecker
from datetime import datetime
from downloader import Downloader
from dataframe import DataFrame, guess_lost_indexes, extract_links

FIELDS = "comments(content,quotedFileContent/value,id,author/displayName,deleted,resolved),nextPageToken"
DATE_STR = datetime.now().strftime("%-y-%m-%d")


def main():
    doc = GDoc(FIELDS)
    doc.get_link()
    doc.get_doc()

    if len(doc.comments) > 0:
        df = DataFrame(doc.comments)
        df.cleanup()
        # Lets find where in text out comments are
        df["index_in_file"] = doc.find_indexes(df.quotedFileContent)
        guess_lost_indexes(df)
        # Sort and create numbers
        df.sort_values(by=["index_in_file"], ignore_index=True, inplace=True, na_position="first")
        df["n"] = df.index.map(lambda n: n+1)
        extract_links(df)

        if input("Check links? (time for tea break) y/n ").lower() in ["y", "yes", "+"]:
            check = LinkChecker(df, "link")

        if input("Numerate all comments in document? (may take a pretty long time as well) y/n ").lower() in ["y", "yes", "+"]:
            doc.numerate(df)

        path = input(f"Path (default is ~/Downloads/Video-{DATE_STR}, press Enter to leave it default): ")
        if path == "":
            path = "~/Downloads/Video-" + DATE_STR + "/"
        Downloader(df, "yt_link", "n", "timecodes", "quotedFileContent", path)


while True:
    try:
        main()
        break
    except:
        pass