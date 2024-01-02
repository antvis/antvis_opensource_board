import random
import streamlit as st
import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime, time

ownerList = ['hustcc','xiaoiver','pearmini','lzxue','Yanyan-Wang','Aarebecca','bubkoo','NewByVector','lijinke666','wjgogogo','lvisei','heiyexing']
def getUserType(name:str):
    if name in ownerList:
        return 'in'
    else:
        return 'out'
def getGitHubToken():
    random_number = random.uniform(1, 4)
    return st.secrets['GIT_HUB'+str(int(random_number))]
# 获取自指定日期以来的所有 PR
def get_prs_since(owner, repo, since_date, state='all' ):
    # 如果使用了私有仓库，请提供 GitHub Personal Access Token
    headers = {}
    token = getGitHubToken()
    if token:
        headers['Authorization'] = f"Bearer {token}"

    # GitHub API URL
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"

    # 存储 PR 的列表
    prs_since = []

    # 初始化页码
    page = 1

    flag = True

    while flag:
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
                    flag = False
            
            # 如果当前页 PR 数量小于分页数量，说明没有更多的 PR 了
            if len(prs) < 100:
                flag = False

            # 增加页码，准备获取下一页
            page += 1
        else:
            print(f"Error: {response.status_code}")
            flag = False
    data = []
    
    for pr in prs_since:
        pr_id = pr['number']
        title = pr['title']
        creator = pr['user']['login']
        created_at = pr['created_at']
        creator_type = getUserType(creator)
        data.append([pr_id, title, creator, created_at,creator_type])
    df = pd.DataFrame(data, columns=['pr_id', 'title', 'creator','created_at','creator_type'])
    df['created_at'] = pd.to_datetime(df['created_at'])

    # 添加一个新列表示年月日
    df['date'] = df['created_at'].dt.strftime('%Y-%m-%d')

    # 添加一个新列表示年月
    df['year_month'] = df['created_at'].dt.strftime('%Y-%m')
    
    return df

def get_commits_since(owner, repo, since):
    commits = []
    page = 1
    per_page = 100  # 每页的提交数，GitHub 默认最大为 100
    
    headers = {}
    token = getGitHubToken()
    if token:
        headers['Authorization'] = f"Bearer {token}"
    flag = True   
    while flag:
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
                creator = ''
    
                if(commit['author']):
                    creator = commit['author']['login']
                else:
                    creator = commit['commit']['author']['name']
                
                creator_type = getUserType(creator)
                created_at = commit['commit']['author']['date']
                commits.append([creator, created_at, creator_type])
            # 如果返回的提交数小于每页的提交数，表示已经到达最后一页
            if len(new_commits) < per_page:
                flag = False

            # 增加页数，继续下一页
            page += 1

        else:
            print(f"Failed to fetch commit information. Status code: {response.status_code}")
            flag = False
    
    df = pd.DataFrame(commits, columns=['creator', 'created_at','creator_type'])

    df['year_month'] =pd.to_datetime(df['created_at']).dt.strftime('%Y-%m')
    return df