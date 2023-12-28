
import requests
import os
import sys
project_root = os.path.abspath('../utils/common')
sys.path.append(project_root)
import streamlit as st
import pandas as pd
import json
from datetime import datetime, time
from streamlit_g2 import g2
from utils import getUserType,getGitHubToken

st.set_page_config(page_title="pull-requests", page_icon="🐠", layout="wide")

def get_commits_since(owner, repo, since,token =None):
    commits = []
    page = 1
    per_page = 30  # 每页的提交数，GitHub 默认最大为 100
    
    headers = {}
    if token:
        headers['Authorization'] = f"Bearer {token}"
        
    while True:
        # 构建 API 请求 URL
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"

        # 构建查询参数
        params = {'since': since, 'page': page, 'per_page': per_page}

        # 发送 GET 请求
        response = requests.get(url,  headers=headers, params=params)

        # 检查响应状态码
        if response.status_code == 200:
            # 解析 JSON 响应
            new_commits = response.json()

            # 将新的提交添加到列表
            # 打印每个提交的信息
            for commit in new_commits:
                author = ''
    
                if(commit['author']):
                    author = commit['author']['login']
                else:
                    author = commit['commit']['author']['name']
                
                author_type = getUserType(author)
                date = commit['commit']['author']['date']
                commits.append([author, date, author_type])
            # 如果返回的提交数小于每页的提交数，表示已经到达最后一页
            if len(new_commits) < per_page:
                break

            # 增加页数，继续下一页
            page += 1

        else:
            print(f"Failed to fetch commit information. Status code: {response.status_code}")
            break

    return commits

# 创建两列
col1, col2 = st.columns(2)

# 替换为你的 GitHub 仓库信息
owner = "antvis"

# 在第一列中创建一个下拉框
selected_repo = col1.selectbox("选择仓库", ["G2", "G6", "L7","S2","X6"])

# 在第二列中创建一个时间选择器
selected_date2 = col2.date_input("选择开始时间",  datetime.combine(datetime(2023, 7, 1).date(), time()))

selected_date  = datetime(selected_date2.year, selected_date2.month, selected_date2.day)

# 替换为你的 GitHub 用户名、仓库名和其他参数
owner = 'antvis'
repo = selected_repo
since = selected_date  # 如果要按日期范围获取，请提供起始日期

# 获取提交信息
data = get_commits_since(owner, repo,  since, token=getGitHubToken())
df = pd.DataFrame(data, columns=['name', 'date','author_type'])

df['year_month'] =pd.to_datetime(df['date']).dt.strftime('%Y-%m')


# 按月份聚合 PR 数据
aggregated_data = df.groupby(['year_month', 'author_type']).size().reset_index(name='count')
st.markdown('### 月度 Commit 数')

options = {
    "autoFit": True,
    "type": "interval",
    "data": json.loads(aggregated_data.to_json(orient='records')),
    "transform": [{ "type": "stackY" }],
    "encode": {
        "x": "year_month",
        "y": "count",
        "color": "author_type"
    }
}
g2(options=options)
