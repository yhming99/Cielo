#!/usr/bin/env python
# coding: utf-8

# In[1]:


from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd


def fetch_apt_sale_data(service_key, gu_code, date, n):
    """
    Fetch apartment transaction data from OpenAPI and return it as a cleaned DataFrame.

    Args:
        service_key(str) : The API key needed to access the service.
        gu_code (int) : The code of the district (구).
        date (int) : The date in the format YYYYMM.
        n (int) : The number of rows to fetch.

    Returns:
        pd.DataFrame: A DataFrame containing cleaned apartment data.
    """

    # Construct the URL
    url = f'https://apis.data.go.kr/1613000/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade?serviceKey={service_key}&'\
          f'LAWD_CD={gu_code}&'\
          f'DEAL_YMD={date}&'\
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
        deal_amount = te[i].dealamount.string.strip()
        deal_year = te[i].dealyear.string.strip()
        deal_month = te[i].dealmonth.string.strip()
        deal_day = te[i].dealday.string.strip()
        dong_name = te[i].umdnm.string.strip()
        gu_code = te[i].sggcd.string.strip()


        data = [dong_name, apt_name, apt_userArea, apt_floor, deal_amount, deal_year, deal_month, deal_day, gu_code, apt_buildYear]
        datas.append(data)

    # Create DataFrame
    df = pd.DataFrame(datas, columns = ['dong_name', 'apt_name', 'apt_userArea', 'apt_floor', 'deal_amount', 'deal_year', 'deal_month', 'deal_day', 'gu_code', 'apt_buildYear'])

    # Clean and convert data types
    df['apt_userArea'] = df['apt_userArea'].astype(float)
    df['apt_floor'] = df['apt_floor'].astype(int)
    df['apt_buildYear'] = df['apt_buildYear'].astype(int)
    df['deal_amount'] = df['deal_amount'].str.replace(',','').astype(int)
    df['deal_year'] = df['deal_year'].astype(int)
    df['deal_month'] = df['deal_month'].astype(int)
    df['deal_day'] = df['deal_day'].astype(int)
    df['gu_code'] = df['gu_code'].astype(int)

    return df

# Example usage
service_key = "sgOQlwpackhO01oaCAAcwfJy4IGwN%2F2uLcXifUcmx%2FIwLRwPkaBTgz9kBtg5oQg8YRxPZICHxtKF%2BsXKn4rf%2Fw%3D%3D"
gu_code = 11680 #강남구 코드
date = 202501 #오늘 날짜로??
n = 10000 #개수만큼나오게 하기

# Fetch data
df = fetch_apt_sale_data(service_key, gu_code, date, n)

# Print head of the DataFrame
df



# In[58]:


get_ipython().system('jupyter nbconvert --to script 매매가.ipynb')


# In[ ]:




