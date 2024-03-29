#!/usr/bin/python
# -*- coding: utf-8 -*-

'''正解データを作る
Examples:
    python shape_data.py
'''

import pandas as pd


def add_latlon(df_: pd.core.frame.DataFrame):
    '''latitude, longitudeカラムを追加
    '''
    assert 'address' in df_.columns
    df = df_.copy()
    if not {'latitude', 'longitude'}.issubset(df.columns):
        df['latitude'] = None
        df['longitude'] = None
    address_latlon = pd.read_csv('learning_data/address_latlon.csv')
    df.index = df.address
    address_latlon.index = address_latlon.address
    df.update(address_latlon)
    return df.reset_index(drop=True)

def building_use_dummy(df_: pd.core.frame.DataFrame):
    '''building_useカラムをダミー変数に変換する
    '''
    df = df_.copy()
    df['office'] = df['building_use'].apply(lambda x: 1 if type(x) is str and '事' in x else 0)
    df['retail'] = df['building_use'].apply(lambda x: 1 if type(x) is str and '店' in x else 0)
    df['residential'] = df['building_use'].apply(lambda x: 1 if type(x) is str and ('住' in x or '居' in x) else 0)
    df['hotel'] = df['building_use'].apply(lambda x: 1 if type(x) is str and 'ホテル' in x else 0)
    df['industrial'] = df['building_use'].apply(lambda x: 1 if type(x) is str and ('工' in x or '倉' in x) else 0)
    return df

class Shaper:
    def __init__(self):
        self.read_appraisal_report_csv()
        self.read_prefecture_city_id_info()

    def read_appraisal_report_csv(self):
        '''とりあえず鑑定評価書情報の東京分のcsvを読み込む
        '''
        prefecture_ids = [13]
        self.appraisal_report_non_shape = pd.concat([pd.read_csv(
            'learning_data/2019_TAKUCHI_k_%d.csv' % prefecture_id, encoding='CP932', header=None, na_values=[0]) for prefecture_id in prefecture_ids])

    def read_prefecture_city_id_info(self):
        '''prefecture_id, city_idのinfoデータ読み込み
        '''
        self.prefecture_city_id_info = pd.read_csv(
            'learning_data/prefecture_city_id_info.csv')

    def shape_address_col(self, df_: pd.core.frame.DataFrame):
        '''addressカラムを住所全体の文字列になるように変換する
        '''
        assert {'prefecture_id', 'ward_city_id'}.issubset(df_.columns)
        df = df_.copy()
        self.prefecture_city_id_info['ward_city_id'] = [int('%d%d' % (prefecture_id, ward_city_id)) for prefecture_id, ward_city_id in zip(
            self.prefecture_city_id_info.prefecture_id.tolist(), self.prefecture_city_id_info.ward_city_id.tolist())]
        self.prefecture_city_id_info.index = self.prefecture_city_id_info.prefecture_id
        prefecture_dic = self.prefecture_city_id_info.to_dict()[
            'prefecture_name']
        self.prefecture_city_id_info.index = self.prefecture_city_id_info.ward_city_id
        ward_dic = self.prefecture_city_id_info.to_dict()['ward_city_name']

        df['ward_city_id'] = [int('%d%d' % (prefecture_id, ward_city_id)) for prefecture_id, ward_city_id in zip(
            df.prefecture_id.tolist(), df.ward_city_id.tolist())]
        df['prefecture_name'] = df['prefecture_id'].map(
            prefecture_dic)
        df['ward_city_name'] = df['ward_city_id'].map(ward_dic)
        df = df.dropna(subset=['prefecture_name', 'ward_city_name'])
        df['address'] = [prefecture_name + ward_city_name + address if address == address and address else prefecture_name + ward_city_name + registered_address for prefecture_name,
                         ward_city_name, address, registered_address in zip(df.prefecture_name.tolist(), df.ward_city_name.tolist(), df.address.tolist(), df.registered_address.tolist())]
        return df

    def shape(self):
        '''成形する
        解凍したzipにデータ仕様がxlsxファイルとして存在しているので，それと見比べながら成形
        '''
        data = self.appraisal_report_non_shape.copy()
        data.columns = [c+1 for c in data.columns] #エクセルの仕様書にカラム名を合わせる
        arr = {
            'prefecture_id': data[2],  # 県id
            'ward_city_id': data[3],  # 区,市のid
            'registered_address': data[27],  # 住所(住居表示)
            'landprice': data[20],  # 地価
            'address': data[28],  # 住所(地番)
            'floors': data[37], # 地上階数
            'basement_floors': data[38], # 地下階数
            'road_width': data[42], # 道路幅員
            'nearest_station': data[50], # 最寄駅
            'nearest_station_distance': data[51], # 最寄駅までの距離
            'lot_coverage': data[68], # 基準建ぺい率
            'gross_floor_area': data[1032] / 0.3025,  # 延床面積
            'building_use_1': data[1043],  # 建物用途
            'rent_tsubo_1': (data[1048] + data[1117]) / 0.3025,  # 坪単価
            'building_use_2': data[1057],
            'rent_tsubo_2': (data[1062] + data[1117]) / 0.3025,
            'building_use_3': data[1071],
            'rent_tsubo_3': (data[1076] + data[1117]) / 0.3025,
            'building_use_4': data[1085],
            'rent_tsubo_4': (data[1090] + data[1117]) / 0.3025,
            'building_use_5': data[1099],
            'rent_tsubo_5': (data[1104] + data[1117]) / 0.3025}
        self.appraisal_report = pd.DataFrame(arr)
        del self.appraisal_report_non_shape
        del data
        self.appraisal_report = self.shape_address_col(self.appraisal_report)
        self.appraisal_report = add_latlon(self.appraisal_report)
        self.appraisal_report = self.appraisal_report.drop(
            ['prefecture_id', 'ward_city_id', 'registered_address', 'prefecture_name', 'ward_city_name'], axis=1)


def make_intermediate_data():
    '''中間ファイル生成
    Attributes:
        correct_answer (pd.core.frame.DataFrame): 正解データ
    '''
    shaper = Shaper()
    shaper.shape()
    correct_answer = pd.concat([shaper.appraisal_report[['landprice', 'address', 'gross_floor_area', 'floors', 'road_width', 'nearest_station_distance', 'lot_coverage', 'latitude', 'longitude', 'rent_tsubo_%d' %
                                                         i, 'building_use_%d' % i]].rename(columns={'rent_tsubo_%d' % i: 'rent_tsubo', 'building_use_%d' % i: 'building_use'}) for i in [1, 2, 3, 4, 5]])
    correct_answer = correct_answer.dropna(
        subset=['rent_tsubo']).drop_duplicates()
    correct_answer = building_use_dummy(correct_answer)
    return correct_answer


if __name__ == '__main__':
    correct_answer = make_intermediate_data()
    correct_answer.to_csv('intermediate/correct_answer.csv', index=False)
