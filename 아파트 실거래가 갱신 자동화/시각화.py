#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
from 아파트정보 import df_deachi_location
from 매매가전월세통합 import process_real_estate_data

service_key = "sgOQlwpackhO01oaCAAcwfJy4IGwN%2F2uLcXifUcmx%2FIwLRwPkaBTgz9kBtg5oQg8YRxPZICHxtKF%2BsXKn4rf%2Fw%3D%3D"
gu_code = 11680
n = 10000
months = 12
filter_region = '대치동'

# 데이터 처리 및 결과 저장
df_combined_result = process_real_estate_data(
service_key=service_key,
gu_code=gu_code,
n=n,
months=months,
filter_region=filter_region
)

def add_coordinates(df_combined_result, df_deachi_location):
    # '좌표X'와 '좌표Y' 컬럼 기본값으로 초기화
    df_combined_result['좌표X'] = None
    df_combined_result['좌표Y'] = None

    # df_combined_result의 각 행에 대해 apt_name_area 내 apt_name 포함 여부 확인
    for i, res_row in df_combined_result.iterrows():
        for _, loc_row in df_deachi_location.iterrows():
            # 'apt_name'이 'apt_name_area'에 포함되어 있는 경우
            if loc_row['apt_name'] in res_row['apt_name_area']:
                # 해당 좌표 값을 추가
                df_combined_result.at[i, '좌표X'] = loc_row['좌표X']
                df_combined_result.at[i, '좌표Y'] = loc_row['좌표Y']
                break  # 매칭되면 더 이상 다음 apt_name을 검사하지 않음

    return df_combined_result


# 함수 사용 예시
df_combined_result = add_coordinates(df_combined_result, df_deachi_location)


# In[ ]:


import folium


def create_map_with_markers(df):
    # 중심 좌표 설정 (대치동 기준, 약간 더 오른쪽으로 이동)
    map_seoul = folium.Map(location=[37.496503, 127.056602], zoom_start=15, tiles="CartoDB Positron")

    # 아파트 이름별 데이터를 그룹화하여 정보 병합
    grouped = df.groupby('apt_name_area').agg({
        'apt_floor': list,
        'deal_amount': list,
        'deal_deposit': list,
        'deal_rent': list,
        '좌표X': 'first',
        '좌표Y': 'first'
    }).reset_index()

    # 좌표 데이터가 있는 행에 대해 Folium 마커 추가
    for _, row in grouped.iterrows():
        if row['좌표X'] and row['좌표Y']:  # 좌표가 존재하는 경우만
            # 툴팁에 표시할 정보 구성
            popup_info = f"<b>아파트명:</b> {row['apt_name_area']}<br><br>"
            for i in range(len(row['apt_floor'])):
                popup_info += (
                    f"<b>층:</b> {row['apt_floor'][i]}<br>"
                    f"<b>거래 금액:</b> {row['deal_amount'][i] if row['deal_amount'][i] is not None else 'N/A'}<br>"
                    f"<b>보증금:</b> {row['deal_deposit'][i] if row['deal_deposit'][i] is not None else 'N/A'}<br>"
                    f"<b>월세:</b> {row['deal_rent'][i] if row['deal_rent'][i] is not None else 'N/A'}<br><br>"
                )
            folium.Marker(
                location=[row['좌표Y'], row['좌표X']],  # 지도 좌표는 [위도, 경도] 순서
                popup=folium.Popup(popup_info, max_width=300),  # 팝업 정보 추가
                icon=folium.Icon(color="blue", icon="info-sign")  # 마커 아이콘 설정
            ).add_to(map_seoul)

    return map_seoul


# 지도 생성
map_with_markers = create_map_with_markers(df_combined_result)

# 지도 출력
map_with_markers


# In[ ]:


get_ipython().system('jupyter nbconvert --to script --output "시각화" 시각화.ipynb')

