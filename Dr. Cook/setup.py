import numpy as np
import pandas as pd

import webbrowser
import IPython.display as ipd
digits = 3
pd.options.display.chop_threshold = 10**-(digits+1)
pd.options.display.float_format = lambda x: '{0:.{1}f}'.format(x,digits)
pd.options.display.show_dimensions = True
def display(X, rows=None, where="inline", name="df"):
    if(rows == 'all'):
        rows = 2000
    elif(type(rows) is int):
        rows *= 2
    else:
        rows = 10

    if isinstance(X, pd.DataFrame) or isinstance(X, pd.Series) or (isinstance(X, np.ndarray) and X.ndim <=2):
        X = pd.DataFrame(X)
        if(where == "popup"):
            filename = name + ".html"
            X.to_html(filename)        
            webbrowser.open(filename,new=2)
        else:
            pd.set_option('display.max_rows', rows)
            ipd.display(X)
            pd.reset_option('display.max_rows')
    else:
        print(X)

def margins(df):
    df = pd.DataFrame(df)
    col_sums = df.sum(axis=0)
    df.loc['TOTAL'] = col_sums
    row_sums = df.sum(axis=1)
    df['TOTAL'] = row_sums
    return df