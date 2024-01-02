import os
import sys
project_root = os.path.abspath('../utils/common')
sys.path.append(project_root)
from utils import get_prs_since,get_commits_since
import streamlit as st
import pandas as pd
import json
from datetime import datetime, time
from streamlit_g2 import g2

st.set_page_config(page_title="oscp", page_icon="📈", layout="wide")
st.markdown('### AntV  OSCP 社区github活跃度报告')
# 创建两列
col1, col2 = st.columns(2)

# 替换为你的 GitHub 仓库信息
owner = "antvis"

# 在第一列中创建一个下拉框
selected_repo = col1.selectbox("选择仓库", ["G2", "G6", "L7","S2","X6"])

# 在第二列中创建一个时间选择器
selected_date2 = col2.date_input("选择开始时间",  datetime.combine(datetime(2023, 10, 1).date(), time()))

selected_date  = datetime(selected_date2.year, selected_date2.month, selected_date2.day)


# 获取自指定日期以来的所有 PR
df = get_prs_since(owner, selected_repo, selected_date)
commitDf = get_commits_since(owner, selected_repo, selected_date)


# # 按月份聚合 PR 数据
aggregated_data = df.groupby(['creator','year_month','creator_type']).size().reset_index(name='count').sort_values(by='count',ascending=False)
cm_data = commitDf.groupby(['creator','year_month','creator_type']).size().reset_index(name='count').sort_values(by='count',ascending=False)
aggregated_data['type']='pull_request'
cm_data['type']='commit'
cocat_data = pd.concat([aggregated_data,cm_data])
# 过滤 creator_type 为 in 的数据
cocat_data = cocat_data[cocat_data['creator_type'] == 'out']

#  df 按照 creator_type 聚合
creator_type_counts =df.groupby(['creator','creator_type']).size().reset_index(name='count').sort_values(by='count',ascending=False)['creator_type'].value_counts().reset_index()
creator_type_counts.columns = ['creator_type', 'count']


# 内外 PR 占比
pr_summary_df = aggregated_data.groupby('creator_type')['count'].sum().reset_index()


# # 内外 Commit 占比
cm_summary_df = cm_data.groupby('creator_type')['count'].sum().reset_index()


col1, col2 = st.columns(2)

with col1:
    col1.markdown('### 贡献者人数内外占比')

    options = {
        "type": "interval",
        "coordinate": {
            "type": "theta"
        },
        "data": json.loads(creator_type_counts.to_json(orient='records')),
         "encode": {
            "y": "count",
            "color": "creator_type"
        },
        "transform": [
            { "type": "stackY" }
        ],
        "scale":{
            "color": {
            "type": 'ordinal',
            "domain": ['in', 'out'],
            "range": ['#fc8d59','#91bfdb'],
         },
        },
        "style": {
            "radius": 4,
            "stroke": "#fff",
            "lineWidth": 1
        },
        "labels": [
            {
            "text": "count",
            "radius": 0.9
            }
        ],
        "animate": {
            "enter": {
            "type": "waveIn"
            }
        },
        "label":{
            "position": 'outside',
        },
        "axis": False,
        "legend": True,
    }

    g2(options=options,style={'height': '300px'},key=0)
    
with col2:
    col2.markdown('### 贡献者PR数内外占比')
    options = {
        "type": "interval",
        "coordinate": {
            "type": "theta"
        },
        "data": json.loads(pr_summary_df.to_json(orient='records')),
        "encode": {
            "y": "count",
            "color": "creator_type"
        },
        "transform": [
            { "type": "stackY" }
        ],
        "style": {
            "radius": 4,
            "stroke": "#fff",
            "lineWidth": 1
        },
        "labels": [
            {
            "text": "count",
            "radius": 0.9
            }
        ],
        "animate": {
            "enter": {
            "type": "waveIn"
            }
        },
        "scale":{
            'color': {
            "type": 'ordinal',
            "domain": ['in', 'out'],
            "range": ['#fc8d59','#91bfdb'],
        },
        },
        "axis": False,
        "legend": True,
    }

    g2(options=options, style={'height': '300px'},key=1)
# with col3:
#     col3.markdown('#### 贡献者 Commit 数内外占比')
#     options = {
#         "type": "interval",
#         "coordinate": {
#             "type": "theta"
#         },
#         "data": json.loads(cm_summary_df.to_json(orient='records')),
#         "encode": {
#             "y": "count",
#             "color": "creator_type"
#         },
#         "transform": [
#             { "type": "stackY" }
#         ],
#         "scale":{
#             'color': {
#             "type": 'ordinal',
#             "domain": ['in', 'out'],
#             "range": ['#fc8d59','#91bfdb'],
#         },
#         },
#         "style": {
#             "radius": 4,
#             "stroke": "#fff",
#             "lineWidth": 1
#         },
#         "labels": [
#             {
#             "text": "count",
#             "radius": 0.9
#             }
#         ],
#         "animate": {
#             "enter": {
#             "type": "waveIn"
#             }
#         },
#         "axis": False,
#         "legend": True,
#     }

#     g2(options=options, style={'height': '300'},key=3)

st.markdown('#### 月度 PR 数')

options = {
    "autoFit": True,
    "type": "interval",
    "coordinate": {
        "transform": [
        
            { "type": "transpose" }
        ]
    },

    "data": json.loads(aggregated_data.to_json(orient='records')),
    "encode": {
        "x": "creator",
        "y": "count",
        "color": "creator_type",
    }
}
g2(options=options,style={'height': '600px'})




st.markdown('#### 社区活跃度报告')

options = {
    "autoFit": True,
    "type": "interval",
    "coordinate": {
        "transform": [
        
            { "type": "transpose" }
            
        ]
    },
    # "transform": [{ "type": "stackY" }],
    "transform": [{ "type": "dodgeX" }],
    "data": json.loads(cocat_data.to_json(orient='records')),
    "encode": {
        "x": "creator",
        "y": "count",
        "color": "type",
    }
}
g2(options=options,style={'height': '800px'})


    