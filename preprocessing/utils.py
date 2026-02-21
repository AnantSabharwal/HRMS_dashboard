import pandas as pd
import numpy as np


# function to rename a column
def rename_column(df, old_column_name, new_column_name):
    return df.rename(columns={old_column_name: new_column_name})


# function to full future missing column values based on last filled column values
def fillna_forward(df, column_name):
    df[column_name] = df[column_name].fillna(method='ffill')
    return df
