from __future__ import division
from PAM.components import Primitive, Variable, airfoils
import numpy, pylab, time, scipy.sparse
import PAM.PAMlib as PAMlib


class Wing(Primitive):
    """ A component used to model lifting surfaces. """

    def __init__(self, nx=1, nz=1, left=2, right=2):
        """ Initialization method
        nx: integer
            Number of surfaces in x (chord-wise) direction
        nz: integer
            Number of surfaces in z (span-wise) direction
        left, right: integer
            The v[0] and v[-1] sections of the wing
            0: open tip, C0
            1: open tip, C1
            2: closed tip
        """ 

        super(Wing,self).__init__(nx,0,nz)

        self.addFace(-1, 3, 0.5)
        self.addFace( 1, 3,-0.5)
        self.connectEdges(f1=0,u1=0,f2=1,u2=-1)
        self.connectEdges(f1=0,u1=-1,f2=1,u2=0)
        if left==2:
            self.connectEdges(f1=0,v1=-1,f2=1,v2=-1)
        if right==2:
            self.connectEdges(f1=0,v1=0,f2=1,v2=0)

        self.left = left
        self.right = right
        self.ax1 = 3
        self.ax2 = 2

    def setDOFs(self):
        setC1 = self.setC1
        setCornerC1 = self.setCornerC1
        for f in range(2):
            setC1('surf', f, val=True) #C1 Everywhere
            setC1('surf', f, i=-f, u=-f, val=False) #C0 trailing edge
            setC1('edge', f, i=-f, u=-f, val=True) #C0 trailing edge
            if self.left==0:  
                setC1('surf', f, j=-1, v=-1, val=False) #C0 left edge
                setC1('edge', f, j=-1, v=-1, val=True) #C0 left edge
                setCornerC1(f, i=-f, j=-1, val=False) #C0 left TE corner     
            if self.right==0:         
                setC1('surf', f, j=0, v=0, val=False) #C0 right edge
                setC1('edge', f, j=0, v=0, val=True) #C0 right edge
                setCornerC1(f, i=-f, j=0, val=False) #C0 right TE corner

    def initializeVariables(self):
        super(Wing,self).initializeVariables()
        ni = self.Qs[0].shape[0]
        nj = self.Qs[0].shape[1]
        v = self.variables
        v['shapeU'] = Variable((ni,nj,3))
        v['shapeL'] = Variable((ni,nj,3))
        self.setAirfoil()

    def setAirfoil(self,filename="naca0012"):
        Ps = airfoils.fitAirfoil(self,filename)
        for f in range(len(self.Ks)):
            for j in range(self.Ns[f].shape[1]):
                shape = 'shapeU' if f==0 else 'shapeL'
                self.variables[shape].V[:,j,:2] = Ps[f][:,:]
        
    def computeQs(self):
        val = lambda var: self.variables[var]()
        ni = self.Qs[0].shape[0]
        nj = self.Qs[0].shape[1]

        #if self.left==2:
        #    v['pos'][-1] = 2*v['pos'][-2] - v['pos'][-3]
        #if self.right==2:
        #    v['pos'][0] = 2*v['pos'][1] - v['pos'][2]

        shapes = [val('shapeU'), val('shapeL')]
        nQ = nj*(9+6*ni)
        self.computeSections(nQ, shapes)


if __name__ == '__main__':
    w = Wing(nx=2,nz=2,left=0)
    import PUBS
    from mayavi import mlab

    w.oml0 = PUBS.PUBS(w.Ps)
    w.setDOFs()
    w.oml0.updateBsplines()
    w.computems()
    w.initializeDOFmappings()
    w.initializeVariables()
    w.variables['pos'][:,2] = numpy.linspace(0,1,w.Qs[0].shape[1])
    #for j in range(w.Qs[0].shape[1]):
    #    w.variables['shape'][0,:,j,0] = 1 - numpy.linspace(0,1,w.Qs[0].shape[0])
    #    w.variables['shape'][1,:,j,0] = numpy.linspace(0,1,w.Qs[0].shape[0])
    w.variables['pos'][:,0] = numpy.linspace(0,1,w.Qs[0].shape[1])
    w.variables['pos'][:,1] = numpy.linspace(0,1,w.Qs[0].shape[1])
    #w.variables['rot'][:,2] = 20
    w.parameters['nor'][:,:] = 1.0
    w.setAirfoil("naca0012.dat")
    w.computeQs()
    w.propagateQs()
    w.oml0.computePoints()
    w.oml0.plot()
    name='wing'
    w.oml0.write2Tec(name)
    w.oml0.write2TecC(name)
