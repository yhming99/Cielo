#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from Portfolio.매매가 import fetch_apt_sale_data
from datetime import datetime
import pandas as pd
from dateutil.relativedelta import relativedelta
from Portfolio.전월세 import fetch_apt_rent_data

df_region_codes = pd.read_csv('region_codes.txt', sep='\t', encoding='cp949')
df_region_codes = df_region_codes[df_region_codes['폐지여부'] == '존재']
df_region_codes['분리된법정동명'] = df_region_codes['법정동명'].str.split(" ")
df_region_codes['gu'] = df_region_codes['분리된법정동명'].str[1]
df_region_codes['dong'] = df_region_codes['분리된법정동명'].str[2]
df_region_codes_seoul = df_region_codes[df_region_codes['법정동명'].str.contains('서울특별시')]
seoul_gu_list = df_region_codes_seoul['gu'].dropna().unique()

service_key = "sgOQlwpackhO01oaCAAcwfJy4IGwN%2F2uLcXifUcmx%2FIwLRwPkaBTgz9kBtg5oQg8YRxPZICHxtKF%2BsXKn4rf%2Fw%3D%3D"
months = 12
end_date = datetime.now()
dates = [(end_date - relativedelta(months=i)).strftime('%Y%m') for i in range(months)]
n = 10000


deal_mean_list = []

for gu in seoul_gu_list:
    df_filtered_gu = df_region_codes[df_region_codes['법정동명'].str.contains(gu, na=False)]
    code = df_filtered_gu['법정동코드'].astype(str).str[:5].iloc[0]

    df_combined_monthly = pd.DataFrame()
    df_combined_monthly_rent = pd.DataFrame()

    deal_mean_monthly_list = []
    rent_mean_monthly_list = []

    df_combined = pd.DataFrame()

    df_combined_rent = pd.DataFrame()

    for date in dates:
        gu_code = code
        df = fetch_apt_sale_data(service_key, gu_code, date, n)
        df_rent = fetch_apt_rent_data(service_key, gu_code, date, n)

        df_rent['rent_converted'] = df_rent['deal_deposit'] + df_rent['deal_rent'] * 100
        df_combined_rent = pd.concat([df_combined_rent, df_rent], ignore_index=True)


        df_filtered_first = df[(df['apt_userArea'] > 84) & (df['apt_userArea'] < 85)]
        df_filtered_second = df_rent[(df_rent['apt_userArea'] > 84) & (df_rent['apt_userArea'] < 85)]

        deal_mean_monthly = round(df_filtered_first['deal_amount'].mean(), -2)
        rent_mean_monthly = round(df_filtered_second['rent_converted'].mean(), -2)

        deal_mean_monthly_list.append({'gu': gu, 'deal_mean_monthly': deal_mean_monthly, 'date': date})
        rent_mean_monthly_list.append({'gu': gu, 'rent_mean_monthly': rent_mean_monthly, 'date': date})

        df_deal_mean_monthly_list = pd.DataFrame(deal_mean_monthly_list)
        df_rent_mean_monthly_list = pd.DataFrame(rent_mean_monthly_list)

        df_combined_monthly = pd.concat([df_combined_monthly, df_deal_mean_monthly_list], ignore_index=True)
        df_combined_monthly_rent = pd.concat([df_combined_monthly_rent, df_rent_mean_monthly_list], ignore_index=True)

        df_combined = pd.concat([df_combined, df], ignore_index=True)

    price_rate = round(df_deal_mean_monthly_list['deal_mean_monthly'][0] / df_deal_mean_monthly_list['deal_mean_monthly'][months - 1], 2)
    rent_rate = round(df_rent_mean_monthly_list['rent_mean_monthly'][0] / df_rent_mean_monthly_list['rent_mean_monthly'][months - 1], 2)

    df_filtered = df_combined[(df_combined['apt_userArea'] > 84) & (df_combined['apt_userArea'] < 85)]
    deal_mean = round(df_filtered['deal_amount'].mean(), -2)

    df_filtered_rent = df_combined_rent[(df_combined_rent['apt_userArea'] > 84) & (df_combined_rent['apt_userArea'] < 85)]
    rent_mean = round(df_filtered_rent['rent_converted'].mean(), -2)


    deal_mean_list.append({"구": gu, "평균 가격": deal_mean, "price_rate" : price_rate, "rent_mean" : rent_mean, "rent_rate" : rent_rate})

df_deal_mean = pd.DataFrame(deal_mean_list)


# In[ ]:


df_deal_mean


# In[ ]:


def cal_cost_buy(gu, deal_mean, holding_year, loan_rate, value_rate):

    price_buy = deal_mean
    region = gu
    # 대출금 산정
    if region in ['강남구', '서초구', '송파구', '용산구']:
        ltv = 0.5
    else:
        ltv = 0.7

    loan = price_buy * ltv
    cash = price_buy * (1 - ltv)
    loan_annual = loan * loan_rate
    loan_annual_total = loan_annual * holding_year

    # 중개수수료 산정
    if  price_buy < 90000:
        fee_rate = 0.004
    elif price_buy < 120000:
        fee_rate = 0.005
    elif price_buy < 150000:
        fee_rate = 0.006
    else:
        fee_rate = 0.007

    fee = price_buy * fee_rate

    # 취득세 산정 (농어촌특별세 85m2 미만 서민주택 비과세 (취득가액의 0.2%)), (지방교육세 = 취득세의 10%)
    if price_buy <= 60000:
        acquisition_tax_rate = 0.01
    elif price_buy <= 90000:
        acquisition_tax_rate = 0.02
    else:
        acquisition_tax_rate = 0.03

    acquisition_tax = price_buy * acquisition_tax_rate
    eud_tax = acquisition_tax * 0.1
    acquisition_tax_total = acquisition_tax + eud_tax

    # 재산세 산정
    # 공시가격 및 과세표준(공시가격 * 공정시장가액) 계산
    price_buy_public = price_buy * 0.8
    if price_buy_public <= 30000:
        tax_base_price = price_buy_public * 0.43
    elif price_buy_public <= 60000:
        tax_base_price = price_buy_public * 0.44
    elif price_buy_public <= 90000:
        tax_base_price = price_buy_public * 0.45
    else:
        tax_base_price = price_buy_public * 0.6

     # 1주택자 공시가격 9억 이하 특례세율
    if price_buy_public <= 90000:
        if tax_base_price <= 6000:
            property_tax_rate = 0.0005
            property_tax = tax_base_price * property_tax_rate
        elif tax_base_price <= 15000:
            property_tax_rate = 0.001
            property_tax = 3 + (tax_base_price - 6000) * property_tax_rate
        elif tax_base_price <= 30000:
            property_tax_rate = 0.002
            property_tax = 12 + (tax_base_price - 15000) * property_tax_rate
        else:
            property_tax_rate = 0.0035
            property_tax = 42 + (tax_base_price - 30000) * property_tax_rate
    else:
        if tax_base_price <= 6000:
            property_tax_rate = 0.001
            property_tax = tax_base_price * property_tax_rate
        elif tax_base_price <= 15000:
            property_tax_rate = 0.002
            property_tax = 6 + (tax_base_price - 6000) * property_tax_rate
        elif tax_base_price <= 30000:
            property_tax_rate = 0.003
            property_tax = 19.5 + (tax_base_price - 15000) * property_tax_rate
        else:
            property_tax_rate = 0.004
            property_tax = 57 + (tax_base_price - 30000) * property_tax_rate
    # 지방교육세 재산세 * 20%
    property_tax_edu = property_tax * 0.2
    property_tax_total = (property_tax + property_tax_edu) * holding_year

    # 종합부동산세 산정
    if price_buy_public <= 120000:
        tax_complex = 0
    else:
        if tax_base_price < 30000:
            tax_complex_rate = 0.005
            tax_complex = tax_base_price * tax_complex_rate
        elif tax_base_price < 60000:
            tax_complex_rate = 0.007
            tax_complex = tax_base_price * tax_complex_rate - 60
        elif tax_base_price < 120000:
            tax_complex_rate = 0.01
            tax_complex = tax_base_price * tax_complex_rate - 240
        elif tax_base_price < 250000:
            tax_complex_rate = 0.013
            tax_complex = tax_base_price * tax_complex_rate - 600
        elif tax_base_price < 500000:
            tax_complex_rate = 0.015
            tax_complex = tax_base_price * tax_complex_rate - 1100
        elif tax_base_price < 940000:
            tax_complex_rate = 0.02
            tax_complex = tax_base_price * tax_complex_rate - 3600
        else:
            tax_complex_rate = 0.027
            tax_complex = tax_base_price * tax_complex_rate - 10180

    tax_complex_total = tax_complex * holding_year

    # 양도차익 산정
    price_sell = price_buy * (1 + value_rate)**holding_year
    capital_gain = price_sell - price_buy
    capital_gain_base = capital_gain * max((price_sell - 120000), 0) // price_sell

    if price_sell <= 120000:
        profit = 0
    else:
        if holding_year == 2:
            profit = capital_gain_base * (1 - 0.08)
        elif holding_year == 3:
            profit = capital_gain_base * (1 - 0.24)
        elif holding_year == 4:
            profit = capital_gain_base * (1 - 0.32)
        elif holding_year == 5:
            profit = capital_gain_base * (1 - 0.40)
        elif holding_year == 6:
            profit = capital_gain_base * (1 - 0.48)
        elif holding_year == 7:
            profit = capital_gain_base * (1 - 0.56)
        elif holding_year == 8:
            profit = capital_gain_base * (1 - 0.64)
        elif holding_year == 9:
            profit = capital_gain_base * (1 - 0.72)
        else:
            profit = capital_gain_base * (1 - 0.80)

    basic_income_deduction = 250
    profit_base_tax = max(profit - basic_income_deduction,0) #기본소득공제

    if profit_base_tax <= 1400:
        profit_base_tax_rate = 0.06
        profit_base_tax_total = profit_base_tax * profit_base_tax_rate
    elif profit_base_tax <= 5000:
        profit_base_tax_rate = 0.15
        profit_base_tax_total = profit_base_tax * profit_base_tax_rate - 126
    elif profit_base_tax <= 8800:
        profit_base_tax_rate = 0.24
        profit_base_tax_total = profit_base_tax * profit_base_tax_rate - 576
    elif profit_base_tax <= 15000:
        profit_base_tax_rate = 0.35
        profit_base_tax_total = profit_base_tax * profit_base_tax_rate - 1544
    elif profit_base_tax <= 30000:
        profit_base_tax_rate = 0.38
        profit_base_tax_total = profit_base_tax * profit_base_tax_rate - 1994
    elif profit_base_tax <= 50000:
        profit_base_tax_rate = 0.40
        profit_base_tax_total = profit_base_tax * profit_base_tax_rate - 2594
    elif profit_base_tax <= 100000:
        profit_base_tax_rate = 0.42
        profit_base_tax_total = profit_base_tax * profit_base_tax_rate - 3594
    else:
        profit_base_tax_rate = 0.45
        profit_base_tax_total = profit_base_tax * profit_base_tax_rate - 6594
    # 지방소득세 양도소득세의 10%
    local_income_tax = profit_base_tax_total * 0.1
    profit_base_tax_total_final = profit_base_tax_total + local_income_tax

    total_cost_buy = cash + loan_annual_total + fee + acquisition_tax_total + property_tax_total + tax_complex_total + profit_base_tax_total_final

    price_gap = price_sell - deal_mean
    cost = loan_annual_total + fee + acquisition_tax_total + property_tax_total + tax_complex_total + profit_base_tax_total_final
    tax_fee = fee + acquisition_tax_total + property_tax_total + tax_complex_total + profit_base_tax_total_final
    total_profit = price_gap - cost
    return_on_investment = total_profit / (cash + cost)
    profit_rate = price_gap / cost

    return round(price_sell, 0), round(price_gap, 0), round(cost, 0), round(total_profit, 0), round(profit_rate, 2), round(cash, 0), round(return_on_investment, 2), round(loan, 0), ltv, round(loan_annual_total, 0), round(tax_fee, 0), round(total_cost_buy, 0)
    # price_sell, price_gap, cost, total_profit, profit_rate, cash, return_on_investment, loan, ltv, loan_annual_total, tax_fee, total_cost_buy,

    # 자기 자본 수익률
    # 10억짜리 아파트를 5억 현금 5억 대출로 샀다.
    # 15억에 팔았다. 5억 양도차익이다.
    # 대출이자, 세금, 수수료 포함 총 비용 3억이 들어서 순수익 2억이다.   순수익 = 양도차익 - 대출이자, 세금, 수수료다. 순수익 = price_gap - cost다.
    # 자기자본수익률은 순수익 2억 / 현금 5억이다. 40%
    # 순수익 2억 / 현금 5억과 비용 3억 총 8억  25%의 투자수익률을 나타낸다.

    # 갭투자 자기 자본 수익률
    # 10억짜리 아파트를 5억 현금 5억 전세로 샀다.
    # 15억에 팔았다. 5억 양도차익이다.
    # 전세를 꼇기에 대출이자 없이, 세금, 수수료 포함 총 비용 2억이 들어서 순수익 3억이다.   순수익 = 양도차익 - 세금, 수수료다. 순수익 = price_gap - tax_fee다.
    # 자기자본수익률은 순수익 3억 / 현금 5억이다. 60%

"""
    def won(i):
        eok = int(i // 10000)
        cheon = int((i % 10000) // 1000)
        baek = int((i % 1000) // 100)
        #ship = int((i % 100) // 10)

        result = []
        if eok > 0:
            result.append(f"{eok}억")
        if cheon > 0:
            result.append(f"{cheon}천")
        if baek > 0:
            result.append(f"{baek}백만원")
        #if ship > 0:
        #    result.append(f"{ship}십만원")
        return " ".join(result)

    return print(
                 f'1세대 1주택자 가정\n'
                 f'거주 및 보유기간: {holding_year}년\n'
                 f'부동산 가치 상승률: {value_rate*100}%\n'
                 f'주택담보대출 이율: {loan_rate*100}%\n'
                 f'조정대상지역 및 투기과열지구: 강남구, 서초구, 송파구, 용산구\n'

                 f'{region} 직전 3개월 국민평형대(85m2) 평균가격: {apt_price_mean}\n'
                 f'LTV: {ltv*100}%\n'
                 f'현금: {won(cash)}\n'
                 f'대출금: {won(loan)} ,연간대출금: {won(loan_annual)}, 총대출금액: {won(loan_annual_total)}\n'
                 f'중개수수료: {won(fee)}\n'
                 f'취득세: {won(acquisition_tax_total)}\n'
                 f'재산세: {won(property_tax_total)}\n'
                 f'종합부동산세: {won(tax_complex_total)}\n'
                 f'양도소득세: {won(profit_base_tax_total_final)}\n'
                 f'총비용: {won(total_cost_buy)}\n'
                 f'수익가액: {won(final_profit)} = 양도가액: {won(price_sell)} - 총비용: {won(total_cost_buy)}\n'
                 )
"""


# In[ ]:


holding_year = 10
loan_rate = 0.04
value_rate = 0.04  # 가치상승률

calculated_results = []

for i in range(len(deal_mean_list)):
    gu = deal_mean_list[i]['구']
    deal_mean = deal_mean_list[i]['평균 가격']
    price_rate = deal_mean_list[i]['price_rate']
    rent_mean = deal_mean_list[i]['rent_mean']
    rent_rate = deal_mean_list[i]['rent_rate']

    result = cal_cost_buy(gu, deal_mean, holding_year, loan_rate, value_rate)
    calculated_results.append({"gu": gu, "deal_mean": deal_mean, "price_rate": price_rate, "rent_mean": rent_mean, "rent_rate": rent_rate, "price_sell": result[0], "price_gap": result[1], "cost": result[2], "total_profit": result[3], "profit_rate": result[4], "cash": result[5], "return_on_investment": result[6], "loan": result[7], "ltv": result[8], "loan_annual_total": result[9], "tax_fee": result[10], "total_cost_buy": result[11]})
    # price_sell, price_gap, cost, total_profit, profit_rate, cash, return_on_investment, loan, ltv, loan_annual_total, tax_fee, total_cost_buy,
df_results = pd.DataFrame(calculated_results)

#df_results['rent_mean'] = df_deal_mean_rent['평균 보증금']
df_results['gap ratio'] = round(df_results['rent_mean'] / df_results['deal_mean'], 2)
df_results['gap_return_on_investment'] = round((df_results['price_gap'] - df_results['tax_fee']) / ((df_results['deal_mean'] * (1 - df_results['gap ratio'])) + df_results['tax_fee']), 2)
df_results['gap_total_profit'] = round((df_results['price_gap'] - df_results['tax_fee']), 2)
df_results
    # 자기 자본 수익률
    # 10억짜리 아파트를 5억 현금 5억 전세로 샀다.
    # 15억에 팔았다. 5억 양도차익이다.
    # 전세를 꼇기에 대출이자 없이, 세금, 수수료 포함 총 비용 2억이 들어서 순수익 3억이다.   순수익 = 양도차익 - 세금, 수수료다. 순수익 = price_gap - tax_fee다.
    # 자기자본수익률은 순수익 3억 / 현금 5억이다. 60%
    # 순수익 3억 / 현금 5억 + 비용 2억


# In[ ]:





# In[ ]:


# Plotting
import matplotlib.pyplot as plt
import numpy as np

# Sort data by 'return_on_equity' in descending order
df_results_sorted = df_results.sort_values(by='return_on_investment', ascending=True)

# Set font for Korean characters
plt.rcParams['font.family'] = 'Malgun Gothic'  # Use a font that supports Korean characters (e.g., Malgun Gothic on Windows)
plt.rcParams['axes.unicode_minus'] = False  # Prevent minus sign from breaking

fig, ax1 = plt.subplots(figsize=(15, 9))

# Bar Plot for deal_mean and cost stacked, and loan with price_gap stacked
bar_width = 0.4
x = np.arange(len(df_results_sorted))

bars1_deal = ax1.bar(x - bar_width/2, df_results_sorted['deal_mean'], bar_width, label='Deal Mean', color='skyblue')
bars1_cost = ax1.bar(x - bar_width/2, df_results_sorted['cost'], bar_width, bottom=df_results_sorted['deal_mean'], label='Cost', color='orange')
bars2_loan = ax1.bar(x + bar_width/2, df_results_sorted['loan'], bar_width, label='Loan', color='lightgreen')
bars2_gap = ax1.bar(x + bar_width/2, df_results_sorted['total_profit'], bar_width, bottom=df_results_sorted['loan'], label='Total Profit', color='pink')

ax1.set_xlabel('GU (District)', fontsize=12)
ax1.set_ylabel('Deal Mean, Cost (Stacked) and Loan + Total Profit (Stacked)', fontsize=12)
ax1.set_xticks(x)
ax1.set_xticklabels(df_results_sorted['gu'], rotation=45, ha='right')
ax1.tick_params(axis='y', labelcolor='blue')

# Twin axis for the return_on_equity scatter plot
ax2 = ax1.twinx()
points = ax2.scatter(x, df_results_sorted['return_on_investment'], label='Return On Investment', color='red', marker='o')
ax2.set_ylabel('Return On Investment', fontsize=12)
ax2.tick_params(axis='y', labelcolor='red')

# Add grid lines for x-axis
ax1.grid(axis='x', linestyle='--', alpha=0.7)

# Improve the layout and add legends
fig.tight_layout()
ax1.legend(loc='upper left', fontsize=10)
ax2.legend(loc='upper right', fontsize=10)
plt.title('Deal Mean + Cost (Stacked) and Loan + Total Profit (Stacked, Bar) with Return On Investment (Scatter)', fontsize=14)
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.show()


# In[ ]:


# Plotting
import matplotlib.pyplot as plt
import numpy as np

# Sort data by 'gap_profit_rate_equity' in descending order
df_results_sorted = df_results.sort_values(by='gap_return_on_investment', ascending=True)

# Set font for Korean characters
plt.rcParams['font.family'] = 'Malgun Gothic'  # Use a font that supports Korean characters (e.g., Malgun Gothic on Windows)
plt.rcParams['axes.unicode_minus'] = False  # Prevent minus sign from breaking

fig, ax1 = plt.subplots(figsize=(15, 9))

# Bar Plot for deal_mean and tax_fee stacked, and rent_mean with price_gap stacked
bar_width = 0.4
x = np.arange(len(df_results_sorted))

bars1_deal = ax1.bar(x - bar_width/2, df_results_sorted['deal_mean'], bar_width, label='Deal Mean', color='skyblue')
bars1_tax = ax1.bar(x - bar_width/2, df_results_sorted['tax_fee'], bar_width, bottom=df_results_sorted['deal_mean'], label='Tax Fee', color='orange')
bars2_rent = ax1.bar(x + bar_width/2, df_results_sorted['rent_mean'], bar_width, label='Rent Mean', color='lightgreen')
bars2_gap = ax1.bar(x + bar_width/2, df_results_sorted['gap_total_profit'], bar_width, bottom=df_results_sorted['rent_mean'], label='Gap Total Profit', color='pink')

ax1.set_xlabel('GU (District)', fontsize=12)
ax1.set_ylabel('Deal Mean, Tax Fee (Stacked) and Rent Mean + Gap Total Profit (Stacked)', fontsize=12)
ax1.set_xticks(x)
ax1.set_xticklabels(df_results_sorted['gu'], rotation=45, ha='right')
ax1.tick_params(axis='y', labelcolor='blue')

# Twin axis for the gap_profit_rate_equity scatter plot
ax2 = ax1.twinx()
points = ax2.scatter(x, df_results_sorted['gap_return_on_investment'], label='Gap Return On Investment', color='red', marker='o')
ax2.set_ylabel('Gap Return On Investment', fontsize=12)
ax2.tick_params(axis='y', labelcolor='red')

# Add grid lines for x-axis
ax1.grid(axis='x', linestyle='--', alpha=0.7)

# Improve the layout and add legends
fig.tight_layout()
ax1.legend(loc='upper left', fontsize=10)
ax2.legend(loc='upper right', fontsize=10)
plt.title('Deal Mean + Tax Fee (Stacked) and Rent Mean + Gap Total Profit (Stacked, Bar) with Gap Return On Investment (Scatter)', fontsize=14)
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.show()


# In[ ]:


get_ipython().system('jupyter nbconvert --to script --output "서울시매매가전세가갭투자" 서울시매매가전세가갭투자.ipynb')

