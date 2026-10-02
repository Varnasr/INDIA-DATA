# Constituency boundaries

`bihar.json`, `tamilnadu.json`, `westbengal.json` and `kerala.json` are drawn
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
of the 2008 delimitation, which all four states' 2025 and 2026 rolls use.
Karnataka has no map because its revision was published by district only.
