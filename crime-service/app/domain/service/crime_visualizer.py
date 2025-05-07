import numpy as np
import pandas as pd
import os
from app.domain.model.reader_schema import ReaderSchema
from sklearn import preprocessing
from app.domain.model.google_map_schema import GoogleMapSchema
import folium
import logging
from fastapi import HTTPException
import traceback    

logger = logging.getLogger("map_visualizer")

class MapVisualizer:
    def __init__(self):
        self.reader = ReaderSchema()
        self.crime_rate_columns = ['살인검거율', '강도검거율', '강간검거율', '절도검거율', '폭력검거율']
        self.crime_columns = ['살인', '강도', '강간', '절도', '폭력']
        self.orginal_data = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'orginal_data')
        self.derived_data = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'derived_data')
        self.stored_map = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'stored_map')
        self.cctv = None
        self.crime = None
        self.police = None
        self.pop = None
    
   


        

    def draw_crime_map2(self) -> object:
        file = self.file
        reader = self.reader
        file.context = self.derived_data
        file.fname = 'police_norm'
        police_norm = reader.csv_to_dframe(file)
        file.context = self.original_data
        file.fname = 'geo_simple'
        state_geo = reader.load_json(file)
        file.fname = 'crime_in_seoul'
        crime = reader.csv_to_dframe(file)
        file.context = self.derived_data
        file.fname = 'police_pos'
        police_pos = reader.csv_to_dframe(file)
        station_names = []
        for name in crime['관서명']:
            station_names.append('서울' + str(name[:-1] + '경찰서'))
        station_addrs = []
        station_lats = []
        station_lngs = []
        gmaps = reader.gmaps()
        for name in station_names:
            temp = gmaps.geocode(name, language='ko')
            station_addrs.append(temp[0].get('formatted_address'))
            t_loc = temp[0].get('geometry')
            station_lats.append(t_loc['location']['lat'])
            station_lngs.append(t_loc['location']['lng'])

        police_pos['lat'] = station_lats
        police_pos['lng'] = station_lngs
        col = ['살인 검거', '강도 검거', '강간 검거', '절도 검거', '폭력 검거']
        tmp = police_pos[col] / police_pos[col].max()
        police_pos['검거'] = np.sum(tmp, axis=1)

        folium_map = folium.Map(location=[37.5502, 126.982], zoom_start=12, title='Stamen Toner')

        folium.Choropleth(
            geo_data=state_geo,
            data=tuple(zip(police_norm['구별'],police_norm['범죄'])),
            columns=["State", "Crime Rate"],
            key_on="feature.id",
            fill_color="PuRd",
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name="Crime Rate (%)",
            reset=True,
        ).add_to(folium_map)
        for i in police_pos.index:
            folium.CircleMarker([police_pos['lat'][i], police_pos['lng'][i]],
                                radius=police_pos['검거'][i] * 10,
                                fill_color='#0a0a32').add_to(folium_map)

        folium_map.save(os.path.join(self.stored_map, 'crime_map.html'))

        return {"message": '서울시의 범죄 지도가 완성되었습니다.'}
        

