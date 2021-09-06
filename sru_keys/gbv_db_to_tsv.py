#!/usr/bin/python
# -*- coding: utf-8 -*-

"""A script for retrieving database data from GBV Datenbankverzeichnis (https://uri.gbv.de/database/)
and putting it into a TSV format.
"""

import os
import pandas as pd
import requests


def _get():
    """Retrieve database data from GBV Datenbankverzeichnis."""
    encoding = "utf-8"

    tsv_file = "./data/gbv_databases.tsv"
    if not os.path.exists(tsv_file):
        os.mkdir(os.path.dirname(tsv_file))

    base_uri = "https://uri.gbv.de/database/?format=json"

    db = {}  # collect data here

    data = requests.get(base_uri).json()  # get data from URI

    for k in data.keys():  # iterate over databases
        if "http://uri.gbv.de/database/" in k:
            if not k.endswith("/"):  # i.e., it is a single database
                db = _fill_dict(db,
                                _get_values(data[k]))
            else:  # i.e., it is a database group
                for group in data[k]["http://www.w3.org/2004/02/skos/core#hasTopConcept"]:
                        group_uri = group["value"] + "?format=json"
                        group_data = requests.get(group_uri).json()  # call URI
                        for group_key in group_data.keys():
                            if "http://uri.gbv.de/database/" in group_key:
                                if "-" in group_key:
                                    db = _fill_dict(db,
                                                    _get_values(group_data[group_key]))

    # convert dict to DataFrame
    df = pd.DataFrame.from_dict(db, orient='index')
    df.index.name = 'dbkey'

    print(f"Number of databases found: {df.shape[0]}")

    # save to TSV file
    with open(tsv_file, "w", encoding=encoding) as f:
        df.to_csv(f, sep="\t")


def _get_values(d):
    """Get values of interest for a given database URI."""
    key = d["http://purl.org/ontology/gbv/dbkey"][0]["value"]
    titles = d["http://purl.org/dc/terms/title"]
    sru_base = d["http://purl.org/ontology/gbv/srubase"][0]["value"]
    return key, titles, sru_base


def _fill_dict(d, v):
    """Fill dictionary d with values from v."""
    key = v[0]
    titles = v[1]
    sru_base = v[2]

    d[key] = {}
    for title in titles:
        lang = title["lang"]
        value = title["value"]
        d[key][lang] = value
    d[key]["srubase"] = sru_base

    return d


if __name__ == "__main__":
    _get()
