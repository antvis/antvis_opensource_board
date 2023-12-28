import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime, time
from streamlit_g2 import g2
st.set_page_config(page_title="pull-requests", page_icon="⭐", layout="wide")
def get_star_history(owner, repo,since_date, access_token):
    star_history = []
    url = f'https://api.github.com/repos/{owner}/{repo}/stargazers'
    headers = {
         "accept": "application/vnd.github.v3.star+json",
        'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    starList = response.json()
    index = 0 
    if 'last' in response.links:
        url = response.links['last']['url']
    else:
        for star in starList:
            date = star['starred_at']
            author = star['user']['login']
            star_history.append([author, date])
        url = None
    while url:
        response = requests.get(url, headers=headers)
        data = response.json()
        if 'prev' in response.links and 'url' in response.links['prev']:
            url = response.links['prev']['url']
        else:
            url = None
        for star in data:
            date = star['starred_at']
            author = star['user']['login']
            created_at = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
            if created_at >= since_date:
                star_history.append([author, date])
            else:
                url = None
    return star_history

# 创建两列
col1, col2 = st.columns(2)
# 在第一列中创建一个下拉框
selected_repo = col1.selectbox("选择仓库", ["G2", "G6", "L7","S2","X6","l7draw"])

# 在第二列中创建一个时间选择器
selected_date2 = col2.date_input("选择开始时间",  datetime.combine(datetime(2023, 7, 1).date(), time()))

selected_date  = datetime(selected_date2.year, selected_date2.month, selected_date2.day)

# 替换为你的 GitHub 用户名、仓库名和其他参数
owner = 'antvis'
repo = selected_repo

# since = selected_date  # 如果要按日期范围获取，请提供起始日期

access_token = st.secrets['GIT_HUB']

star_history = get_star_history(owner, repo, selected_date, access_token)

df = pd.DataFrame(star_history, columns=['author', 'date'])

df['year_month_day'] =pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
df['year_month'] =pd.to_datetime(df['date']).dt.strftime('%Y-%m')
df['year'] =pd.to_datetime(df['date']).dt.strftime('%Y')

# 按月份聚合 PR 数据
aggregated_year = df.groupby('year').size().reset_index(name='count')
aggregated_Month = df.groupby('year_month').size().reset_index(name='count')
aggregated_Day = df.groupby('year_month_day').size().reset_index(name='count')

aggregated_Day['Cumulative'] = aggregated_Day['count'].cumsum()
st.markdown('### 月度 Star 数')

options = {
    "autoFit": True,
    "type": "interval",
    "data": json.loads(aggregated_Month.to_json(orient='records')),
    "encode": {
        "x": "year_month",
        "y": "count",
    }
}
g2(options=options,key='month')

st.markdown('###  Star 增长曲线')

options = {
    "autoFit": True,
    "type": "line",
    "data": json.loads(aggregated_Day.to_json(orient='records')),
    "encode": {
        "x": "year_month_day",
        "y": "Cumulative",
    },
}
g2(options=options,key='increase')

