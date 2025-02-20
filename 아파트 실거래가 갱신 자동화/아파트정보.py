#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd

#파일 불러오기
df = pd.read_csv("apt_info_seoul.csv", encoding = "euc-kr")
df_deachi = df[df['주소(읍면동)'].str.contains('대치동')]
df_deachi = df_deachi.sort_values(by = ['k-아파트명'], ascending = True)
df_deachi_location = df_deachi.set_index('k-아파트명')[['좌표X', '좌표Y']]
df_deachi_location = df_deachi_location.reset_index(names='apt_name')

#두 행 카피 후 붙이기
df_copied_rows = df_deachi_location.iloc[[0, 9]].copy()
df_copied_rows['apt_name'] = ['개포우성1', '선경1차']
df_deachi_location = pd.concat([df_deachi_location, df_copied_rows], ignore_index=True)

#이름 변경 후 이름순 정렬
df_deachi_location['apt_name'] = ['개포우성2', '대치1차현대아파트', '대치SK VIEW', '대치대우아이빌4차', '대치동부센트레빌', '대치롯데캐슬아파트', '대치르엘', '대치미도맨션', '대치삼성', '선경2차', '대치쌍용2차', '대치아이파크', '대치우성1차아파트', '대치포스코더샵', '대치푸르지오써밋', '대치현대', '대치효성', '래미안 대치 팰리스', '래미안대치하이스턴', '롯데캐슬리베아파트', '선경301(대치동)', '쌍용대치1차', '은마', '테헤란로대우아이빌', '개포우성1', '선경1차']
df_deachi_location = df_deachi_location.sort_values(by='apt_name').reset_index(drop=True)

#전체 이름 변경 후 재정렬
df_deachi_location['apt_name'] = ['개포우성1', '개포우성2','현대1','대치SKVIEW','대우아이빌명문가','동부센트레빌','롯데캐슬','대치르엘','한보미도맨션','대치삼성','선경1차','선경2차','쌍용대치2','대치아이파크','대치우성아파트','포스코더샵','대치푸르지오써밋','대치현대','대치효성','래미안대치팰리스','래미안대치하이스턴','롯데캐슬리베','선경3차','쌍용대치아파트','은마','테헤란로대우아이빌']
df_deachi_location = df_deachi_location.sort_values(by='apt_name').reset_index(drop=True)

df_deachi_location


# In[2]:


get_ipython().system('jupyter nbconvert --to script --output "아파트정보" 서울시공동주택아파트정보.ipynb')


# In[ ]:




