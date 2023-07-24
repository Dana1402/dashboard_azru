# dashboard_azru

![](https://github.com/Dana1402/dashboard_azru/blob/master/demo.gif)

Dashboard is built with using Dash, Plotly Express and Css.
1. Firts thing first we get data from Database (Sql script+sqlalchemy). 
2. Then we preparing data (this part places also separatedly). On this step we need to map id of states from geojson with our dataset.
   To do this we search in text address the best fit by comparing texts. Then we set up the best fit state.
   (The try with API and Geocoder worked worse and more code)
4. On the mapbox I get distribution of insured premia or number of policies depends what filter is set.
5. There is also policy conclusion year filter.
6. On the bottom part we see premia and distribution on sale channels per months depends on region we clicked on the upper map.
