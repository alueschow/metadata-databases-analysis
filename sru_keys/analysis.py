#!/usr/bin/python
# -*- coding: utf-8 -*-

"""A script for comparing search possibilities across all SRU endpoint from the GBV (Gemeinsamer Bibliotheksverbund)."""

import json
import os
import pandas as pd

from loguru import logger
from progress.bar import Bar

from polymatheia_tools.download.sru_call import SRUCall


def create_json():
    """Analyse SRU search keys and create JSON file."""
    # set up logging
    logging_filename = "./log/sru_keys_{time}.log"
    logging_format = "{time} {level} {message}"
    logger.remove()
    logger.add(logging_filename, format=logging_format, level="DEBUG")

    # variables
    encoding = "utf-8"
    database_tsv = os.path.join("./data", "gbv_databases.tsv")
    json_output_file = os.path.join("./data", "gbv_databases_keys.json")

    # open GBV databases file
    with open(database_tsv, "r", encoding=encoding) as f:
        df = pd.read_csv(f, sep="\t")

    key_dict = {}

    with Bar("Progress:", max=len(df["srubase"])) as progressbar:
        for sru in df["srubase"]:
            dbkey = df[df["srubase"] == sru].iloc[0]["dbkey"]
            try:
                keys = SRUCall.keys(sru)
                keys = keys.split("\n")
                for k in keys:
                    kk = k.split(" ")[0]
                    if kk in key_dict.keys():
                        if sru not in key_dict[kk]["db"]:
                            key_dict[kk]["count"] += 1
                            key_dict[kk]["db"].append(dbkey)
                    else:
                        key_dict[kk] = {}
                        key_dict[kk]["count"] = 1
                        key_dict[kk]["db"] = []
                        key_dict[kk]["db"].append(dbkey)
            except:
                logger.debug(f"Database '{dbkey}' is not available.")
            progressbar.next()

    with open(json_output_file, "w", encoding=encoding) as ofile:
        ofile.write(json.dumps(key_dict, indent=4))

    print(f"See log file {logging_filename} for more information about the process.")


if __name__ == "__main__":
    create_json()
