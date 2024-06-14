# argoline
Reconstruct an oceanographic line using Argo profiles

Using [argopy]() or [argopandas]() as data sources, fetch all profiles within
a defined _date_ range and _radius_ kilometers from a given oceanographic _line_:

```python
import argoline as al

line = 'ar7w' # some lines built in, otherwise can be supplied numerically
radius = 150 # km
date = ['2024-05-01', '2024-06-01']

index = al.profiles(line, radius, date, source='argopy')

print(index.head())
```

```
>>> 
                                        file                date  ...  profiler  distance_from_line
0  coriolis/5906994/profiles/R5906994_032.nc 2024-05-08 22:08:00  ...   Unknown           27.744760
1  coriolis/5906994/profiles/R5906994_033.nc 2024-05-18 23:12:00  ...   Unknown           82.483724
2  coriolis/5906994/profiles/R5906994_034.nc 2024-05-28 23:11:00  ...   Unknown           66.342931
3  coriolis/5906994/profiles/R5906994_035.nc 2024-06-07 23:47:00  ...   Unknown           89.029014
4  coriolis/6902895/profiles/R6902895_072.nc 2024-05-09 21:49:00  ...   Unknown           86.584376
```