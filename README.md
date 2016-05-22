# transit
tool(s) for munging transit data from http://web.mta.info/developers/

# getting the data
totals.py expects data from files like http://web.mta.info/developers/data/nyct/turnstile/turnstile_160521.txt
to download a set of files used in the example below run

```bash
wget http://web.mta.info/developers/data/nyct/turnstile/turnstile_160521.txt
wget http://web.mta.info/developers/data/nyct/turnstile/turnstile_160514.txt
```

# usage
to specify which stations you want, you must modify the code in totals.py, only a subset are currently used

```bash
python totals.py <end_week> <start_week> > out.csv
```
using the data we downloaded above, it would be

```bash
python totals.py turnstile_160521.txt turnstile_160514.txt > out.csv
```

out.csv looks like:
```
station,entrances,exits,totals
MYRTLE-WYCKOFF,131406,85299,216705
DEKALB AV,81904,22735,104639
HALSEY ST,64975,37752,102727
SENECA AVE,17068,16585,33653
KNICKERBOCKER,26250,25769,52019
TIMES SQ-42 ST,610315,582437,1192752
BERGEN ST,25786,20759,46545
CARROLL ST,67984,27791,95775
JEFFERSON ST,52982,12495,65477
CENTRAL AV,23848,21809,45657
FOREST AVE,26710,20412,47122
```
depending which stations you select in totals.py
