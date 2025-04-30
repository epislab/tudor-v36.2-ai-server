import numpy as np
import pandas as pd
import os
from app.domain.model.reader_schema import ReaderSchema
from sklearn import preprocessing
from app.domain.model.google_map_schema import GoogleMapSchema
from app.domain.model.crime_schema import CrimeSchema

class CrimeService:
    def __init__(self):
        self.dataset = CrimeSchema()
        self.reader = ReaderSchema()
        self.crime_rate_columns = ['살인검거율', '강도검거율', '강간검거율', '절도검거율', '폭력검거율']
        self.crime_columns = ['살인', '강도', '강간', '절도', '폭력']
        self.stored_data = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'stored_data')
        self.updated_data = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'updated_data')
    
    def preprocess(self, *args) -> object:
        print(f"------------모델 전처리 시작-----------")
        this = self.dataset
        for i in list(args):
            self.save_object_to_csv(this, i)
        return this
    
    def create_matrix(self, fname) -> object:
        print(f"😎🥇🐰파일명 : {fname}")
        self.reader.fname = fname
        if fname.endswith('csv'):
            return self.reader.csv_to_dframe()
        elif fname.endswith('xls'):
            return self.reader.xls_to_dframe(header=2, usecols='B,D,G,J,N')
    
    def save_object_to_csv(self, this, fname) -> object:
        print(f"🌱save_csv 실행 : {fname}")
        full_name = os.path.join(self.stored_data, fname)

        if not os.path.exists(full_name) and fname == "cctv_in_seoul.csv":
            this.cctv = self.create_matrix(fname)
            this = self.update_cctv(this)
            
        elif not os.path.exists(full_name) and fname == "crime_in_seoul.csv":
            this.crime = self.create_matrix(fname)
            this = self.update_crime(this) 
            this = self.update_police(this) 

        elif not os.path.exists(full_name) and fname == "pop_in_seoul.xls":
            this.pop = self.create_matrix(fname)
            this = self.update_pop(this)

        else:
            print(f"파일이 이미 존재합니다. {fname}")

        return this
    
    def update_cctv(self, this) -> object:
        print(f"------------ update_cctv 실행 ------------")
        this.cctv = this.cctv.drop(['2013년도 이전', '2014년', '2015년', '2016년'], axis=1)
        print(f"CCTV 데이터 헤드: {this.cctv.head()}")
        cctv = this.cctv
        cctv = cctv.rename(columns={'기관명': '자치구'})
        cctv.to_csv(os.path.join(self.stored_data, 'cctv_in_seoul.csv'), index=False)
        this.cctv = cctv
        return this
    
    def update_crime(self, this) -> object:
        print(f"------------ update_crime 실행 ------------")
        crime = this.crime
        station_names = []  # 경찰서 관서명 리스트
        for name in crime['관서명']:
            station_names.append('서울' + str(name[:-1]) + '경찰서')
        print(f"🔥💧경찰서 관서명 리스트: {station_names}")
        
        station_addrs = []
        station_lats = []
        station_lngs = []
        gmaps = GoogleMapSchema()  # 구글맵 객체 생성
        
        for name in station_names:
            tmp = gmaps.geocode(name, language='ko')
            print(f"""{name}의 검색 결과: {tmp[0].get("formatted_address")}""")
            station_addrs.append(tmp[0].get("formatted_address"))
            tmp_loc = tmp[0].get("geometry")
            station_lats.append(tmp_loc['location']['lat'])
            station_lngs.append(tmp_loc['location']['lng'])
            
        print(f"🔥💧자치구 리스트: {station_addrs}")
        gu_names = []
        for addr in station_addrs:
            tmp = addr.split()
            tmp_gu = [gu for gu in tmp if gu[-1] == '구'][0]
            gu_names.append(tmp_gu)
        [print(f"🔥💧자치구 리스트 2: {gu_names}")]
        crime['자치구'] = gu_names

        # 구 와 경찰서의 위치가 다른 경우 수작업
        crime.loc[crime['관서명'] == '혜화서', ['자치구']] == '종로구'
        crime.loc[crime['관서명'] == '서부서', ['자치구']] == '은평구'
        crime.loc[crime['관서명'] == '강서서', ['자치구']] == '양천구'
        crime.loc[crime['관서명'] == '종암서', ['자치구']] == '성북구'
        crime.loc[crime['관서명'] == '방배서', ['자치구']] == '서초구'
        crime.loc[crime['관서명'] == '수서서', ['자치구']] == '강남구'
        
        crime.to_csv(os.path.join(self.stored_data, 'crime_in_seoul.csv'), index=False)
        this.crime = crime
        return this
    
    def update_police(self, this) -> object:
        print(f"------------ update_police 실행 ------------")
        crime = this.crime
        crime = crime.groupby("자치구").sum().reset_index()
        crime = crime.drop(columns=["관서명"])

        police = pd.pivot_table(crime, index='자치구', aggfunc=np.sum).reset_index()
        
        police['살인검거율'] = (police['살인 검거'].astype(int) / police['살인 발생'].astype(int)) * 100
        police['강도검거율'] = (police['강도 검거'].astype(int) / police['강도 발생'].astype(int)) * 100
        police['강간검거율'] = (police['강간 검거'].astype(int) / police['강간 발생'].astype(int)) * 100
        police['절도검거율'] = (police['절도 검거'].astype(int) / police['절도 발생'].astype(int)) * 100
        police['폭력검거율'] = (police['폭력 검거'].astype(int) / police['폭력 발생'].astype(int)) * 100
        
        police = police.drop(columns={'살인 검거', '강도 검거', '강간 검거', '절도 검거', '폭력 검거'}, axis=1)
        police.to_csv(os.path.join(self.stored_data, 'police_in_seoul.csv'), index=False)

        # 검거율이 100%가 넘는 경우 처리
        for column in self.crime_rate_columns:
            police.loc[police[column] > 100, column] = 100

        police = police.rename(columns={
            '살인 발생': '살인',
            '강도 발생': '강도',
            '강간 발생': '강간',
            '절도 발생': '절도',
            '폭력 발생': '폭력'
        })

        # 정규화 처리
        x = police[self.crime_rate_columns].values
        min_max_scalar = preprocessing.MinMaxScaler()
        x_scaled = min_max_scalar.fit_transform(x.astype(float))
        
        police_norm = pd.DataFrame(x_scaled, columns=self.crime_columns, index=police.index)
        police_norm[self.crime_rate_columns] = police[self.crime_rate_columns]
        police_norm['범죄'] = np.sum(police_norm[self.crime_rate_columns], axis=1)
        police_norm['검거'] = np.sum(police_norm[self.crime_columns], axis=1)
        police_norm.to_csv(os.path.join(self.stored_data, 'police_norm_in_seoul.csv'))

        this.police = police
        return this
    
    def update_pop(self, this) -> object:
        print(f"------------ update_pop 실행 ------------")
        pop = this.pop
        pop = pop.rename(columns={
            pop.columns[0]: '자치구',
            pop.columns[1]: '인구수',
            pop.columns[2]: '한국인',
            pop.columns[3]: '외국인',
            pop.columns[4]: '고령자'
        })
        
        pop.to_csv(os.path.join(self.stored_data, 'pop_in_seoul.csv'), index=False)
        pop.drop([26], inplace=True)
        
        pop['외국인비율'] = pop['외국인'].astype(int) / pop['인구수'].astype(int) * 100
        pop['고령자비율'] = pop['고령자'].astype(int) / pop['인구수'].astype(int) * 100

        # CCTV와 인구 데이터 결합 및 상관관계 분석
        cctv_pop = pd.merge(this.cctv, pop, on='자치구')
        cor1 = np.corrcoef(cctv_pop['고령자비율'], cctv_pop['소계'])
        cor2 = np.corrcoef(cctv_pop['외국인비율'], cctv_pop['소계'])
        print(f'고령자비율과 CCTV의 상관계수 {str(cor1)} \n'
              f'외국인비율과 CCTV의 상관계수 {str(cor2)} ')
        
        """
         고령자비율과 CCTV 의 상관계수 [[ 1.         -0.28078554]
                                     [-0.28078554  1.        ]] 
         외국인비율과 CCTV 의 상관계수 [[ 1.         -0.13607433]
                                     [-0.13607433  1.        ]]
        r이 -1.0과 -0.7 사이이면, 강한 음적 선형관계,
        r이 -0.7과 -0.3 사이이면, 뚜렷한 음적 선형관계,
        r이 -0.3과 -0.1 사이이면, 약한 음적 선형관계,
        r이 -0.1과 +0.1 사이이면, 거의 무시될 수 있는 선형관계,
        r이 +0.1과 +0.3 사이이면, 약한 양적 선형관계,
        r이 +0.3과 +0.7 사이이면, 뚜렷한 양적 선형관계,
        r이 +0.7과 +1.0 사이이면, 강한 양적 선형관계
        고령자비율 과 CCTV 상관계수 [[ 1.         -0.28078554] 약한 음적 선형관계
                                    [-0.28078554  1.        ]]
        외국인비율 과 CCTV 상관계수 [[ 1.         -0.13607433] 거의 무시될 수 있는
                                    [-0.13607433  1.        ]]                        
         """

        print(f"🔥💧pop: {pop.head()}")
        return this
    

    def draw_crime_map(self) -> object:
        file = self.file
        reader = self.reader
        file.context = self.updated_data
        file.fname = 'police_norm'
        police_norm = reader.csv(file)
        file.context = self.stored_data
        file.fname = 'geo_simple'
        state_geo = reader.json(file)
        file.fname = 'crime_in_seoul'
        crime = reader.csv(file)
        file.context = self.updated_data
        file.fname = 'police_pos'
        police_pos = reader.csv(file)
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

        folium_map.save('./saved_data/crime_map.html')
        

