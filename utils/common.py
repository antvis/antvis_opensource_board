ownerList = ['hustcc','xiaoiver','pearmini','lzxue','Yanyan','Aarebecca','bubkoo','NewByVector','lijinke666','wjgogogo']
def getUserType(name:str):
    if name in ownerList:
        return 'in'
    else:
        return 'out'