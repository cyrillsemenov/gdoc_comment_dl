from googleapiclient.discovery import build
from google.oauth2 import service_account
from apiclient import errors
from progress.bar import Bar
from time import perf_counter
import os
import requests
import ast
import re
import json
from regex import GOOGLE_ID

CRED_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", None)
TEST_ID = os.getenv("TEST_ID", None)

with open(CRED_FILE) as app_creds:
    credentials = service_account.Credentials.from_service_account_info(json.load(app_creds))


def read_paragraph_element(element):
    """
    Returns the text in the given ParagraphElement.

    :param element: a ParagraphElement from a Google Doc.
    """
    text_run = element.get("textRun")
    if not text_run:
        return ""
    return text_run.get("content")


def read_strucutural_elements(elements):
    """
    Recurses through a list of Structural Elements to read a document's text where text may be in nested elements.
    :param elements: a list of Structural Elements.
    """
    text = ""
    for value in elements:
        if "paragraph" in value:
            elements = value.get("paragraph").get("elements")
            for elem in elements:
                text += read_paragraph_element(elem)
        elif "table" in value:
            # The text in table cells are in nested Structural Elements and tables may be
            # nested.
            table = value.get("table")
            for row in table.get("tableRows"):
                cells = row.get("tableCells")
                for cell in cells:
                    text += read_strucutural_elements(cell.get("content"))
        elif "tableOfContents" in value:
            # The text in the TOC is also in a Structural Element.
            toc = value.get("tableOfContents")
            text += read_strucutural_elements(toc.get("content"))
    return text


def return_id(s):
    return re.findall(GOOGLE_ID, s)[0]


class GDoc:
    def __init__(self, fields, page_size=100):
        self.file_id = ""
        self.fields = fields
        self.content = ""
        self.page_size = page_size
        self.next_page_token = ""
        self.comments = []
        self.doc_attempts = 4

    def get_link(self):
        file = input("Paste link to GDoc file: ")

        try:
            if TEST_ID:
                self.file_id = TEST_ID if file.lower() == "test" else return_id(file)
            else:
                self.file_id = return_id(file)
        except IndexError:
            print("Wrong link provided. Try again.")
            self.get_link()

    def get_doc(self):
        # Get comments and full text of GDoc
        try:
            with build("docs", "v1", credentials=credentials) as service:
                self._get_content(service)
            with build("drive", "v3", credentials=credentials) as service:
                self._get_comments(service)
        except:
            print(f"Something went wrong. Try again({self.doc_attempts})...")
            self.doc_attempts -= 1
            if self.doc_attempts > 0:
                self.get_doc()
            else:
                print(f"Sorry, can't reach the file.")
                self.doc_attempts = 4

    def numerate(self, df, content="n", id="id"):
        """
        Post indexes of comments as replies in doc.

        :param df: Pandas dataframe
        :param content: name of column containing content of reply
        :param id: name of column containing id of comment
        """
        bar = Bar("Processing", max=len(df[id]))
        with build("drive", "v2", credentials=credentials) as service:
            dic = df[[content, id]].to_dict()
            for key in dic[id]:
                new_reply = {"content": dic[content][key]}
                try:
                    service.replies().insert(fileId=self.file_id, commentId=dic[id][key], body=new_reply).execute()
                except errors as error:
                    print("An error occurred: %s" % error)
                bar.next()
        bar.finish()

    def _get_content(self, service):
        print("Loading file contents... ", end="")
        time_start = perf_counter()
        try:
            doc = service.documents().get(documentId=self.file_id).execute()
            self.content = read_strucutural_elements(doc.get("body", {}).get("content", None))
            print(f"{round(perf_counter() - time_start, 4)} seconds")
        except errors as error:
            print(f"\nAn error occurred: {error}")

    def _get_comments(self, service):
        time_start = perf_counter()
        text = "Loading file comments... "
        print(text, end="\r")
        while True:
            try:
                results = service.comments().list(fileId=self.file_id,
                                                  pageSize=self.page_size,
                                                  fields=self.fields,
                                                  pageToken=self.next_page_token,
                                                  includeDeleted=False).execute()
                self.comments.extend(results.get("comments", []))
                self.next_page_token = results.get("nextPageToken")
                print(text + f"{round(perf_counter() - time_start, 4)} seconds", end="\r")
            except errors.HttpError as error:
                print(f"\nAn error occurred: {error}")
                break
            if not bool(self.next_page_token):
                print("\n", end="")
                break

    def find_indexes(self, iterable):
        """
        Returns list of indexes of iterable elements in source text.
        """
        indexes = []
        for i in iterable:
            indexes.append(self.content.find(i))
        return indexes


class LinkChecker:
    def __init__(self, dataframe, field):
        self.df = dataframe
        self.field = field
        # self.responses
        self.errors = []
        self.start()
        if len(self.errors) > 0:
            print("Following links contain errors (are you sure there are no typos?):\n"+"\n".join(self.errors))

    def start(self):
        with Bar("Checking links...", max=len(self.df[self.field])) as self.bar:
            self.df["responses"] = self.df[self.field].map(self._get_status_code)

    def _get_status_code(self, links):
        self.bar.next()
        if type(links) is str:
            links = ast.literal_eval(links)

        if type(links) is list:
            status = []
            for link in links:
                try:
                    code = requests.get(link).status_code
                    if code > 200:
                        self.errors.append(f"{code} - {link}")
                    status.append(code)
                except Exception as e:
                    self.errors.append(f"{e} - {link}")
                    status.append(e)
        else:
            return None
        return status
