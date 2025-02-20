#!/usr/bin/env python
# coding: utf-8

# In[ ]:


def process_real_estate_data(service_key, gu_code, n=10000, months=3, filter_region='대치동'):
    """
    Process real estate data for sales and rent for the specified region.

    Args:
        service_key (str): Service key for API requests.
        gu_code (int): Region code for data retrieval.
        n (int): Number of records to fetch per request. Default is 10,000.
        months (int): Number of past months to fetch data for. Default is 3.
        filter_region (str): Region name to filter (e.g., '대치동'). Default is '대치동'.

    Returns:
        pd.DataFrame: Processed DataFrame combining sales and rent data.
    """
    from 매매가 import fetch_apt_sale_data
    from 전월세 import fetch_apt_rent_data
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    import pandas as pd

    # Calculate date ranges for the last 'months'
    end_date = datetime.today()
    dates = [(end_date - relativedelta(months=i)).strftime('%Y%m') for i in range(months)]

    # Initialize empty DataFrames
    df_sale_combined = pd.DataFrame()
    df_rent_combined = pd.DataFrame()

    # Fetch and concatenate sales and rental data for the given months
    for date in dates:
        df_sale = fetch_apt_sale_data(service_key, gu_code, date, n)
        df_rent = fetch_apt_rent_data(service_key, gu_code, date, n)

        df_sale_combined = pd.concat([df_sale_combined, df_sale], ignore_index=True)
        df_rent_combined = pd.concat([df_rent_combined, df_rent], ignore_index=True)

    # Filter data for the specified region
    df_sale_deachi = df_sale_combined[df_sale_combined['dong_name'].str.contains(filter_region)]
    df_rent_deachi = df_rent_combined[df_rent_combined['dong_name'].str.contains(filter_region)]

    # Create 'deal_date' column
    df_sale_deachi['deal_date'] = (
        df_sale_deachi['deal_year'].astype(str) +
        df_sale_deachi['deal_month'].astype(str).str.zfill(2) +
        df_sale_deachi['deal_day'].astype(str).str.zfill(2)
    )

    df_rent_deachi['deal_date'] = (
        df_rent_deachi['deal_year'].astype(str) +
        df_rent_deachi['deal_month'].astype(str).str.zfill(2) +
        df_rent_deachi['deal_day'].astype(str).str.zfill(2)
    )

    # Create combined apartment name and area column
    df_sale_deachi['apt_name_area'] = (
        df_sale_deachi['apt_name'] + '_' + df_sale_deachi['apt_userArea'].astype(str)
    )

    df_rent_deachi['apt_name_area'] = (
        df_rent_deachi['apt_name'] + '_' + df_rent_deachi['apt_userArea'].astype(str)
    )

    # Extract relevant columns
    df_sale_deachi = df_sale_deachi[
        ['apt_name_area', 'apt_floor', 'deal_amount', 'deal_date']
    ]
    df_rent_deachi = df_rent_deachi[
        ['apt_name_area', 'apt_floor', 'deal_deposit', 'deal_rent', 'deal_date']
    ]

    # Remove duplicates and sort by apartment name
    df_sale_deachi = df_sale_deachi.sort_values('deal_date', ascending=False).drop_duplicates(subset='apt_name_area')
    df_rent_deachi = df_rent_deachi.sort_values('deal_date', ascending=False).drop_duplicates(subset='apt_name_area')

    # Combine sales and rental data into one DataFrame
    df_combined_deachi = pd.concat([df_sale_deachi, df_rent_deachi], ignore_index=True)

    # Adjust column order and sort by apartment name
    df_combined_deachi = df_combined_deachi[
        ['apt_name_area', 'apt_floor', 'deal_amount', 'deal_deposit', 'deal_rent', 'deal_date']
    ]
    df_combined_deachi = df_combined_deachi.sort_values('apt_name_area', ascending=True)

    return df_combined_deachi

service_key = "3D"
gu_code = 11680
n = 10000
months = 3
filter_region = '대치동'

df_combined_result = process_real_estate_data(
    service_key=service_key,
    gu_code=gu_code,
    n=n,
    months=months,
    filter_region=filter_region
)

df_combined_result


# In[2]:


get_ipython().system('jupyter nbconvert --to script --output "매매가전월세통합" 매매가전월세통합.ipynb')


# In[ ]:




