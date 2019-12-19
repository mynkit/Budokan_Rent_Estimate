# 武道館の賃料推定

## Required

`Budokan/learning_data/`に[鑑定評価書データ](https://www.land.mlit.go.jp/landPrice/CSVDownloadServlet)の東京分データ(`2019_TAKUCHI_k_13.csv`)を格納する

## Usage

```shell
docker-compose up -d --build # コンテナ立ち上げる
docker-compose exec budokan bash # コンテナにログイン

python shape_data.py # 鑑定評価書情報のデータ成形
python ml.py # 交差検証 + model&精度の保存
python budokan.py # 武道館に対して推定
```

## Result

### 交差検証結果

MER (誤差率の絶対値の中央値): [3.71%](https://github.com/mynkit/Budokan_Rent_Estimate/blob/master/Budokan/accuracy/result.json)
![交差検証結果](https://github.com/mynkit/Budokan_Rent_Estimate/blob/master/Budokan/accuracy/accuracy.png)

### 武道館の月額賃料(推定値)

[22006円/坪](https://github.com/mynkit/Budokan_Rent_Estimate/blob/master/Budokan/result/budokan_rent_tsubo.json)

#### 武道館をオフィスにした場合の最大年間収入

```sh
max ( 賃料(円/坪/月) * 賃貸可能面積(坪) * 稼働率 * 12ヶ月 )
= 賃料 * 延床面積 * 1.0 * 12
= 22006 * (21133.300 * 0.3025) * 12
= 1,688,165,621 円 ( 約17億円 )
```