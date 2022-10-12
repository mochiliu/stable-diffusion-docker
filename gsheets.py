"""Wrap functions in pygsheets so that I don't have to think about authorizaiton.

Setup
-----

First, Authorize gsheets via a service account, via:
https://pygsheets.readthedocs.io/en/stable/authorization.html#service-account

Download the service account JSON, and copy it into a .env or otherwise export it to the 
environment under the variable GOOGLE_SERVICE_ACCT_JSON.

You must then share the sheets you'd like to operate on with the client email fromn the 
JSON, which should look like: <name>@<project>-<id>.iam.gserviceaccount.com

From there you SHOULD be good to go.
"""
import pygsheets
import pandas as pd
import os

API_ENV_VAR_NAME = "GOOGLE_SERVICE_ACCT_JSON"


def get_client() -> pygsheets.authorization.Client:
    """Grabs the client from the environment variable."""
    if os.getenv(API_ENV_VAR_NAME) is None:
        raise EnvironmentError(
            'Service account JSON not found in environment variable "{}".'.format(
                API_ENV_VAR_NAME
            )
        )
    return pygsheets.authorize(service_account_env_var=API_ENV_VAR_NAME)


def sheet_to_dataframe(sheet_key: str, tab_name: str, **kw) -> pd.DataFrame:
    """Grabs the data from a sheet/tab.

    All kwargs passed to pygsheets.Worksheet.get_as_df()
    https://pygsheets.readthedocs.io/en/latest/worksheet.html#pygsheets.Worksheet.get_as_df
    """
    client = get_client()
    sheet = client.open_by_key(sheet_key)
    tab = sheet.worksheet_by_title(tab_name)
    return tab.get_as_df(**kw)


def dataframe_to_sheet(df: pd.DataFrame, sheet_key: str, tab_name: str, start: tuple=(1,1), **kw) -> None:
    """Updates the data from a sheet/tab.

    All kwargs passed to pygsheets.Worksheet.set_dataframe()
    https://pygsheets.readthedocs.io/en/stable/_modules/pygsheets/worksheet.html#Worksheet.set_dataframe
    """
    client = get_client()
    sheet = client.open_by_key(sheet_key)
    tab = sheet.worksheet_by_title(tab_name)
    tab.clear(start='A1', end=None, fields='*')
    tab.set_dataframe(df, start, **kw)

    
def get_last_updated_time(sheet_key: str) -> pd.Timestamp:
    """gets the last updated timestamp

    https://pygsheets.readthedocs.io/en/stable/spreadsheet.html#pygsheets.Spreadsheet
    """
    client = get_client()
    sheet = client.open_by_key(sheet_key)

    return pd.to_datetime(sheet.updated)