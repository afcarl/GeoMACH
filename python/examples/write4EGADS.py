from __future__ import division
import sys
sys.path.append(sys.path[0]+'/../')
import oml, GeoMACH
import numpy, pylab
import copy, time
import mpl_toolkits.mplot3d.axes3d as p3

n = [20,40]

P0 = []
P0.append(numpy.zeros((n[1],n[1],3),order='F'))
P0.append(numpy.zeros((n[0],n[1],3),order='F'))
P0.append(numpy.zeros((n[0],n[1],3),order='F'))
P0.append(numpy.zeros((n[1],n[0],3),order='F'))
P0.append(numpy.zeros((n[1],n[0],3),order='F'))

r = 1
dx = 1
dy = 1
dz = 1
            
a1 = [ 1]
a2 = [-1]
b1 = [ 1]
b2 = [-1]
s  = [-1]
for k in range(1):
    for i in range(n[1]):
        for j in range(n[1]):
            a = a1[k] + (a2[k]-a1[k])*i/(n[1]-1)
            b = b1[k] + (b2[k]-b1[k])*j/(n[1]-1)
            y = s[k]*r/(1+a**2+b**2)**0.5
            P0[0][i,j,0] = a*y*dx
            P0[0][i,j,1] = y*dy
            P0[0][i,j,2] = b*y*dz
a1 = [ 0, -1]
a2 = [ 1,  0]
b1 = [ 1, -1]
b2 = [-1,  1]
s  = [-1,  1]
for k in range(2):
    for i in range(n[0]):
        for j in range(n[1]):
            a = a1[k] + (a2[k]-a1[k])*i/(n[0]-1)
            b = b1[k] + (b2[k]-b1[k])*j/(n[1]-1)
            x = s[k]*r/(1+a**2+b**2)**0.5
            P0[k+1][i,j,0] = x*dx
            P0[k+1][i,j,1] = a*x*dy
            P0[k+1][i,j,2] = b*x*dz
a1 = [-1,  1]
a2 = [ 1, -1]
b1 = [-1,  0]
b2 = [ 0,  1]
s  = [ 1, -1]
for k in range(2):
    for i in range(n[1]):
        for j in range(n[0]):
            a = a1[k] + (a2[k]-a1[k])*i/(n[1]-1)
            b = b1[k] + (b2[k]-b1[k])*j/(n[0]-1)
            z = s[k]*r/(1+a**2+b**2)**0.5
            P0[k+3][i,j,0] = a*z*dx
            P0[k+3][i,j,1] = b*z*dy
            P0[k+3][i,j,2] = z*dz

oml1 = oml.oml()
oml1.importSurfaces(P0)
oml1.plot(pylab.figure(),False)
pylab.show()





filename = "test.dat"
file = open(filename,"w")

file.write(str(oml1.nvert)+'\n')
file.write(str(oml1.nedge)+'\n')
file.write(str(oml1.nsurf)+'\n')

for i in range(oml1.nvert):
    file.write(str(oml1.C[i,0])+' ')
    file.write(str(oml1.C[i,1])+' ')
    file.write(str(oml1.C[i,2])+'\n')

edgePtr = numpy.zeros((oml1.nedge,3),int)
for i in range(oml1.nsurf):
    for u in range(2):
        for v in range(2):
            edgePtr[abs(oml1.surf_edge[i,u,v])-1,:] = [i,u,v]
ms = GeoMACH.getsurfacesizes(oml1.nsurf, oml1.nedge, oml1.ngroup, oml1.surf_edge, oml1.edge_group, oml1.group_m)
for i in range(oml1.nedge):
    surf = edgePtr[i,0]
    edge0 = edgePtr[i,1]
    edge1 = edgePtr[i,2]
    if edge0==0:
        if edge1==0:
            start = [0,0]
            end = [1,0]
        else:
            start = [0,1]
            end = [1,1]
    else:
        if edge1==0:
            start = [0,0]
            end = [0,1]
        else:
            start = [1,0]
            end = [1,1]
    if oml1.surf_edge[surf,edge0,edge1] < 0:
        temp = start
        start = end
        end = temp
    file.write(str(oml1.surf_vert[surf,start[0],start[1]])+' ')
    file.write(str(oml1.surf_vert[surf,end[0],end[1]])+'\n')
    group = oml1.edge_group[i] - 1
    k = oml1.group_k[group]
    m = oml1.group_m[group]
    file.write(str(k)+' ')
    file.write(str(m)+'\n')
    print k,m, group
    print oml1.group_k,oml1.group_m,oml1.ngroup
    d = GeoMACH.extractd(group+1,oml1.ngroup,oml1.nD,k+m,oml1.group_k,oml1.group_m,oml1.group_d)
    for j in range(d.shape[0]):
        file.write(str(d[j])+' ')
    file.write('\n')
    C = GeoMACH.getsurfacep(surf+1, oml1.nC, ms[surf,0], ms[surf,1], oml1.nsurf, oml1.nedge, oml1.ngroup, oml1.nvert, oml1.surf_vert, oml1.surf_edge, oml1.edge_group, oml1.group_m, oml1.surf_index_C, oml1.edge_index_C, oml1.C)
    if edge0==0:
        if edge1==0:
            edgeCs = copy.copy(C[:,0,:])
        else:
            edgeCs = copy.copy(C[:,-1,:])
    else:
        if edge1==0:
            edgeCs = copy.copy(C[0,:,:])
        else:
            edgeCs = copy.copy(C[-1,:,:])
    if oml1.surf_edge[surf,edge0,edge1] < 0:
        edgeCs[:,:] = copy.copy(edgeCs[::-1,:])
    for j in range(edgeCs.shape[0]):
        file.write(str(edgeCs[j,0])+' ')
        file.write(str(edgeCs[j,1])+' ')
        file.write(str(edgeCs[j,2])+'\n')

for i in range(oml1.nsurf):
    for u in range(2):
        for v in range(2):
            file.write(str(oml1.surf_edge[i,u,v])+' ')
    file.write('\n')
    ugroup = oml1.edge_group[abs(oml1.surf_edge[i,0,0])-1] - 1
    vgroup = oml1.edge_group[abs(oml1.surf_edge[i,1,0])-1] - 1
    ku = oml1.group_k[ugroup]
    mu = oml1.group_m[ugroup]
    kv = oml1.group_k[vgroup]
    mv = oml1.group_m[vgroup]
    file.write(str(ku)+' ')
    file.write(str(mu)+' ')
    file.write(str(kv)+' ')
    file.write(str(mv)+' ')
    file.write('\n')    
    d = GeoMACH.extractd(ugroup+1,oml1.ngroup,oml1.nD,ku+mu,oml1.group_k,oml1.group_m,oml1.group_d)
    for j in range(d.shape[0]):
        file.write(str(d[j])+' ')
    file.write('\n') 
    d = GeoMACH.extractd(vgroup+1,oml1.ngroup,oml1.nD,kv+mv,oml1.group_k,oml1.group_m,oml1.group_d)
    for j in range(d.shape[0]):
        file.write(str(d[j])+' ')
    file.write('\n')
    C = GeoMACH.getsurfacep(i+1, oml1.nC, ms[i,0], ms[i,1], oml1.nsurf, oml1.nedge, oml1.ngroup, oml1.nvert, oml1.surf_vert, oml1.surf_edge, oml1.edge_group, oml1.group_m, oml1.surf_index_C, oml1.edge_index_C, oml1.C)
    for v in range(C.shape[1]):
        for u in range(C.shape[0]):
            file.write(str(C[u,v,0])+' ')
            file.write(str(C[u,v,1])+' ')
            file.write(str(C[u,v,2])+'\n')

file.close()
