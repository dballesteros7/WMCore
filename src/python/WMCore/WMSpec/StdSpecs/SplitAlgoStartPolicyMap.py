'''
Map between split algorithm and start policy
'''
#TODO not sure what to do with LumiBased (can't get information from DBS by block or dataset)
# Anzar will add api for Lumibased
SplitAlgoToStartPolicy = {"FileBased" : "NumberOfFiles",
                          "EventBased" : "NumberOfEvents"}

SplitAlogToArgMap = {"FileBased" : "files_per_job",
                     "EventBased" : "events_per_job"}

def getSliceType(splitAlgo):
    """
    convert split algorithm to slice type
    """
    if SplitAlgoToStartPolicy.has_key(splitAlgo):
        return SplitAlgoToStartPolicy[splitAlgo]
    else:
        return SplitAlgoToStartPolicy["FileBased"]
        
def getSliceSize(splitAlgo, splitArgs):
    """
    get slice size according to the split algorithm
    """
    
    if SplitAlgoToStartPolicy.has_key(splitAlgo):
        return splitArgs[SplitAlogToArgMap[splitAlgo]]
    else:
        return splitArgs[SplitAlogToArgMap["FileBased"]]
    