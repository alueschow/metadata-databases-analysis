#!/usr/bin/python
# -*- coding: utf-8 -*-

"""A script for visualizing SRU search keys of SRU endpoints from the GBV (Gemeinsamer Bibliotheksverbund)."""

import os
import pandas as pd


def visualize():
    """Visualize search key distribution across multiple GBV databases."""
    # variables
    encoding = "utf-8"
    databases_json = os.path.join("./data", "gbv_databases_keys.json")
    json_sorted = os.path.join("./data", "gbv_databases_keys_sorted.json")
    figure_file = os.path.join("./data", "gbv_databases_keys.png")

    # database URIs that will be used for visualization. If list is empty, all available URIs will be used
    databases = []
    # e.g., databases = ["opac-de-7"]

    # if a key is used in less than X databases, it will be ignored
    count_threshold = 0

    # if th following parameter is given, only those search keys will be used; otherwise, all keys will be used
    keys = []
    # e.g., keys = ["per", "tit", "bib", "sw"]

    # open file
    with open(databases_json, "r", encoding=encoding) as f:
        df = pd.read_json(f, orient="index")
    print(df)

    # convert and sort values
    df['count'] = pd.to_numeric(df['count'])
    df = df.sort_values(by='count', ascending=False)

    # save file
    with open(json_sorted, "w", encoding=encoding) as f:
        f.write(df.to_json(orient="index", indent=4))
    print(df)

    # delete unwanted rows
    to_delete = list()
    for i, row in df.iterrows():
        if len(keys) > 0 and i.lower() not in keys:
            to_delete.append(i)
        if len(databases) > 0 and set(row.db).isdisjoint(databases):
            to_delete.append(i)
        if row["count"] < count_threshold:
            to_delete.append(i)
    df = df.drop(to_delete)

    # plot
    fig = df.plot.bar(x=None, y="count").get_figure()
    fig.set_size_inches(30, 12)
    fig.savefig(figure_file, bbox_inches='tight')


if __name__ == "__main__":
    visualize()
