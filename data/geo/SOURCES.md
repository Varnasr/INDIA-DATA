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
