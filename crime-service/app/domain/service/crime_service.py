import numpy as np
import pandas as pd
import os
from app.domain.model.reader_schema import ReaderSchema
from sklearn import preprocessing
from xarray import Dataset
from app.domain.model.google_map_schema import GoogleMapSchema

class CrimeService:
    def __init__(self):
        self.dataset = Dataset()
        self.reader = ReaderSchema()
        self.crime_rate_columns = ['살인검거율', '강도검거율', '강간검거율', '절도검거율', '폭력검거율']
        self.crime_columns = ['살인', '강도', '강간', '절도', '폭력']
        self.save_dir = 'C:\\Users\\pakjk\\Documents\\Tudor\\2501\\tudor\\v36.2\\ai-server\\crime-service\\app\\stored_data'
    
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
        full_name = os.path.join(self.save_dir, fname)

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
        cctv.to_csv(os.path.join(self.save_dir, 'cctv_in_seoul.csv'), index=False)
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
        
        crime.to_csv(os.path.join(self.save_dir, 'crime_in_seoul.csv'), index=False)
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
        police.to_csv(os.path.join(self.save_dir, 'police_in_seoul.csv'), index=False)

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
        police_norm.to_csv(os.path.join(self.save_dir, 'police_norm_in_seoul.csv'))

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
        
        pop.to_csv(os.path.join(self.save_dir, 'pop_in_seoul.csv'), index=False)
        pop.drop([26], inplace=True)
        
        pop['외국인비율'] = pop['외국인'].astype(int) / pop['인구수'].astype(int) * 100
        pop['고령자비율'] = pop['고령자'].astype(int) / pop['인구수'].astype(int) * 100

        # CCTV와 인구 데이터 결합 및 상관관계 분석
        cctv_pop = pd.merge(this.cctv, pop, on='자치구')
        cor1 = np.corrcoef(cctv_pop['고령자비율'], cctv_pop['소계'])
        cor2 = np.corrcoef(cctv_pop['외국인비율'], cctv_pop['소계'])
        print(f'고령자비율과 CCTV의 상관계수 {str(cor1)} \n'
              f'외국인비율과 CCTV의 상관계수 {str(cor2)} ')

        print(f"🔥💧pop: {pop.head()}")
        return this