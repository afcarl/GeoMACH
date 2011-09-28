from __future__ import division
import wrapper, GeoMACH
import numpy, pylab, copy
import string
import mpl_toolkits.mplot3d.axes3d as p3


class vertex:

    def __init__(self):
        self.e = []
        self.d = []

        self.f = []
        self.i = []
        self.j = []

    def addEdgeLink(self, e, d):
        self.e.append(e)
        self.d.append(d)

    def addFaceLink(self, f, i, j):
        self.f.append(f)
        self.i.append(i)
        self.j.append(j)

    def getP(self, oml):
        return oml.faces[self.f[0]].getP(self.i[0],self.j[0])

    def setC(self, oml, value):
        for f in range(len(self.f)):
            oml.faces[self.f[f]].setC(self.i[f],self.j[f],value)

    def setP(self, oml, value):
        for f in range(len(self.f)):
            oml.faces[self.f[f]].setP(self.i[f],self.j[f],value)


class edge:

    def __init__(self):
        self.f = []
        self.i1 = []
        self.i2 = []
        self.j1 = []
        self.j2 = []

    def addLink(self, f, i1, i2, j1, j2):
        self.f.append(f)
        self.i1.append(i1)
        self.i2.append(i2)
        self.j1.append(j1)
        self.j2.append(j2)

    def getm(self, oml):
        if self.i1[0]==self.i2[0]:
            m = oml.faces[self.f[0]].m[1]
        else:
            m = oml.faces[self.f[0]].m[0]
        return m

    def getClen(self, oml):
        if self.i1[0] == self.i2[0]:
            Clen = oml.faces[self.f[0]].getm()[1]
        else:
            Clen = oml.faces[self.f[0]].getm()[0]
        return Clen

    def getPlen(self, oml):
        if self.i1[0] == self.i2[0]:
            Plen = oml.faces[self.f[0]].getn()[1]
        else:
            Plen = oml.faces[self.f[0]].getn()[0]
        return Plen

    def getIndices(self, f, d):
        if self.i1[f] == self.i2[f]:
            i = self.i1[f]
            if self.j1[f] == 0:
                j = d
            else:
                j = -1-d
        else:
            j = self.j1[f]
            if self.i1[f] == 0:
                i = d
            else:
                i = -1-d
        return i,j

    def getC(self, oml, d):
        i,j = self.getIndices(0,d)
        return oml.faces[self.f[0]].getC(i,j)

    def getP(self, oml, d):
        i,j = self.getIndices(0,d)
        return oml.faces[self.f[0]].getP(i,j)

    def getCs(self, oml):
        Clen = self.getClen(oml)
        C = numpy.zeros((Clen,3))
        for i in range(Clen):
            C[i,:] = self.getC(oml,i)
        return C

    def getPs(self, oml):
        Plen = self.getPlen(oml)
        P = numpy.zeros((Plen,3))
        for i in range(Plen):
            P[i,:] = self.getP(oml,i)
        return P

    def setC(self, oml, d, value):
        for f in range(len(self.f)):
            i,j = self.getIndices(f,d)
            oml.faces[self.f[f]].setC(i,j,value)

    def setP(self, oml, d, value):
        for f in range(len(self.f)):
            i,j = self.getIndices(f,d)
            oml.faces[self.f[f]].setP(i,j,value)

    def setCs(self, oml, values):
        Clen = values.shape[0]
        for i in range(Clen):
            self.setC(oml,i,values[i,:])


class face:

    def __init__(self, P=None):
        self.surface = wrapper.surface()
        self.surface.P = copy.copy(P)
        self.m0id = None
        self.m1id = None
        self.m = [4,4]

    def initializeDirect(self,C,n):
        self.surface.create(C,n)

    def initializeBspline(self):
        self.surface.C = numpy.zeros((self.m[0],self.m[1],3))

    def performFit(self):
        self.surface.fit(self.surface.P,self.surface.C,self.m)

    def getm(self):
        return self.surface.C.shape

    def getn(self):
        return self.surface.P.shape

    def getC(self,i,j):
        return self.surface.C[i,j,:]

    def getP(self,i,j):
        return self.surface.P[i,j,:]

    def getdPdC(self,i,j):
        return self.surface.dPdC[i,j]

    def getPder(self,u,v,du,dv):
        return self.surface.evaluatePder(u,v,du,dv)

    def getPderAt(self,t0,t1,du,dv):
        return self.surface.evaluatePderAt(t0,t1,du,dv)

    def setC(self,i,j,value):
        self.surface.C[i,j,:] = value[:]

    def setP(self,i,j,value):
        self.surface.P[i,j,:] = value[:]

    def getCs(self):
        return self.surface.C

    def getPs(self):
        return self.surface.P

    def setCs(self,C):
        self.surface.C[:,:,:] = C[:,:,:]

    def evaluatePts(self):
        self.surface.evaluatePts()

    def evaluateJacob(self):
        self.surface.evaluateJacob()

    def projectPt(self,P,u,v):
        return self.surface.projectPt(P,u,v)


class size:

    def __init__(self, idf):
        self.idf = idf
        self.f = []
        self.g = []

    def addLink(self, f, g):
        self.f.append(f)
        self.g.append(g)

    def getm(self, oml):
        face = oml.faces[self.f[0]]
        if self.g[0] == 0:
            m = face.m[0]
        else:
            m = face.m[1]
        return m

    def getn(self, oml):
        face = oml.faces[self.f[0]]
        P = face.getPs()
        if self.g[0] == 0:
            n = P.shape[0]
        else:
            n = P.shape[1]
        return n

    def setm(self, oml, m):
        for f in range(len(self.f)):
            face = oml.faces[self.f[f]]
            if self.g[f]==0:
                face.m[0] = m
            else:
                face.m[1] = m


class manifold2d:

    def __init__(self):
        self.vertices = []
        self.edges = []
        self.faces = []
        self.sizes = []

        self.vSymm = []
        self.eSymm = []        

    def setm(self,z,m):
        self.sizes[z].setm(self,m)
        self.initializeBsplines()
        self.fitCurves()
        self.fitSurfaces()

    def importCGNSsurf(self, filename):
        n = GeoMACH.nsurfaces2(filename)  
        z,sizes = GeoMACH.surfacesizes2(filename, n) 
        P0 = []
        for i in range(n):
            P0.append(GeoMACH.getsurface2(filename,z[i],sizes[i,0],sizes[i,1]))
        self.importSurfaces(P0)

    def importSurfacesDirect(self, C, ratio=4):        
        for s in range(len(C)):
            self.faces.append(face())
            n = [C[s].shape[0]*ratio,C[s].shape[1]*ratio]
            self.faces[-1].initializeDirect(C[s],n)

        self.vtol = 1e-10#1e-10
        self.etol = 1e-5#1e-5

        self.computeTopology()
        self.determineSymmPlane(1)
        self.initializeSizes()
        self.printSizes()
        self.tessellate()

    def importSurfaces(self, P0, ratio=4):        
        for s in range(len(P0)):
            self.faces.append(face(P0[s]))

        self.vtol = 1e-10#1e-10
        self.etol = 1e-5#1e-5

        self.computeTopology()
        self.determineSymmPlane(1)
        self.initializeSizes()
        self.assignSizes(ratio)
        self.tessellate()
        self.initializeBsplines()
        self.fitCurves()
        self.fitSurfaces()

    def determineSymmPlane(self, plane):
        for v in range(len(self.vertices)):
            vertex = self.vertices[v]
            if numpy.linalg.norm(vertex.getP(self)[plane]) < self.vtol:
                self.vSymm.append(v)
        for e in range(len(self.edges)):
            edge = self.edges[e]
            if numpy.linalg.norm(edge.getPs(self)[:,plane]) < self.etol:
                self.eSymm.append(e)

    def computeTopology(self):        
        for f in range(len(self.faces)):
            face = self.faces[f]
            for i in range(-1,1):
                self.addEdge(f,i,i,0,-1,face.getPs()[i,:,:])
            for j in range(-1,1):
                self.addEdge(f,0,-1,j,j,face.getPs()[:,j,:])
        for f in range(len(self.faces)):
            face = self.faces[f]
            for i in range(-1,1):
                for j in range(-1,1):
                    self.addVertex(f,i,j,face.getPs()[i,j,:])

        sum = len(self.vertices)
        for e in range(len(self.edges)):
            sum += self.edges[e].getPlen(self) - 2
        for f in range(len(self.faces)):
            n = self.faces[f].getn()
            sum += (n[0]-2)*(n[1]-2)

        print 'Topology computed.'
        print 'Vertices:', len(self.vertices)
        print 'Edges:', len(self.edges)
        print 'Faces:', len(self.faces)
        print 'Points:', sum

    def addEdge(self, f, i1, i2, j1, j2, P):
        found = False
        reverse = False
        index = 0
        
        for e in range(len(self.edges)):
            if self.edges[e].getPlen(self) == P.shape[0]:
                if numpy.linalg.norm(self.edges[e].getPs(self)-P) < self.etol:
                    found = True
                    index = e
                    reverse = False
                elif numpy.linalg.norm(self.edges[e].getPs(self)-P[::-1]) < self.etol:
                    found = True
                    index = e
                    reverse = True
        if not found:
            self.edges.append(edge())
            index = -1
        if reverse:
            self.edges[index].addLink(f,i2,i1,j2,j1)
        else:
            self.edges[index].addLink(f,i1,i2,j1,j2)

    def addVertex(self, f, i, j, P):
        found = False
        index = 0
        for v in range(len(self.vertices)):
            if numpy.linalg.norm(self.vertices[v].getP(self)-P) < self.vtol:
                found = True
                index = v
        if not found:
            self.vertices.append(vertex())
            index = -1
            for e in range(len(self.edges)):
                if numpy.linalg.norm(self.edges[e].getP(self,0)-P) < self.vtol:
                    self.vertices[index].addEdgeLink(e,0)
                elif numpy.linalg.norm(self.edges[e].getP(self,-1)-P) < self.vtol:
                    self.vertices[index].addEdgeLink(e,-1)
        self.vertices[index].addFaceLink(f,i,j)

    def initializeSizes(self):
        for f in range(len(self.faces)):
            self.faces[f].m0id = 2*f
            self.faces[f].m1id = 2*f + 1
        done = False
        while not done:
            done = True
            for e in range(len(self.edges)):
                edge = self.edges[e]
                if edge.i1[0]==edge.i2[0]:
                    id0 = self.faces[edge.f[0]].m1id
                else:
                    id0 = self.faces[edge.f[0]].m0id
                for f in range(1,len(edge.f)):
                    if edge.i1[f]==edge.i2[f]:
                        idf = self.faces[edge.f[f]].m1id
                    else:
                        idf = self.faces[edge.f[f]].m0id
                    if id0!=idf:
                        done = False
                        if edge.i1[f]==edge.i2[f]:
                            self.setSize(self.faces[edge.f[f]].m1id,id0)
                        else:
                            self.setSize(self.faces[edge.f[f]].m0id,id0)
        for f in range(len(self.faces)):
            self.addSize(self.faces[f].m0id,f,0)
            self.addSize(self.faces[f].m1id,f,1)

    def printSizes(self):
        ms = []
        for s in range(len(self.sizes)):
            m = self.sizes[s].getm(self)
            ms.append(m)
        print 'Sizes:', ms
                                           
    def assignSizes(self, ratio):
        ms = []
        for s in range(len(self.sizes)):
            n = self.sizes[s].getn(self)
            m = int(n/ratio)
            if m<4:
                m = 4
            self.sizes[s].setm(self,m)
            ms.append(m)
        print 'Sizes:', ms

    def setSize(self, idf, id0):
        for f in range(len(self.faces)):
            if self.faces[f].m0id==idf:
                self.faces[f].m0id = id0
            if self.faces[f].m1id==idf:
                self.faces[f].m1id = id0

    def addSize(self, idf, f, g):
        found = False
        index = 0
        for s in range(len(self.sizes)):
            if idf==self.sizes[s].idf:
                found = True
                index = s
        if not found:
            self.sizes.append(size(idf))
            index = -1
        self.sizes[index].addLink(f,g)

    def tessellate(self):
        for v in range(len(self.vertices)):
            vertex = self.vertices[v]
            sum = numpy.zeros(3)
            for f in range(len(vertex.f)):
                sum += self.faces[vertex.f[f]].getPs()[vertex.i[f],vertex.j[f]]
            avg = sum/len(vertex.f)
            vertex.setP(self,avg)
        for e in range(len(self.edges)):
            edge = self.edges[e]
            sum = numpy.zeros((edge.getPlen(self),3))
            for f in range(len(edge.f)):
                if edge.i1[f]==edge.i2[f]:
                    if edge.j1[f]==0:
                        sum += self.faces[edge.f[f]].getPs()[edge.i1[f],:]
                    else:
                        sum += self.faces[edge.f[f]].getPs()[edge.i1[f],::-1]
                else:
                    if edge.i1[f]==0:
                        sum += self.faces[edge.f[f]].getPs()[:,edge.j1[f]]
                    else:
                        sum += self.faces[edge.f[f]].getPs()[::-1,edge.j1[f]]
            avg = sum/len(edge.f)
            for i in range(1,sum.shape[0]-1):
                edge.setP(self,i,avg[i,:])

    def adjacentVindices(self, vertex, f):
        i,j = vertex.i[f], vertex.j[f]
        if i==0:
            i = 1
        else:
            i = -2
        if j==0:
            j = 1
        else:
            j = -2
        return i,j

    def adjacentEindices(self, edge, f, d):
        i,j = edge.getIndices(f,d)
        i1,i2,j1,j2 = edge.i1[f],edge.i2[f],edge.j1[f],edge.j2[f]
        if i1==i2:
            if i1==0:
                i = 1
            else:
                i = -2
        else:
            if j1==0:
                j = 1
            else:
                j = -2
        return i,j

    def fillet(self):
        for v in range(len(self.vertices)):
            vertex = self.vertices[v]
            sum = numpy.zeros(3)
            for f in range(len(vertex.f)):
                i,j = self.adjacentVindices(vertex,f)
                sum += self.faces[vertex.f[f]].getCs()[i,j]
            sum /= len(vertex.f)
            if v in self.vSymm:
                sum[1] = 0
            vertex.setC(self,sum)
        for e in range(len(self.edges)):
            edge = self.edges[e]
            for d in range(edge.getClen(self)-2):
                sum = numpy.zeros(3)
                for f in range(len(edge.f)):
                    i,j = self.adjacentEindices(edge,f,d+1)
                    sum += self.faces[edge.f[f]].getCs()[i,j]
                sum /= len(edge.f)
                if e in self.eSymm:
                    sum[1] = 0
                edge.setC(self,d+1,sum)

    def initializeBsplines(self):
        for f in range(len(self.faces)):
            self.faces[f].initializeBspline()

    def fitCurves(self):
        curve = wrapper.curve()
        for e in range(len(self.edges)):
            edge = self.edges[e]
            curve.fit(edge.getPs(self),edge.getm(self))
            edge.setCs(self,curve.C)

    def fitSurfaces(self):
        for f in range(len(self.faces)):
            self.faces[f].performFit()

    def update(self):
        for f in range(len(self.faces)):        
            self.faces[f].evaluatePts()

    def setC(self, i, C):
        if i < len(self.vertices):
            self.vertices[i].setC(self,C)
        elif i < self.getJf(0,0,0,True):
            i -= len(self.vertices)
            for e in range(len(self.edges)):
                if i >= self.edges[e].getClen(self)-2:
                    i -= self.edges[e].getClen(self)-2
                elif i > -1:
                    self.edges[e].setC(self,i+1,C)
                    i = -1
        else:
            i -= self.getJf(0,0,0,True)
            for f in range(len(self.faces)):
                m = self.faces[f].getm()
                if i >= (m[0]-2)*(m[1]-2):
                    i -= (m[0]-2)*(m[1]-2)
                elif i > -1:
                    self.faces[f].setC(i%(m[0]-2)+1,int(numpy.floor(i/(m[0]-2)))+1,C)
                    i = -1

    def getC(self, i):
        if i < len(self.vertices):
            C = self.vertices[i].getP(self)
        elif i < self.getJf(0,0,0,True):
            i -= len(self.vertices)
            for e in range(len(self.edges)):
                if i >= self.edges[e].getClen(self)-2:
                    i -= self.edges[e].getClen(self)-2
                elif i > -1:
                    C = self.edges[e].getC(self,i+1)
                    i = -1
        else:
            i -= self.getJf(0,0,0,True)
            for f in range(len(self.faces)):
                m = self.faces[f].getm()
                if i >= (m[0]-2)*(m[1]-2):
                    i -= (m[0]-2)*(m[1]-2)
                elif i > -1:
                    C = self.faces[f].getC(i%(m[0]-2)+1,int(numpy.floor(i/(m[0]-2)))+1)
                    i = -1
        return C

    def incC(self, i, value):
        C = self.getC(i)
        C += value
        self.setC(i,C)

    def getPts(self):
        n = self.getn()
        P = numpy.zeros((n,3))
        index = 0
        for v in range(len(self.vertices)):
            P[index,:] = self.vertices[v].getP(self)
            index += 1
        for e in range(len(self.edges)):
            for d in range(1,self.edges[e].getPlen(self)-1):
                P[index,:] = self.edges[e].getP(self,d)
                index += 1
        for f in range(len(self.faces)):
            for j in range(1,self.faces[f].getn()[1]-1):
                for i in range(1,self.faces[f].getn()[0]-1):
                    P[index,:] = self.faces[f].getP(i,j)
                    index += 1
        return P

    def getm(self):
        sum = len(self.vertices)
        for e in range(len(self.edges)):
            sum += self.edges[e].getClen(self) - 2
        for f in range(len(self.faces)):
            m = self.faces[f].getm()
            sum += (m[0]-2)*(m[1]-2)
        return sum

    def getn(self):
        sum = len(self.vertices)
        for e in range(len(self.edges)):
            sum += self.edges[e].getPlen(self) - 2
        for f in range(len(self.faces)):
            n = self.faces[f].getn()
            sum += (n[0]-2)*(n[1]-2)
        return sum

    def getme(self):
        return self.getJf(0,0,0,True)

    def getne(self):
        return self.getJf(0,0,0,False)

    def getGlobalJacobianFDfilleted(self):
        me = self.getme()
        ne = self.getne()
        m = self.getm()
        n = self.getn()
        J = numpy.zeros((n,m-me))
        
        P0 = self.getPts()
        value = numpy.array([1,0,0])
        for j in range(me,m):
            self.incC(j,value)
            self.fillet()
            self.update()
            P = self.getPts()
            for i in range(n):
                J[i,j-me] = P[i,0] - P0[i,0]
            self.incC(j,-value)
        self.fillet()
        self.update()

        return J

    def getGlobalJacobianFilleted(self):
        me = self.getJf(0,0,0,True)
        ne = self.getJf(0,0,0,False)
        m = self.getm()
        n = self.getn()

        J = self.getGlobalJacobian()
        Jf = J[:,me:m]
        for v in range(len(self.vertices)):
            vertex = self.vertices[v]
            for f in range(len(vertex.f)):
                i,j = self.adjacentVindices(vertex,f)  
                i,j = self.processIndices(vertex.f[f],i,j,True)
                Ja = self.getJv(v,True)
                Jb = self.getJf(vertex.f[f],i-1,j-1,True)
                Jf[:,Jb-me] += J[:,Ja]/len(vertex.f)
        for e in range(len(self.edges)):
            edge = self.edges[e]
            for d in range(edge.getClen(self)-2):
                for f in range(len(edge.f)):
                    i,j = self.adjacentEindices(edge,f,d+1)
                    i,j = self.processIndices(edge.f[f],i,j,True)
                    Ja = self.getJe(e,d,True)
                    Jb = self.getJf(edge.f[f],i-1,j-1,True)
                    Jf[:,Jb-me] += J[:,Ja]/len(edge.f)

        return Jf

    def getGlobalJacobianFD(self):
        m = self.getm()
        n = self.getn()
        J = numpy.zeros((n,m))
        
        P0 = self.getPts()
        value = numpy.array([1,0,0])
        for j in range(m):
            self.incC(j,value)
            self.update()
            P = self.getPts()
            for i in range(n):
                J[i,j] = P[i,0] - P0[i,0]
            self.incC(j,-value)
        self.update()

        return J

    def getGlobalJacobian(self):
        m = self.getm()
        n = self.getn()
        J = numpy.zeros((n,m))

        for f in range(len(self.faces)):
            self.faces[f].evaluateJacob()

        for i in range(len(self.vertices)):
            J[i,i] = 1.0

        for v in range(len(self.vertices)):
            vertex = self.vertices[v]
            for e in range(len(vertex.e)):
                edge = self.edges[vertex.e[e]]
                face = self.faces[edge.f[0]]
                for d in range(edge.getPlen(self)-2):
                    J1 = self.getJe(vertex.e[e],d,False)
                    J2 = self.getJv(v,True)
                    B1 = self.getB1e(vertex.e[e],d)
                    B2 = self.getB2ev(v,e)
                    J[J1,J2] = face.getdPdC(B1,B2)

        for e in range(len(self.edges)):
            edge = self.edges[e]
            face = self.faces[edge.f[0]]
            for d2 in range(edge.getClen(self)-2):
                for d1 in range(edge.getPlen(self)-2):
                    J1 = self.getJe(e,d1,False)
                    J2 = self.getJe(e,d2,True)
                    B1 = self.getB1e(e,d1)
                    B2 = self.getB2ee(e,d2)
                    J[J1,J2] = face.getdPdC(B1,B2)

        for v in range(len(self.vertices)):
            vertex = self.vertices[v]
            for f in range(len(vertex.f)):
                face = self.faces[vertex.f[f]]
                for i in range(face.getn()[0]-2):
                    for j in range(face.getn()[1]-2):
                        J1 = self.getJf(vertex.f[f],i,j,False)
                        J2 = self.getJv(v,True)
                        B1 = self.getB1f(vertex.f[f],i+1,j+1)
                        B2 = self.getB2fv(v,f)
                        J[J1,J2] = face.getdPdC(B1,B2)

        for e in range(len(self.edges)):
            edge = self.edges[e]
            for d in range(edge.getClen(self)-2):
                for f in range(len(edge.f)):
                    face = self.faces[edge.f[f]]
                    for i in range(face.getn()[0]-2):
                        for j in range(face.getn()[1]-2): 
                            J1 = self.getJf(edge.f[f],i,j,False)
                            J2 = self.getJe(e,d,True)
                            B1 = self.getB1f(edge.f[f],i+1,j+1)
                            B2 = self.getB2fe(f,e,d)
                            J[J1,J2] = face.getdPdC(B1,B2)

        for f in range(len(self.faces)):
            face = self.faces[f]
            for i1 in range(face.getn()[0]-2):
                for j1 in range(face.getn()[1]-2):  
                    for i2 in range(face.getm()[0]-2):
                        for j2 in range(face.getm()[1]-2): 
                            J1 = self.getJf(f,i1,j1,False)
                            J2 = self.getJf(f,i2,j2,True) 
                            B1 = self.getB1f(f,i1+1,j1+1)
                            B2 = self.getB2ff(f,i2+1,j2+1)
                            J[J1,J2] = face.getdPdC(B1,B2)

        return J

    def getB1e(self,e,d):
        edge = self.edges[e]
        face = self.faces[edge.f[0]]
        f = edge.f[0]
        i,j = edge.getIndices(0,d+1)
        i,j = self.processIndices(f,i,j,False)
        return i + j*face.getn()[0]

    def getB1f(self,f,i,j):
        face = self.faces[f]
        return i + j*face.getn()[0]        

    def getB2ev(self,v,e):
        vertex = self.vertices[v]
        edge = self.edges[vertex.e[e]]
        face = self.faces[edge.f[0]]
        f = edge.f[0]
        i,j = edge.getIndices(0,vertex.d[e])
        i,j = self.processIndices(f,i,j,True)
        return i + j*face.getm()[0]

    def getB2fv(self,v,f):
        vertex = self.vertices[v]
        face = self.faces[vertex.f[f]]
        i = vertex.i[f]
        j = vertex.j[f]
        i,j = self.processIndices(vertex.f[f],i,j,True)
        return i + j*face.getm()[0]

    def getB2ee(self,e,d):
        edge = self.edges[e]
        face = self.faces[edge.f[0]]
        f = edge.f[0]
        i,j = edge.getIndices(0,d+1)
        i,j = self.processIndices(f,i,j,True)
        return i + j*face.getm()[0]

    def getB2fe(self,f,e,d):
        edge = self.edges[e]
        face = self.faces[edge.f[f]]
        i,j = edge.getIndices(f,d+1)
        i,j = self.processIndices(edge.f[f],i,j,True)
        return i + j*face.getm()[0]

    def getB2ff(self,f,i,j):
        face = self.faces[f]
        return i + j*face.getm()[0]  

    def getJv(self,v,isCtrlPt):
        return v

    def getJe(self,e,d,isCtrlPt):
        index = len(self.vertices)
        if isCtrlPt:
            for ee in range(e):
                index += self.edges[ee].getClen(self) - 2
        else:
            for ee in range(e):
                index += self.edges[ee].getPlen(self) - 2
        index += d
        return index

    def getJf(self,f,i,j,isCtrlPt):
        index = len(self.vertices)
        if isCtrlPt:
            for e in range(len(self.edges)):
                index += self.edges[e].getClen(self) - 2
            for ff in range(f):
                m = self.faces[ff].getm()
                index += (m[0]-2)*(m[1]-2)
            m = self.faces[f].getm()
            index += i + j*(m[0]-2)
        else:
            for e in range(len(self.edges)):
                index += self.edges[e].getPlen(self) - 2
            for ff in range(f):
                n = self.faces[ff].getn()
                index += (n[0]-2)*(n[1]-2)
            n = self.faces[f].getn()
            index += i + j*(n[0]-2)
        return index

    def processIndices(self,f,i,j,isCtrlPt):
        if isCtrlPt:
            if i<0:
                i += self.faces[f].getm()[0]
            if j<0:
                j += self.faces[f].getm()[1]
        else:
            if i<0:
                i += self.faces[f].getn()[0]
            if j<0:
                j += self.faces[f].getn()[1]
        return i,j

    def getRanges(self):
        maxs = []
        mins = []
        for f in range(len(self.faces)):
            P = self.faces[f].getPs()
            maxs.append([numpy.max(P[:,:,0]),numpy.max(P[:,:,1]),numpy.max(P[:,:,2])])
            mins.append([numpy.min(P[:,:,0]),numpy.min(P[:,:,1]),numpy.min(P[:,:,2])])
        maxs = numpy.array(maxs)
        mins = numpy.array(mins)
        maxs2 = numpy.zeros(3)
        mins2 = numpy.zeros(3)
        for i in range(3):
            maxs2[i] = numpy.max(maxs[:,i])
            mins2[i] = numpy.min(mins[:,i])
        return maxs2,mins2

    def plot(self, fig, mirror=False, plotP=True, plotN=False, plotB=False, plotS=False): 
        #self.ax = p3.Axes3D(self.fig,azim=210)  
        self.ax = p3.Axes3D(fig,azim=-135,elev=45)         

        if plotP:
            for f in range(len(self.faces)):
                P = self.faces[f].getPs()
                self.ax.plot_wireframe(P[:,:,0],P[:,:,1],P[:,:,2],linewidth=0.25)
                if mirror:
                    self.ax.plot_wireframe(P[:,:,0],-P[:,:,1],P[:,:,2],linewidth=0.25)
                #cen = self.surfaces[k].getMid()
                #self.ax.scatter([cen[0]],[cen[1]],[cen[2]])
        if plotN:
            for v in range(len(self.vertices)):
                P = self.vertices[v].getP(self)
                self.ax.scatter([P[0]],[P[1]],[P[2]])
                if mirror:
                    self.ax.scatter([P[0]],[-P[1]],[P[2]])
        if plotB:
            for e in range(len(self.edges)):
                P = self.edges[e].curve.P
                self.ax.plot(P[:,0],P[:,1],P[:,2],'k')
                C = self.boundaries[b].curve.C
                self.ax.scatter(C[:,0],C[:,1],C[:,2])
                if mirror:
                    self.ax.plot(P[:,0],-P[:,1],P[:,2],'k')
                    self.ax.scatter(C[:,0],-C[:,1],C[:,2])
        if plotS:
            for f in range(len(self.faces)):
                C = self.faces[f].getCs()
                for i in range(C.shape[0]):
                    self.ax.scatter(C[i,:,0],C[i,:,1],C[i,:,2])
                    if mirror:
                        self.ax.scatter(C[i,:,0],-C[i,:,1],C[i,:,2])
        maxs,mins = self.getRanges()
        lengths = numpy.array([maxs[0]-mins[0],maxs[1]-mins[1],maxs[2]-mins[2]])
        maxL = numpy.max(lengths)
        maxL *= 0.6

        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.ax.set_zlabel('z')
        Y = numpy.linspace(-maxL/2.0,maxL/2.0,2)
        Y2 = numpy.linspace(-maxL/3.0,maxL*2/3.0,2)
        self.ax.scatter(Y2,Y,Y,s=0.0001)

