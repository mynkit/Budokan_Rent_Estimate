#!/usr/bin/python
# -*- coding: utf-8 -*-

'''lightgbmによる学習
Examples:
    python ml.py
'''

import os
import json
import pickle
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import const


def figure_accuracy(ans: np.ndarray, pred: np.ndarray):
    '''散布図をplotする
    '''
    fig = plt.figure(figsize=(6, 6), facecolor='w')
    fig, ax = plt.subplots(1, 1, figsize=(6, 6))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(
        lambda x, loc: "{:,}".format(int(x))))
    ax.xaxis.set_major_formatter(plt.FuncFormatter(
        lambda x, loc: "{:,}".format(int(x))))
    ax.set_aspect('equal')
    ax.scatter(pred, ans, s=1)
    ax.set_xlabel("prediction")
    ax.set_ylabel("actual")
    plt.savefig('accuracy/accuracy.png')
    mer = np.median(abs(pred - ans)/ans)
    print("MER(誤差率の絶対値の中央値): {:.2f}%".format(100*mer))
    return mer


def accuracy_verification(correct_answer_data: pd.core.frame.DataFrame):
    '''精度検証
    '''
    X = np.array(correct_answer_data[const.feature_values])
    y = np.array(correct_answer_data[const.target_col])
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=1)

    lgb_train = lgb.Dataset(X_train, y_train)
    lgb_eval = lgb.Dataset(X_test, y_test, reference=lgb_train)

    lgbm_params = {
        'objective': 'regression',
        'n_estimators': 200,
        'metric': 'rmse',
    }

    model = lgb.train(lgbm_params, lgb_train, valid_sets=lgb_eval)
    with open('accuracy/model.pkl', mode='wb') as f:
        pickle.dump(model, f)

    y_pred = model.predict(X_test, num_iteration=model.best_iteration)

    mer = figure_accuracy(y_test, y_pred)

    result = {}
    result.update(lgbm_params)
    result.update({'MER': mer})
    with open('accuracy/result.json', mode='w') as f:
        json.dump(result, f, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))


if __name__ == '__main__':
    os.makedirs('intermediate', exist_ok=True)
    correct_answer_data = pd.read_csv('intermediate/correct_answer.csv')
    correct_answer_data = correct_answer_data.dropna(
        subset=const.feature_values, how='any')
    accuracy_verification(correct_answer_data)
