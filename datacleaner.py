import os.path
from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path
from io import FileIO

import requests
import rispy
import pandas as pd

import logging
from termcolor import colored

try:
    import readline
except:
    pass #readline not available

#logger = logging.getLogger(__name__)

class DataCleaner:
    """
    Cleans the data from a ris file.
    Removes duplicate entries, entries without title and entries without abstract
    """

    def __init__(self, logger: logging.Logger = logging.getLogger(__name__)):
        # entries to be cleaned
        self.logger = logger
        self.in_entries: list[dict] = []

        # output entries
        self.out_entries: list[dict] = []

    def count_in_entries(self) -> int:
        """Returns the total number of input entries"""

        return len(self.in_entries)

    def count_out_entries(self) -> int:
        """Returns the total number of output entries"""

        return len(self.out_entries)

    def add_file(self, file: FileIO | Path | str) -> None:
        """Adds the entries from a file to self.in_entries"""
        if isinstance(file, str):
            file = Path(file)
        self.in_entries = self.in_entries + rispy.load(file, encoding='utf-8')

    def clean_entries(self) -> tuple[int, int, int, int]:
        """
        Removes duplicates, entries without title, entries without abstract and entries without doi
        :returns tuple: (number of duplicates, number of entries without title, number of entries without abstract, number of entries without doi)
        """
        df = pd.DataFrame(self.in_entries)

        # Check if titles exist in any entry
        if 'title' not in df.columns:
            print("No regular title entries found, checking for primary title")
            # Check if primary_title exists (ScienceDirect uses primary_title (T1) when export RIS instead of title (TI)
            if 'primary_title' in df.columns:
                # Copy data from primary_title to title
                df['title'] = df.loc[:, 'primary_title']
            # If neither exist, the file could be invalid or corrupted
            else:
                raise Exception("Title and Primary Title do not exist, check the export options for the file on the database!")
        # If both title and primary title exist, fill empty title values with the primary title
        elif 'primary_title' in df.columns and 'title' in df.columns:
            df['title'] = df['title'].fillna(df['primary_title'])
            df['primary_title'] = df['primary_title'].fillna(df['title'])

        data_size = df.shape[0]
        clean_df = df

        # Checking the DOI column
        # Some databases export the DOI as a link, so we need to extract the DOI from the link
        # We do this by removing the 'https://doi.org/' part of the link and keeping the rest
        if 'doi' in clean_df.columns:
            clean_df['doi'] = clean_df['doi'].str.replace('https://doi.org/', '')


        # Removing no DOI entries
        # If an entry does not have a Digital Object Identifier, it is removed as we cannot retrieve the PDF
        #  and the article itself probably isn't very relevant
        # We remove these first, because when removing duplicates, we guarantee to have the version with doi, as the non doi is already gone (happens in a lot more than I thought)
        clean_df, n_no_doi = self.clean_no_doi(clean_df)

        # Removing no title
        clean_df, n_no_title = self.clean_no_title(clean_df)

        # Removing no abstract
        clean_df, n_no_abstract = self.clean_no_abst(clean_df)

        # Removing duplicates.
        # Duplicates are removed last, as the other method eliminate the articles that are "bad data" first
        clean_df, n_duplicated = self.clean_duplicate(clean_df)

        # store the clean data to out_entries, so we can export later
        self.out_entries = clean_df.to_dict("records")

        # remove keys when value is NaN
        self.out_entries = [{k: v for k, v in x.items() if v == v} for x in self.out_entries]

        return n_duplicated, n_no_title, n_no_abstract, n_no_doi

    def log_removal(self, df: pd.DataFrame):
        """Logs the removal of a result with its title, authors, type and doi (if these exist)"""
        rem_entries = df[['title', 'authors', 'type_of_reference', 'doi']].to_dict("records")
        rem_entries = [{k: v for k, v in x.items() if v == v} for x in rem_entries]
        for entry in rem_entries:
            self.logger.info(entry)

    def clean_no_doi(self, clean_df):
        df = clean_df
        self.logger.info("NO DOI:")
        self.log_removal(df[df['doi'].isnull()])
        clean_df = df.dropna(subset=['doi'])

        self.logger.info("DOI NOT REGISTERED:")
        # check the validity of all DOIs, using https://doi.org/api/handles/DOI. If the response code is not 1, the DOI is invalid
        # This is done to prevent the program from trying to download a PDF from a non-existing DOI
        with ThreadPoolExecutor(int(len(self.in_entries) / 5)) as executor:
            valid_dois = list(executor.map(self.is_valid_doi, clean_df['doi']))

        valid_dois_series = pd.Series(valid_dois, index=clean_df.index)
        self.log_removal(clean_df[~valid_dois_series])
        clean_df = clean_df[valid_dois_series]

        n_no_doi = df.shape[0] - clean_df.shape[0]
        return clean_df, n_no_doi

    def is_valid_doi(self, doi):
        return requests.get(f'https://doi.org/api/handles/{doi}').json()['responseCode'] == 1

    def clean_no_abst(self, clean_df):
        df = clean_df
        self.logger.info("NO ABSTRACT:")
        self.log_removal(df[df['abstract'].isnull()])
        clean_df = df.dropna(subset=['abstract'])
        n_no_abstract = df.shape[0] - clean_df.shape[0]
        return clean_df, n_no_abstract

    def clean_no_title(self, clean_df):
        df = clean_df
        self.logger.info("NO TITLE:")
        self.log_removal(df[df['title'].isnull()])
        clean_df = df.dropna(subset=['title'])
        n_no_title = df.shape[0] - clean_df.shape[0]
        return clean_df, n_no_title

    def clean_duplicate(self, df):
        # Removing duplicates (An entry is considered a duplicate if the title and type (Journal, Article, etc...)
        # are the same. We keep the first entry in the dataframe because that one is usually the most relevant,
        # per the Web Of Science criteria.
        self.logger.info("DUPLICATES [Title and type]:")
        self.log_removal(df[df.duplicated(subset=['title', 'type_of_reference'], keep='first')])
        clean_df = df.drop_duplicates(subset=['title', 'type_of_reference'], keep='first')
        self.logger.info("DUPLICATES [DOI]:")
        self.log_removal(df[df.duplicated(subset=['doi'], keep='first')])
        clean_df = clean_df.drop_duplicates(subset=['doi'], keep='first')
        n_duplicated = df.shape[0] - clean_df.shape[0]
        return clean_df, n_duplicated

    def export_data(self, path: str = ""):
        """Exports the cleaned data to a file named out.ris in the path specified"""
        if Path(path).is_file() or Path(path).suffix == '.ris':
            raise ValueError("The path is a file, not a directory!")
        os.makedirs(os.path.abspath(path), exist_ok=True)
        with open(path + '/out.ris', 'w', encoding='utf-8') as outfile:
            rispy.dump(self.out_entries, outfile)
        print("Cleaned results exported to " + path + '/out.ris')

    def export_data_tofile(self, file: FileIO | Path | str):
        """Exports the cleaned data to a file"""
        if isinstance(file, str):
            file = Path(file)
        if isinstance(file, Path):
            if file.is_dir():
                raise Exception("The path is a directory, not a file!")
            if file.suffix != '.ris':
                raise Exception("The file is not a RIS file!")
        rispy.dump(self.out_entries, file)
        print("Cleaned results exported to " + file.name)

if __name__ == '__main__':
    # check if the log folder exists, if not, create it
    os.makedirs("log", exist_ok=True)
    logging.basicConfig(filename="log/datacleaner.log", level=logging.INFO, encoding='UTF-8', filemode='w')
    logger = logging.getLogger(__name__)
    cleaner = DataCleaner(logger)
    #cleaner.add_file('testdata/artf-intl-wos.ris')

    print("Path of the files to import (Press ENTER with empty input to terminate).")
    f = input(": ").replace('"', '')
    while len(f) > 0:
        try:
            cleaner.add_file(os.path.abspath(f))
        except FileNotFoundError:
            print(colored("The file doesn't exist! Please try again.", "red"))
        f = input(": ").replace('"', '')

    print(f'Total number of articles imported: {cleaner.count_in_entries()}')
    print("Cleaning data...")

    start_time = pd.Timestamp.now()

    n_dup, n_no_title, n_no_abst, n_no_doi = cleaner.clean_entries()
    clean = cleaner.count_out_entries()

    end_time = pd.Timestamp.now()

    print(f'Number of duplicated entries: {n_dup}')
    print(f'Number of entries without title: {n_no_title}')
    print(f'Number of entries without abstract: {n_no_abst}')
    print(f'Number of entries without doi: {n_no_doi}')
    print(f'Number of entries after cleanup: {clean}')
    print("Additional info about removed files in log/datacleaner.log")
    #print(f"Time taken: {end_time - start_time}")
    logger.info(f"Time taken: {end_time - start_time}")

    cleaner.export_data("export")
