#!/usr/bin/python
# -*- coding: utf-8 -*-

'''武道館の賃料推定
Examples:
    python budokan.py
'''

import json
import pickle
import pandas as pd
import numpy as np
import const

class Estimator:
    def __init__(self):
        self.read_model()
    
    def read_model(self):
        '''ml.pyで学習したmodelを読み込む
        '''
        with open('accuracy/model.pkl', mode='rb') as f:
            self.model = pickle.load(f)

    def estimate(self, df: pd.core.frame.DataFrame) -> pd.core.frame.DataFrame:
        '''特徴量を含むデータフレームに対して賃料(坪単価)を推定する
        '''
        pred = self.model.predict(np.array(df[const.feature_values]), num_iteration=self.model.best_iteration)
        df[const.target_col] = pred
        df[const.target_col] = df[const.target_col].astype(int)
        return df

def estimate_budokan():
    '''武道館の賃料予測
    https://www.nipponbudokan.or.jp/about/gaiyou から情報を引っ張ってくる
    '''
    budokan_info = {
        'landprice': 3130000, # 最寄地価(東京都千代田区九段南２－２－５)の平均値(3120000, 3140000)
        'gross_floor_area': 21133.300 * 0.3025, # 坪単位にする
        'floors': 3, # 地上3階
        'road_width': 10, # GoogleMapsみた感じ10mくらいっぽかった
        'nearest_station_distance': 5 * 80, # 徒歩5分 * 80m/分
        'lot_coverage': 100 * 8132.240 / 12625.000, # 建築面積/敷地面積
        'office': 1, # オフィス物件と仮定
        'retail': 0,
        'residential': 0,
        'hotel': 0,
        'industrial': 0,
    }
    estimator = Estimator()
    budokan = estimator.estimate(pd.io.json.json_normalize(budokan_info))
    budokan_dic = budokan.to_dict(orient='list')
    budokan_result = {k: budokan_dic[k][0] for k in budokan_dic.keys()}
    print('武道館の月額賃料: %d円/坪' % budokan_result['rent_tsubo'])
    with open('result/budokan_rent_tsubo.json', mode='w') as f:
        json.dump(budokan_result, f, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
    return budokan_result

if __name__ == '__main__':
    estimate_budokan()

    
