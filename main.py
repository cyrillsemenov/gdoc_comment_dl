from datetime import datetime
from downloader import Downloader
from dataframe import DataFrame, guess_lost_indexes, extract_links
import argparse
import os


# TODO: Man, can you document this shit?
parser = argparse.ArgumentParser(description='Download all link from GDocs comments.')
parser.add_argument('--link', dest='link', default=None, help='Link or ID of GDoc (does not have an effect yet)')
parser.add_argument('--creds', dest='creds', default=None, help='Path of Google API credentials .json file')
parser.add_argument('--test', dest='test', default=None, help='ID or Link of file for test')
args = parser.parse_args()

if args.creds:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = args.creds
if args.test:
    os.putenv("TEST_ID", args.test)
if args.link:
    # TODO: Implement adding link from arguments instead of input option
    pass

from gdoc import GDoc, LinkChecker

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


# while True:
#     # TODO: I don't like this construction
#     main()
#     # try:
#     #
#     #     break
#     # except Exception as e:
#     #     print(e)

if __name__ == '__main__':
    main()
