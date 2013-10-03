class Test(BaseModeller, EstimatorMixin):
    def __init__(self, a=1, b='a', c=None):
        self.a = 1
        self.b = b
        self.c = c
        
    def fit(self, X):
        self.mean_ = np.array([1,2,3])
        self.mean0_ = self.mean_[1] 
        self.mean1_ = 4.0
        return self

t = Test().fit(None)
f = tables.open_file('f.h5', 'w')
t.to_pytables(f.root)
print f
print f.root.Test.params.row[:]

f.close()
