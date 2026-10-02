# Constituency boundaries

`bihar.json`, `tamilnadu.json`, `westbengal.json`, `kerala.json` and `karnataka.json` are drawn
from DataMeet's assembly constituency map (`assembly-constituencies/India_AC.shp`,
github.com/datameet/maps), licensed CC BY 2.5 India. Every page that draws one
credits it under the map.

Each was cut to one state, dissolved on `AC_NO`, reduced to the single field
`ac` and simplified with mapshaper:

    mapshaper India_AC.shp -filter "ST_NAME=='WEST BENGAL'" -dissolve2 AC_NO \
      -rename-fields ac=AC_NO -filter-fields ac -simplify 6% keep-shapes -clean \
      -o format=geojson precision=0.001

The seat numbers were checked against each state's data: every constituency in
the data has one shape and every shape a constituency. The boundaries are those
of the 2008 delimitation, which all five states' 2025 and 2026 rolls use.
`karnataka.json` is by election district, because the revision was published
by district only: the constituencies are joined to their district from
`data/karnataka/raw/ac_district.csv` (the Election Commission's own list, see
`SOURCES.md` there) and dissolved, with `ac` holding the district's position in
the Chief Electoral Officer's tables and `name` its name as the pages print it.
The shapefile carries one Bengaluru polygon with no constituency number
(`AC_NO` 0, about 9 sq km), which is left out.

# State boundaries

`india.json` is DataMeet's map of India's states (`States/Admin2.shp`,
github.com/datameet/maps), licensed CC BY 4.0, with the 36 states and union
territories as they stand since 2020 (Ladakh, and Dadra and Nagar Haveli and
Daman and Diu, are present). Its outline follows India's official boundary,
the same as DataMeet's `Country/india-composite.geojson`. Reduced with
mapshaper:

    mapshaper Admin2.shp -each "ac=this.id+1, name=ST_NM" -filter-fields ac,name \
      -filter-islands min-area=40km2 -simplify 0.8% keep-shapes \
      -o format=geojson precision=0.01

Lakshadweep's islands are all smaller than the island filter, so they were
simplified separately (5%, keep-shapes) and added back. Do not run `-clean`
on this file: on these boundaries it undoes the simplification and the file
returns to 1.5 MB. The front page joins it to `data/india/states.json` by
name, with `Andaman & Nicobar` and `Jammu & Kashmir` mapped to the names
there.
