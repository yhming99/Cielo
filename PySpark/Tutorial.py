#### PySpark Tutorial
1. 데이터 불러오기
2. 셀렉 앤 드랍
3. 결측치 처리
4. 스트링인덱서
5. 벡터 어셈블러
6. 파이널 데이터 독립변수 종속변수
7. 선형회귀분석

!pip install pyspark
import pyspark

from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("PySpark Regression").getOrCreate()

df_pyspark = spark.read.csv('df_deal_mean.csv', header=True, inferSchema=True)

df_pyspark.na.drop() # or df_pyspark.na.fill('Missing Value')

from pyspark.ml.feature import Imputer
imputer = Imputer(
    inputCols=['price_mean', 'price_rate', 'rent_mean', 'rent_rate'],
    outputCols=['{}_imputed'.format(c) for c in ['price_mean', 'price_rate', 'rent_mean', 'rent_rate']]
).setStrategy('mean')
df_pyspark = imputer.fit(df_pyspark).transform(df_pyspark)

df_pyspark.filter(
    ~(df_pyspark['price_mean_imputed'] >= 100000) &
    (df_pyspark['price_rate_imputed'] >= 1.0)
)

from pyspark.ml.feature import StringIndexer
indexer = StringIndexer(inputCols=['price_mean_imputed', 'price_rate_imputed', 'rent_mean_imputed', 'rent_rate_imputed'],
                        outputCols=['price_mean_imputed_indexed', 'price_rate_imputed_indexed', 'rent_mean_imputed_indexed', 'rent_rate_imputed_indexed']
                        )
df_pyspark = indexer.fit(df_pyspark).transform(df_pyspark)

from pyspark.ml.feature import VectorAssembler
featureassembler = VectorAssembler(
    inputCols=['price_mean_imputed_indexed', 'price_rate_imputed_indexed', 'rent_mean_imputed_indexed', 'rent_rate_imputed_indexed'],
    outputCol='features'
)
output = featureassembler.transform(df_pyspark)

finalized_data = output.select('features', 'sell_or_not')

from pyspark.ml.regression import LinearRegression
train_data, test_data = finalized_data.randomSplit([0.8, 0.2])
regressor = LinearRegression(featuresCol='features', labelCol='sell_or_not')
regressor = regressor.fit(train_data)

# outcomes
regressor.coefficients
regressor.intercept
pred_results = regressor.evaluate(test_data)
pred_results.predictions.show()
