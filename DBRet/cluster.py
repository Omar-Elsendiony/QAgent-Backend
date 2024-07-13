class Cluster(object):
    def __init__(self,vectors=list(),idx=list()):
        self.vectors = vectors
        self.idx= idx

    def add_vertex(self, vector, datasetkey):
        self.vectors.append(vector)
        self.idx.append(datasetkey)
    
    def __contains__(self, key):
        return key in self.idx

    def __iter__(self):
        return iter(self.vectors)

    def __str__(self):
        return 'Cluster ({})'.format(self.idx[:5])
    