#!/usr/bin/env python3

from appdirs import AppDirs
import pandas as pd
import webbrowser
import argparse
import requests
import json
import shutil
from pathlib import Path

dirs = AppDirs('ShadowSearch')
API_URL = 'https://shadowverse-portal.com/api/v1/cards?format=json&lang=en'
GUI_CARD_URL = 'https://shadowverse-portal.com/card/'
USER_DIR = Path(dirs.user_data_dir)
JSON_CACHE = USER_DIR / 'cards.json'


def update_json():
    """
    Downloads the latest Shadowverse json
    """
    USER_DIR.mkdir(parents=True, exist_ok=True)
    response = requests.get(API_URL, stream=True)
    with JSON_CACHE.open('wb') as cache:
        shutil.copyfileobj(response.raw, cache)


def get_df() -> pd.DataFrame:
    # Download the cache if we don't have it, but don't check if it's out of date
    if not JSON_CACHE.exists():
        update_json()

    # Load the cards into a data frame
    with JSON_CACHE.open() as json_fp:
        json_content = json.load(json_fp)
    return pd.DataFrame(json_content['data']['cards'])


def query_df(query, output) -> str:
    df = get_df()
    queried = df.query(query)

    if output == 'name':
        for card in list(queried.card_name):
            print(card)
    elif output == 'id':
        for card in list(queried.card_id):
            print(card)
    elif output == 'details':
        print(queried.to_csv(index=False, sep='\t'))
    elif output == 'browser':
        for id in queried.card_id:
            webbrowser.open_new_tab(GUI_CARD_URL + str(id))


def print_columns():
    df = get_df()
    for column in df.columns:
        print(column)


def run_cli():
    # Generate the parser and subparsers
    parser = argparse.ArgumentParser(description='Utility for finding Shadowverse cards')
    subparsers = parser.add_subparsers(dest='cmd')
    subparsers.required = True

    update = subparsers.add_parser('update', help='Update the Shadowverse JSON cache')
    update.set_defaults(func=lambda args: update_json())

    query = subparsers.add_parser('query', help='Search for Shadowverse cards that meet certain criteria')
    query.add_argument(
        'query_str',
        help='A pandas query string. Refer to the pandas documentation for more information: '
             'https://pandas.pydata.org/pandas-docs/stable/indexing.html#indexing-query. For information on the '
             'column names, use `{} columns`'.format(parser.prog)
    )
    query.add_argument('-o', '--output', choices=['name', 'id', 'details', 'browser'], default='name',
                       help='The way to output the query results. "name"'
                            'will print the card name, "id" will print its'
                            'id, and "browser" will open the Shadowverse '
                            'Portal page for each card returned')
    query.set_defaults(func=lambda args: query_df(args.query_str, args.output))

    columns = subparsers.add_parser('fields', help='Print out the names of the card fields that are useable in a query')
    columns.set_defaults(func=lambda args: print_columns())

    # Execute the command
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    run_cli()
