import os
import sys
project_root = os.path.abspath('../utils/common')
sys.path.append(project_root)
from utils import getUserType,getGitHubToken
import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime, time
from streamlit_g2 import g2

ownerList = ['hustcc','xiaoiver','pearmini','lzxue','Yanyan','Aarebecca','bubkoo','NewByVector','lijinke666','wjgogogo','lvisei','heiyexing']

def get_prs_since(owner, repo, since_date, state='all', token=None):
    # 如果使用了私有仓库，请提供 GitHub Personal Access Token
    headers = {}
    if token:
        headers['Authorization'] = f"Bearer {token}"

    # GitHub API URL
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"

    # 存储 PR 的列表
    prs_since = []

    # 初始化页码
    page = 1


    while True:
        # 发送 GET 请求，使用分页参数和起始日期
        response = requests.get(url,  headers=headers, params={'page': page, 'state':state, 'per_page': 100, 'since': since_date})

        # 检查响应状态码
        if response.status_code == 200:
            # 解析 JSON 响应
            prs = response.json()

            # 将当前页的 PR 添加到列表
            for pr in prs:
                    created_at_str = pr['created_at']
                    created_at = datetime.strptime(created_at_str, '%Y-%m-%dT%H:%M:%SZ')

                    if created_at >= since_date:
                        prs_since.append(pr)
                    else:
                        # 如果创建时间早于指定时间，停止查询
                        return prs_since

            # 如果当前页 PR 数量小于分页数量，说明没有更多的 PR 了
            if len(prs) < 100:
                break

            # 增加页码，准备获取下一页
            page += 1
        else:
            print(f"Error: {response.status_code}")
            return None

    return prs_since
st.set_page_config(page_title="pull-requests", page_icon="📈", layout="wide")
# 创建两列
col1, col2 = st.columns(2)

# 替换为你的 GitHub 仓库信息
owner = "antvis"

# 在第一列中创建一个下拉框
selected_repo = col1.selectbox("选择仓库", ["G2", "G6", "L7","S2","X6"])

# 在第二列中创建一个时间选择器
selected_date2 = col2.date_input("选择开始时间",  datetime.combine(datetime(2023, 7, 1).date(), time()))

selected_date  = datetime(selected_date2.year, selected_date2.month, selected_date2.day)

# api_token = st.secrets["GIT_HUB"]


# 获取自指定日期以来的所有 PR
prs_since = get_prs_since(owner, selected_repo,  selected_date, token=getGitHubToken())

data = []
if prs_since:
    for pr in prs_since:
        pr_id = pr['number']
        title = pr['title']
        creator = pr['user']['login']
        created_at = pr['created_at']
        creator_type = 'in'  if getUserType(creator) else 'out'
        # changed_files = pr['changed_files']

        data.append([pr_id, title, creator, created_at,creator_type])


# 创建 DataFrame 存储 PR 数据
df = pd.DataFrame(data, columns=['pr_id', 'title', 'creator','created_at','creator_type'])

# 将 created_at 列的字符串表示转换为 datetime 对象
df['created_at'] = pd.to_datetime(df['created_at'])

# 添加一个新列表示年月日
df['date'] = df['created_at'].dt.strftime('%Y-%m-%d')

# 添加一个新列表示年月
df['year_month'] = df['created_at'].dt.strftime('%Y-%m')


# 按月份聚合 PR 数据
aggregated_data = df.groupby('year_month').size().reset_index(name='count')


st.markdown('### 月度 PR 数')

options = {
    "autoFit": True,
    "type": "interval",
    "data": json.loads(aggregated_data.to_json(orient='records')),
    "encode": {
        "x": "year_month",
        "y": "count",
    }
}
g2(options=options)


# 按照年月和创建者聚合 PR 数据
aggregated_creator = df.groupby(['year_month', 'creator_type']).size().reset_index(name='count')

# 计算 in 和 out 的 占比
aggregated_creator['percent'] = aggregated_creator['count'] / aggregated_creator.groupby('year_month')['count'].transform('sum') * 100
aggregated_creator['total'] = aggregated_creator.groupby('year_month')['count'].transform('sum')
# 过滤掉 creator_type == in
aggregated_creator = aggregated_creator[aggregated_creator['creator_type'] == 'out']
options2 = {
    "autoFit": True,
   
    "data": json.loads(aggregated_creator.to_json(orient='records')),
    "children": [
    {
    "type": "interval",
    "encode": {
        "x": "year_month",
        "y": "total",
        # "color": "creator_type"
    },
    "scale": {
        "x": { "padding": 0.3 }
    },
    "axis":{
        "x":{
            "title": '时间'
        }
        
    },
    "interaction": { "elementHighlight": { "background": True } },
    },
     {
      "type": "line",
      "encode": {
        "x": "year_month",
        "y": "percent",
        "color": "#EE6666",
        "shape": "smooth",
        "size": 2
      },
      "scale": {
        "y": {
          "independent": True,
          "domainMax": 100
        }
      },
      "axis": {
        "y": {
          "title": "占比(%)",
          "grid": None,
          "titleFill": "#EE6666",
           "position": "right",
           "formatter": "{value} %"
        }
      }
    }]
}
st.markdown('### 月度 PR来源分布')

g2(options=options2,key='2')

st.markdown('### 月度 PR 来源明细')

aggregated_creator_1 = df.groupby(['year_month', 'creator']).size().reset_index(name='count')



options2 = {
    "autoFit": True,
    "type": "interval",
    "data": json.loads(aggregated_creator_1.to_json(orient='records')),
    "encode": {
        "x": "year_month",
        "y": "count",
        "color": "creator"
    },
    "transform": [{ "type": "stackY" }],
    "scale": {
        "x": { "padding": 0.3 }
    },

    "interaction": { "elementHighlight": { "background": True } },
}
g2(options=options2,key='3')