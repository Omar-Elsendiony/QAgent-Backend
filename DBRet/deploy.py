import numpy as np
from .unixcoder import UniXcoder
import torch
import os
import json
import pickle
current_dir = os.path.dirname(__file__)

clustersPathJ=os.path.join(current_dir,'clustersJ256')
centroidsPathJ=os.path.join(clustersPathJ,'centroids.pkl')
centroidsJ= pickle.load(open(os.path.join(centroidsPathJ), 'rb'))

clustersPathP=os.path.join(current_dir,'clustersPy160')
centroidsPathP=os.path.join(clustersPathP,'centroids.pkl')
centroidsP= pickle.load(open(centroidsPathP, 'rb'))



DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = UniXcoder("microsoft/unixcoder-base")
model.to(DEVICE)

#returns numpy array of embeddings
def get_embeddings(model,tokens,device=DEVICE):
  tokens_ids = model.tokenize([tokens],max_length=512,mode="<encoder-only>")
  source_ids = torch.tensor(tokens_ids).to(device)
  _,embeddings = model(source_ids)
  return embeddings.detach()


# # Get the directory where Graph.py is located
# the files in the directory are named as test1.py, test2.py, test3.py, ... We sort according to number
# M2CodeFiles=sorted(M2CodeFiles, key=lambda x: int(re.search(r'\d+', x).group()))

CatlasCodeDirJ = os.path.join(current_dir, "catlasM2UniDedup")
CatlasCodeDirPy= os.path.join(current_dir, "catLMPyDedupUni")

def getClosestNeibours(query,centroids,clustersPath,noOfCentroidsSerached=30,k=3,threshold=0.8):
    distances=np.einsum('ac,bc->ab', query, centroids)[0]
    # pick the minimum 10 arguments from the distances
    clusterindices=np.argsort(distances)[-noOfCentroidsSerached:]
    results=[]
    for clusterindex in clusterindices:
        cluster=pickle.load(open(os.path.join(clustersPath,f'cluster{clusterindex}.pkl'), 'rb'))
        # res=cluster.query(query)
        similarities=np.einsum('ac,bc->ab', query, cluster.vectors)[0]
        index=np.argmax(similarities)
        resid=cluster.idx[index]
        similarity=similarities[index]
        if similarity>=threshold:
            results.append((resid,similarity))
    return results


def queryDB(query,noOfCentroidsSerached=35,k=3,isJava=True,isPython=True,thresholdSameLanguage=0.8,thresholdDifferentLanguage=0.6):
    global centroidsJ,clustersPathJ,centroidsP,clustersPathP
    if isJava:
        #give more priority to Java results
        idsAndDistancesJ=getClosestNeibours(query,centroidsJ,clustersPathJ,noOfCentroidsSerached,k,thresholdSameLanguage)
        idsAndDistancesP=[]
        noOfJavaResults=len(idsAndDistancesJ)
        if noOfJavaResults<k:
            idsAndDistancesP=getClosestNeibours(query,centroidsP,clustersPathP,noOfCentroidsSerached,k-noOfJavaResults,thresholdDifferentLanguage)
        
    elif isPython:
        #give more priority to Python results
        idsAndDistancesP=getClosestNeibours(query,centroidsP,clustersPathP,noOfCentroidsSerached,k,thresholdSameLanguage)
        noOfPythonResults=len(idsAndDistancesP)
        idsAndDistancesJ=[]
        if noOfPythonResults<k:
            idsAndDistancesJ=getClosestNeibours(query,centroidsJ,clustersPathJ,noOfCentroidsSerached,k-noOfPythonResults,thresholdDifferentLanguage)
    else:
        # sort the results based on similarity equally
        idsAndDistancesP=getClosestNeibours(query,centroidsP,clustersPathP,noOfCentroidsSerached,k,thresholdDifferentLanguage)
        # add a flag for python
        idsAndDistancesP_python=[(res[0],res[1],0) for res in idsAndDistancesP]
        idsAndDistancesJ=[]
        if len(idsAndDistancesP)<k:
            idsAndDistancesJ=getClosestNeibours(query,centroidsJ,clustersPathJ,noOfCentroidsSerached,k,thresholdDifferentLanguage)
        # add a flag for java
        idsAndDistancesJ_Java=[(res[0],res[1],1) for res in idsAndDistancesP]
        
        idsAndDistances=idsAndDistancesP_python+idsAndDistancesJ_Java
        
        results=sorted(idsAndDistances,key=lambda x: 1-x[1])
        # classify each id based on the flag
        idsAndDistancesP=[]
        idsAndDistancesJ=[]
        for i in range(k):
            if results[i][2]==0:
                idsAndDistancesP.append((results[i][0],results[i][1]))
            else:
                idsAndDistancesJ.append((results[i][0],results[i][1]))

    resultsJ=sorted(idsAndDistancesJ,key=lambda x: 1-x[1])
    JavaDB_ids=[res[0] for res in resultsJ[:k]]
    resultsP=sorted(idsAndDistancesP,key=lambda x: 1-x[1])
    PythonDB_ids=[res[0] for res in resultsP[:k]]

    
    global CatlasCodeDirPy,CatlasCodeDirJ
    codes=[]
    tests=[]
    for id in JavaDB_ids:
        # open json
        with open(os.path.join(CatlasCodeDirJ, f"test{id}.json")) as f:
            data = json.load(f)
            codes.append(data["code"])
            test=data["test_cases"]
            tests.append(test)
    for id in PythonDB_ids:
        # open json
        with open(os.path.join(CatlasCodeDirPy, f"test{id}.json")) as f:
            data = json.load(f)
            codes.append(data["code"])
            test=data["test_cases"]
            tests.append(test)

    return codes,tests

def query_db(code,isJava,isPython,thresholdSameLanguage=0.8,thresholdDifferentLanguage=0.6):
    
    global model, DEVICE,centroidsJ,centroidsP
    query = get_embeddings(model, code, DEVICE)
    query=torch.nn.functional.normalize(query,p=2, dim=1)
    query = query.numpy()

    codes,tests=queryDB(query,35,3,isJava,isPython,thresholdSameLanguage,thresholdDifferentLanguage)
    return codes,tests
