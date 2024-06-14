
import pandas as pd
from geopy.distance import geodesic

from .resources import resource_path

def load_line(line):
    '''
    Load line/stations into standard format.

    args:
        - line (iterable or string): list of lat/long coordinates or a named
        line in the package (see argoline.names for a full list).
    returns:
        pandas.DataFrame: dataframe with station name, latitude, longitude
        fields. If no station names exist, simply counts in order give.
    '''

    if type(line) is str:
        df_line = pd.read_csv(resource_path(f'{line.lower()}.csv'))
    else:
        raise NotImplementedError('Numerical or file input not yet supported')
    
    return df_line

def measure_distance(line, index):
    '''
    Measure the distance of each profile in `index` away from `line`.
    '''
    
    distance = [
        min([
            geodesic((lat, long), (slat, slong)).km for slat, slong in zip(line.latitude, line.longitude)
        ]) for lat, long in zip(index.latitude, index.longitude)
    ]

    return distance

def nearest_station(line, index):

    station = []
    for lat, long, dist in zip(index.latitude, index.longitude, index.distance_from_line):
        for slat, slong, stn in zip(line.latitude, line.longitude, line.station):
            if geodesic((lat, long), (slat, slong)) == dist:
                station.append(stn)
                break
    
    return station

def along_line(line, index):

    lx = line.set_index('station')
    s1 = line.station.iloc[0]

    along = [
        geodesic((lx.loc[s1].latitude, lx.loc[s1].longitude), (lx.loc[s].latitude, lx.loc[s].longitude)).km for s in index.nearest_station
    ]

    return along

def profiles(line, radius, date, variable='core', source='argopandas'):
    '''
    Find all profiles within `radius` of `line` in the given `date` limits.

    args:
        - line (iterable or string): list of lat/long coordinates or a named
        line in the package (see argoline.names for a full list).
        - radius (scalar): radius in kilometers of acceptable distance profiles
        can be away from `line`. 
        - date: (string, date, or iterable): date limits in "yyyy-mm" or 
        "yyyy-mm-dd" format for strings, or as pandas.Timestamp or datetime
        objects. Can provide only the minimum date (with implicit present as
        upper limit) or a date window as a tuple.
        - variable: Argo variable of interest. If none given, core variables are
        assumed. If BGC variable, synthetic profiles are used. Proper Argo variable
        names must be used (e.g. "TEMP", "DOXY")
        - source (string): preferred python package to source data, argopandas or 
        argopy
    
    returns:
        - pandas.DataFrame: index of the profiles that fit the above criteria. Can
        use argopandas index.levels to access profile data.
    '''

    if source == 'argopandas':
        import argopandas as argo

        # grab the appropriate index
        if variable in ['core', 'TEMP', 'PSAL']:
            ix = argo.prof
        else:
            ix = argo.synthetic_prof.subset_parameter(variable)
        
        # subset for dates
        ix = ix.subset_date(date)

        # draw a box around the line to subset the data before measuring distances
        line = load_line(line)
        ix = ix.subset_rect(
            line.latitude.min(), line.longitude.min(),
            line.latitude.max(), line.longitude.max()
        )

    elif source == 'argopy':
        import argopy
        argopy.set_options(mode='expert')

        # grab the appropriate index
        if variable in ['core', 'TEMP', 'PSAL']:
            ix = argopy.ArgoIndex().load()
        else:
            ix = argopy.ArgoIndex('bgc-s').load().search_params(variable)
        
        # draw a box around the line to subset the data before measuring distances
        line = load_line(line)
        ix = ix.search_lat_lon_tim([
            line.longitude.min(), line.longitude.max(),
            line.latitude.min(), line.latitude.max(),
            date[0], date[1]
        ]).to_dataframe()

    # measure distance of each profile from line
    ix['distance_from_line'] = measure_distance(line, ix)
    ix = ix.loc[ix.distance_from_line < radius]
    ix['nearest_station'] = nearest_station(line, ix)
    ix['distance_along_line'] = along_line(line, ix)

    return ix