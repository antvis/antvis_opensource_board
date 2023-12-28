import streamlit as st
import os
import sys
project_root = os.path.abspath('../utils/common')
sys.path.append(project_root)
from utils import getUserType,getGitHubToken
st.set_page_config(page_title="pull-requests", page_icon="🐲", layout="wide")

st.markdown('### 月度 PR')
st.markdown('### 月度 commit')
st.markdown('### 月度 issue')
st.markdown('### 月度 star')