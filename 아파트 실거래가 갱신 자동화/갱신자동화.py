#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from apscheduler.schedulers.blocking import BlockingScheduler

def save_df_to_html():
    import pandas as pd
    from 매매가전월세통합 import process_real_estate_data

    service_key = "sgOQlwpackhO01oaCAAcwfJy4IGwN%2F2uLcXifUcmx%2FIwLRwPkaBTgz9kBtg5oQg8YRxPZICHxtKF%2BsXKn4rf%2Fw%3D%3D"
    gu_code = 11680
    n = 10000
    months = 3
    filter_region = '대치동'

    # 데이터 처리 및 결과 저장
    df_combined_result = process_real_estate_data(
        service_key=service_key,
        gu_code=gu_code,
        n=n,
        months=months,
        filter_region=filter_region
    )

    # HTML 저장 경로
    desktop = "C:\\Users\\yoonh\\Desktop"
    output_path = f"{desktop}\\df_combined_result.html"
    df_combined_result.to_html(output_path)
    print(f"DataFrame이 {output_path}에 저장되었습니다.")


# 스케줄러 설정
scheduler = BlockingScheduler()
# 매일 06:00 (24시간 기준) 실행되도록 설정
scheduler.add_job(save_df_to_html, 'cron', hour=6, minute=0)

print("스케줄러가 시작되었습니다. 매일 06:00에 데이터가 저장됩니다.")
scheduler.start()


# In[ ]:


get_ipython().system('jupyter nbconvert --to script --output "갱신자동화" 갱신자동화.ipynb')

