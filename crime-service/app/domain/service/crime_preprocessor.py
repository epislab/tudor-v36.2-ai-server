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
from app.domain.model.file_schema import FileSchema
from app.domain.model.printer_schema import PrinterSchema

logger = logging.getLogger("crime_preprocessor")

class CrimePreprocessor:
    def __init__(self):
        self.file = FileSchema()
        self.reader = ReaderSchema()
        self.printer = PrinterSchema()
        self.crime_rate_columns = ['살인검거율', '강도검거율', '강간검거율', '절도검거율', '폭력검거율']
        self.crime_columns = ['살인', '강도', '강간', '절도', '폭력']
        current_dir = os.path.dirname(__file__)  # service directory
        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))  # app directory
        print(f"😎👩🏻‍🦰👨🏻🧔🏻‍♂️app_dir: {app_dir}")
        self.orginal_data = os.path.join(app_dir, 'original_data')
        self.derived_data = os.path.join(app_dir, 'derived_data')
        self.stored_map = os.path.join(app_dir, 'stored_map')
        self.cctv = None
        self.crime = None
        self.police = None
        self.pop = None
    
    def preprocess(self, *args) -> None:
        print(f"------------모델 전처리 시작-----------")
        for i in list(args):
            self.save_object_to_csv(i)
        
      
    
    def create_matrix(self, fname) -> pd.DataFrame:
        print(f"😎🥇🐰파일명 : {fname}")
        self.reader.fname = fname
        if fname.endswith('csv'):
            return self.reader.csv_to_dframe()
        elif fname.endswith('xls'):
            return self.reader.xls_to_dframe(header=2, usecols='B,D,G,J,N')
        return None
    
    def save_object_to_csv(self, fname) -> None:
        print(f"🌱save_csv 실행 : {fname}")
        full_name = os.path.join(self.derived_data, fname)

        if not os.path.exists(full_name) and fname == "police_positioin.csv":
            self.save_police_position()
            
        elif not os.path.exists(full_name) and fname == "cctv_pop.csv":
            self.save_cctv_pop()

        elif not os.path.exists(full_name) and fname == "police_norm.csv":
            self.save_police_norm()

        else:
            print(f"파일이 이미 존재합니다. {fname}")
    

    
    def save_police_position(self) -> None:
        print(f"------------ set_police_position 실행 ------------")
        if self.crime is not None:
            station_names = []  # 경찰서 관서명 리스트
            for name in self.crime['관서명']:
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
            print(f"🔥💧자치구 리스트 2: {gu_names}")
            self.crime['자치구'] = gu_names

            # 구 와 경찰서의 위치가 다른 경우 수작업
            self.crime.loc[self.crime['관서명'] == '혜화서', ['자치구']] = '종로구'
            self.crime.loc[self.crime['관서명'] == '서부서', ['자치구']] = '은평구'
            self.crime.loc[self.crime['관서명'] == '강서서', ['자치구']] = '양천구'
            self.crime.loc[self.crime['관서명'] == '종암서', ['자치구']] = '성북구'
            self.crime.loc[self.crime['관서명'] == '방배서', ['자치구']] = '서초구'
            self.crime.loc[self.crime['관서명'] == '수서서', ['자치구']] = '강남구'
            
            self.crime.to_csv(os.path.join(self.derived_data, 'police_positioin.csv'), index=False)
    
    def save_cctv_pop(self) -> None:
        file = self.file
        reader = self.reader
        printer = self.printer
        file.context = self.orginal_data
        file.fname = 'cctv_in_seoul'
        cctv = reader.csv_to_dframe(file)
        # p.dframe(cctv)
        file.fname = 'pop_in_seoul'

        pop = reader.xls_to_dframe(file, 2, 'B, D, G, J, N')
        # p.dframe(pop)

        cctv.rename(columns={cctv.columns[0]: '구별'}, inplace=True)

        pop.rename(columns={
            pop.columns[0]: '구별',
            pop.columns[1]: '인구수',
            pop.columns[2]: '한국인',
            pop.columns[3]: '외국인',
            pop.columns[4]: '고령자'
        }, inplace=True)
        print('*' * 20)
        print(pop.loc[20:30])
        print('*' * 20)
        pop.drop([26], inplace=True)

        pop['외국인비율'] = pop['외국인'].astype(int) / pop['인구수'].astype(int) * 100
        pop['고령자비율'] = pop['고령자'].astype(int) / pop['인구수'].astype(int) * 100

        cctv.drop(['2013년도 이전', '2014년', '2015년', '2016년'], 1, inplace=True)
        cctv_pop = pd.merge(cctv, pop, on='구별')
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
        self.cctv_pop.to_csv(os.path.join(self.derived_data, 'cctv_pop.csv'), index=False)

    def save_police_norm(self):
        file = self.file
        reader = self.reader
        printer = self.printer
        file.context = self.derived_data
        file.fname = 'police_position'
        police_positioin = reader.csv_to_dframe(file)
        police = pd.pivot_table(police_positioin, index='구별', aggfunc=np.sum)
        police['살인검거율'] = (police['살인 검거'].astype(int) / police['살인 발생'].astype(int)) * 100
        police['강도검거율'] = (police['강도 검거'].astype(int) / police['강도 발생'].astype(int)) * 100
        police['강간검거율'] = (police['강간 검거'].astype(int) / police['강간 발생'].astype(int)) * 100
        police['절도검거율'] = (police['절도 검거'].astype(int) / police['절도 발생'].astype(int)) * 100
        police['폭력검거율'] = (police['폭력 검거'].astype(int) / police['폭력 발생'].astype(int)) * 100
        police.drop(columns={'살인 검거', '강도 검거', '강간 검거', '절도 검거', '폭력 검거'}, axis=1, inplace=True)
        for i in self.crime_rate_columns:
            police.loc[police[i] > 100, 1] = 100  # 데이터값의 기간 오류로 100을 넘으면 100으로 계산
        police.rename(columns={
            '살인 발생': '살인',
            '강도 발생': '강도',
            '강간 발생': '강간',
            '절도 발생': '절도',
            '폭력 발생': '폭력'
        }, inplace=True)

        x = police[self.crime_rate_columns].values
        min_max_scalar = preprocessing.MinMaxScaler()
        """
          스케일링은 선형변환을 적용하여
          전체 자료의 분포를 평균 0, 분산 1이 되도록 만드는 과정
          """
        x_scaled = min_max_scalar.fit_transform(x.astype(float))
        """
         정규화 normalization
         많은 양의 데이터를 처리함에 있어 데이터의 범위(도메인)를 일치시키거나
         분포(스케일)를 유사하게 만드는 작업
         """
        police_norm = pd.DataFrame(x_scaled, columns=self.crime_columns, index=police.index)
        police_norm[self.crime_rate_columns] = police[self.crime_rate_columns]
        police_norm['범죄'] = np.sum(police_norm[self.crime_rate_columns], axis=1)
        police_norm['검거'] = np.sum(police_norm[self.crime_columns], axis=1)
        self.police_norm.to_csv(os.path.join(self.derived_data, 'police_norm.csv'), index=False)

    