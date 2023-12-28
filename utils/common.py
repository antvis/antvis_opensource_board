import random
from streamlit import st

ownerList = ['hustcc','xiaoiver','pearmini','lzxue','Yanyan','Aarebecca','bubkoo','NewByVector','lijinke666','wjgogogo']
def getUserType(name:str):
    if name in ownerList:
        return 'in'
    else:
        return 'out'
def getGitHubToken():
    random_number = random.uniform(1, 4)
    return st.secrets['GIT_HUB'+str(int(random_number))]