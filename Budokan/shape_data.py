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
        arr = {
            'prefecture_id': data[1],  # 県id
            'ward_city_id': data[2],  # 区,市のid
            'registered_address': data[26],  # 住所(住居表示)
            'landprice': data[19],  # 地価
            'address': data[27],  # 住所(地番)
            'gross_floor_area': data[1031] / 0.3025,  # 延床面積
            'building_use_1': data[1042],  # 建物用途
            'rent_tsubo_1': (data[1047] + data[1116]) / 0.3025,  # 坪単価
            'building_use_2': data[1056],
            'rent_tsubo_2': (data[1061] + data[1116]) / 0.3025,
            'building_use_3': data[1070],
            'rent_tsubo_3': (data[1075] + data[1116]) / 0.3025,
            'building_use_4': data[1084],
            'rent_tsubo_4': (data[1089] + data[1116]) / 0.3025,
            'building_use_5': data[1098],
            'rent_tsubo_5': (data[1103] + data[1116]) / 0.3025}
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
    correct_answer = pd.concat([shaper.appraisal_report[['landprice', 'address', 'gross_floor_area', 'latitude', 'longitude', 'rent_tsubo_%d' %
                                                         i, 'building_use_%d' % i]].rename(columns={'rent_tsubo_%d' % i: 'rent_tsubo', 'building_use_%d' % i: 'building_use'}) for i in [1, 2, 3, 4, 5]])
    correct_answer = correct_answer.dropna(
        subset=['rent_tsubo']).drop_duplicates()
    return correct_answer


if __name__ == '__main__':
    correct_answer = make_intermediate_data()
    correct_answer.to_csv('intermediate/correct_answer.csv', index=False)
