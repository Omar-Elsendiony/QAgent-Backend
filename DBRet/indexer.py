import faiss
from faiss import write_index, read_index
import torch
import numpy as np
from tqdm import tqdm
import os
import shutil
# for pytorch to work with multiprocessing where OPENMP is linked multiple times to runtime 
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"


def indexVectors(embeddingsPath ,index_path):

   if not os.path.exists(index_path):
      print("Index Doesn't exist, creating one")
      Catembeddings = torch.load(embeddingsPath,map_location=torch.device('cpu'))
      print(Catembeddings.shape)
      vectors= torch.nn.functional.normalize(Catembeddings,dim=1)
      vectors= Catembeddings
      vectors=vectors.numpy()
      vector_dimension = vectors.shape[1]
      index = faiss.IndexFlatIP(vector_dimension)
      index.add(vectors)
      write_index(index, index_path)
      print("Finished Indexing Original Catlass Embeddings")
   else:
      index=read_index(index_path)
   return index

ctxt=512
catlasPyEmbeddingsPath=os.path.join(f'CatlasPyUDedup_C{ctxt}.pt')
catlasJEmbeddingsPath=os.path.join(f'CatlasJUDedup_C{ctxt}.pt')

Pyindexpath=os.path.join(f'catPy.index')
Jindexpath=os.path.join(f'catJava.index')

Pyindex=indexVectors(catlasPyEmbeddingsPath,Pyindexpath)
Jindex=indexVectors(catlasJEmbeddingsPath,Jindexpath)
