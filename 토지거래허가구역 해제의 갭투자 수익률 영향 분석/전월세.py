#!/usr/bin/env python
# coding: utf-8

# In[1]:


from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd


def fetch_apt_rent_data(service_key, gu_code, date, n):
    """
    Fetch apartment rental transaction data from OpenAPI and return it as a cleaned DataFrame.

    Args:
        service_key(str) : The API key needed to access the service.
        gu_code (int) : The code of the district (구).
        date (int) : The date in the format YYYYMM.
        n (int) : The number of rows to fetch.

    Returns:
        pd.DataFrame: A DataFrame containing cleaned apartment data.
    """
    # Construct the URL
    url = f'https://apis.data.go.kr/1613000/RTMSDataSvcAptRent/getRTMSDataSvcAptRent?LAWD_CD={gu_code}&'\
        f'DEAL_YMD={date}&'\
        f'serviceKey={service_key}&'\
        f'numOfRows={n}'

    # Request data from the API
    result = urlopen(url)
    house = BeautifulSoup(result, 'lxml')
    te = house.find_all('item')

    # Parse the data
    datas = []
    for i in range(len(te)):
        apt_name = te[i].aptnm.string.strip()
        apt_userArea = te[i].excluusear.string.strip()
        apt_floor = te[i].floor.string.strip()
        apt_buildYear = te[i].buildyear.string.strip()
        deal_deposit = te[i].deposit.string.strip()
        deal_rent = te[i].monthlyrent.string.strip()
        deal_year = te[i].dealyear.string.strip()
        deal_month = te[i].dealmonth.string.strip()
        deal_day = te[i].dealday.string.strip()
        dong_name = te[i].umdnm.string.strip()
        gu_code = te[i].sggcd.string.strip()

        data = [dong_name, apt_name, apt_userArea, apt_floor, deal_deposit, deal_rent , deal_year, deal_month, deal_day, gu_code, apt_buildYear]
        datas.append(data)

    # Create DataFrame
    df = pd.DataFrame(datas, columns = ['dong_name', 'apt_name', 'apt_userArea', 'apt_floor', 'deal_deposit', 'deal_rent', 'deal_year', 'deal_month', 'deal_day', 'gu_code', 'apt_buildYear'])

    # Clean and convert data types
    df['apt_userArea'] = df['apt_userArea'].astype(float)
    df['apt_floor'] = df['apt_floor'].astype(int)
    df['apt_buildYear'] = df['apt_buildYear'].astype(int)
    df['deal_deposit'] = df['deal_deposit'].str.replace(',','').astype(int)
    df['deal_rent'] = df['deal_rent'].str.replace(',','').astype(int)
    df['deal_year'] = df['deal_year'].astype(int)
    df['deal_month'] = df['deal_month'].astype(int)
    df['deal_day'] = df['deal_day'].astype(int)
    df['gu_code'] = df['gu_code'].astype(int)

    return df

# Example usage
service_key = "sgOQlD%3D"
gu_code = 11680
date = 202501
n = 10000

# Fetch data
df = fetch_apt_rent_data(service_key, gu_code, date, n)

# Print head of the DataFrame
df


# In[13]:


get_ipython().system('jupyter nbconvert --to script 전월세.ipynb')


# In[ ]:




