import pandas as pd, glob, os
import pathlib
ROOT=str(pathlib.Path(__file__).resolve().parents[1]/'data'/'matches')
def events():
    return pd.concat([pd.read_csv(f,low_memory=False) for f in sorted(glob.glob(f'{ROOT}/*/*_dynamic_events.csv'))],ignore_index=True)
def phases():
    return pd.concat([pd.read_csv(f) for f in sorted(glob.glob(f'{ROOT}/*/*_phases_of_play.csv'))],ignore_index=True)
