# 武道館の賃料推定

~ *もしも武道館が賃貸オフィス物件だったら* ~

儲かるのか，それともこれが最適解なのか

## 学習

* データセット
    * [鑑定評価書データ](https://www.land.mlit.go.jp/landPrice/CSVDownloadServlet)
* 学習モデル
    * [LightGBM](https://lightgbm.readthedocs.io/en/latest/)
    * [ハイパーパラメータ](https://github.com/mynkit/Budokan_Rent_Estimate/blob/master/Budokan/accuracy/result.json) (ほとんどいじってない)

## Result

**結論： 武道館は賃貸オフィス物件になったほうが年間3億儲かる**

### 精度検証結果

MER (誤差率の絶対値の中央値): [3.71%](https://github.com/mynkit/Budokan_Rent_Estimate/blob/master/Budokan/accuracy/result.json)
![交差検証結果](https://github.com/mynkit/Budokan_Rent_Estimate/blob/master/Budokan/accuracy/accuracy.png)

### 武道館の月額賃料(推定値)

[22,006円/坪](https://github.com/mynkit/Budokan_Rent_Estimate/blob/master/Budokan/result/budokan_rent_tsubo.json)

#### 武道館をオフィスにした場合の最大年間収入

**約13.5億円**

```sh
max ( 賃料(円/坪/月) * 賃貸可能面積(坪) * 稼働率 * 12ヶ月 )
= 賃料 * (延床面積 * 0.8 ) * 1.0 * 12
= 22006 * (21133.300 * 0.3025 * 0.8) * 12
= 1,350,532,497 円 ( 約13.5億円 )
```

※ [estiepro](https://pro.estie.jp/)によると，`賃貸可能面積 / 延床面積`の平均値,中央値はどちらも80%台なので
```
賃貸可能面積 = 延床面積 * 0.8
```
を採用した

### 武道館2019年度の収支予算書

**約10.3億円**

[令和元年度 収支予算書](https://www.nipponbudokan.or.jp/pdf/about/R01yosan.pdf)

収支予算書によると，2019年度の事業計画では`平成31年年4月1日から令和2年3月31日`の事業収益の合計が

```
1,031,445,000 円 ( 約10.3億円 )
```

*オフィスやったほうが年間3億以上儲かる・・！*

------ 動かしたい人向け ------

## Required

`Budokan/learning_data/`に[鑑定評価書データ](https://www.land.mlit.go.jp/landPrice/CSVDownloadServlet)の東京分(`2019_TAKUCHI_k_13.csv`)を格納する

## Usage

### docker環境(推奨)

```shell
docker-compose up -d --build # コンテナ立ち上げる
docker-compose exec budokan bash # コンテナにログイン

python shape_data.py # 鑑定評価書情報のデータ成形
python ml.py # 精度検証 + model&精度の保存
python budokan.py # 武道館に対して推定
```

### local環境

```shell
cd Budokan
python shape_data.py # 鑑定評価書情報のデータ成形
python ml.py # 交差検証 + model&精度の保存
python budokan.py # 武道館に対して推定
```