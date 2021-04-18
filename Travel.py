'''import export as export
from mapbox import Directions

service = Directions(access_token="pk.eyJ1Ijoicm92ciIsImEiOiJja25tZXJlZXYwcHNkMm9tMHd3c2RrbWRxIn0.0xMzD3AuAcFXbbocVYEiLA")

#-122.7282, 45.5801, -121.3153, 44.0582
origin = { 'type': 'Feature',
            'properties': {'name': 'Portland, OR'},
            'geometry': {
            'type': 'Point',
            'coordinates': [-122.7282, 45.5801]}}
destination = {
                'type': 'Feature',
                'properties': {'name': 'Bend, OR'},
                'geometry': {
                'type': 'Point',
                'coordinates': [-121.3153, 44.0582]}}

response = service.directions([origin, destination],'mapbox/driving')
print(response.status_code)
driving_routes = response.geojson()
#print(driving_routes['features'][0]['geometry']['type'])
print(driving_routes['features'][0]['geometry']['coodinates'])
routes = driving_routes['features'][0]['geometry']['coodinates'];
print(routes.type)'''

from mapbox import Directions
import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.offline as pyo
import plotly.graph_objects as go

service = Directions(access_token="pk.eyJ1Ijoicm92ciIsImEiOiJja25tZXJlZXYwcHNkMm9tMHd3c2RrbWRxIn0.0xMzD3AuAcFXbbocVYEiLA")

origin = { 'type': 'Feature',
            'properties': {'name': 'Portland, OR'},
            'geometry': {
            'type': 'Point',
            'coordinates': [-122.7282, 45.5801]}}
destination = {
                'type': 'Feature',
                'properties': {'name': 'Bend, OR'},
                'geometry': {
                'type': 'Point',
                'coordinates': [-121.3153, 44.0582]}}

response = service.directions([origin, destination],'mapbox/driving')
print(response.status_code)
driving_routes = response.geojson()

waypoints = driving_routes['features'][0]['geometry']['coordinates']

df = pd.DataFrame(waypoints, columns=['long', 'lat'])

fig = go.Figure(go.Scattermapbox(
        mode = "markers+lines",
        lon = df.iloc[:, 0], lat = df.iloc[:, 1],
        marker = {'size': 40}, fillcolor = 'blue'))

fig.update_layout(
     mapbox = {
       'accesstoken': "pk.eyJ1Ijoicm92ciIsImEiOiJja25tZXJlZXYwcHNkMm9tMHd3c2RrbWRxIn0.0xMzD3AuAcFXbbocVYEiLA",
       'style': "satellite-streets", 'zoom': 15.0, 
       'center':dict(lat = origin['geometry']['coordinates'][1],lon = origin['geometry']['coordinates'][0])},
          showlegend = False)

fig.update_traces(marker=dict(size=6))
fig.show()
