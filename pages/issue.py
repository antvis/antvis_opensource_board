import requests
import os
import sys
project_root = os.path.abspath('../utils/common')
sys.path.append(project_root)
from utils import getUserType,getGitHubToken
import streamlit as st
import pandas as pd
import json
from datetime import datetime, time
from streamlit_g2 import g2

def get_github_issues(repo_owner, repo_name, access_token, since_date):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
    headers = {"Authorization": f"token {access_token}"}
    params = {"since": since_date,"state":'all'}
    st.write(since_date)
    all_issues = []

    while url:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            issues = response.json()
            for issue in issues:
                issue_number = issue['number']
                issue_title = issue['title']
                created_at = issue['created_at']
                closed_at = issue['closed_at']
                creator_info = issue['user']['login']
                state: str = issue['state']

                issue_details = {
                    "number": issue_number,
                    "title": issue_title,
                    "created_at": created_at,
                    "closed_at": closed_at,
                    "state": state,
                    "creator_info": creator_info
                    
                }
                
                if created_at < since_date:
                   url = None

                all_issues.append(issue_details)
            # 如果还有下一页，更新URL
            url = response.links.get("next", {}).get("url") if "next" in response.links else None
            url = None
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None

    return all_issues
# 创建两列
col1, col2 = st.columns(2)
# 在第一列中创建一个下拉框
selected_repo = col1.selectbox("选择仓库", ["G2", "G6", "L7","S2","X6"])

# 在第二列中创建一个时间选择器
selected_date2 = col2.date_input("选择开始时间",  datetime.combine(datetime(2023, 7, 1).date(), time()))

# selected_date  = datetime(selected_date2.year, selected_date2.month, selected_date2.day)

# 替换以下信息为实际值
repo_owner = "antvis"
repo_name = selected_repo
access_token = getGitHubToken()
since_date = selected_date2.strftime('%Y-%m-%dT%H:%M:%SZ')

issues = get_github_issues(repo_owner, repo_name, access_token, since_date)



df = pd.DataFrame(issues, columns=['number', 'title', 'created_at', 'closed_at','state','creator_info'])

# 月度新建 issue 数量

df['year_month'] =pd.to_datetime(df['created_at']).dt.strftime('%Y-%m')

aggregated_data = df.groupby(['year_month','state']).size().reset_index(name='count')


options = {
    "autoFit": True,
    "type": "interval",
    "data": json.loads(aggregated_data.to_json(orient='records')),
    "transform": [{ "type": "stackY" }],
    "encode": {
        "x": "year_month",
        "y": "count",
        "color": "state"
    }
}
g2(options=options)
