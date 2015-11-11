#!/usr/bin/env python2

import random
from multiprocessing import Pool
from collections import defaultdict
import numpy as np
import sys

class qPt:
    def __init__(self,q1,q2,q3,q,s,qt,m,n,u,num_gens):
        self.q1 = q1
        self.q2 = q2
        self.q3 = q3
        self.q = q
        self.s = s
        self.qt = qt
        self.m = m
        self.n = n
        self.u = u
        self.num_gens = num_gens

def qj(q,s):       #this is selection
    n = s*(q**2)+q
    d = s*(q**2)+1
    return float(n)/float(d)

def qa(qj,qt,m):    #this is immigration - really qj2
    return float(qj-qj*m+qt*m)

def qa_drift(qa,n):     #this is juv->adult; binomial due to infinite number of juvs   
    newblind=np.random.binomial(n, qa)
                      
    return float(newblind)/n
                  
def qpr(qa,u):
    return float(qa+u-u*qa)
 
def gen(q,s,qt,m,n,u):
    juv=qj(q,s)      #freq after selection
    juv2=qa(juv,qt,m)   #freq after immigration (still juv fish)
    adultD=qa_drift(juv2,2*n)    #freq after drift (adults about to reproduce); 2n = num alleles
    offsp = qpr(adultD,u)   #freq after reproduction (new juvs)

    return offsp

def multi_gen(q,s,qt,m,n,u,num_gens):
    for i in range(num_gens):
        q = gen(q,s,qt,m,n,u)
        if i == num_gens/4:
            q1 = q
        if i == num_gens/2:
            q2 = q
        if i == num_gens*3/4:
            q3 = q
    
    return qPt(q1,q2,q3,q,s,qt,m,n,u,num_gens)

def product_helper(args):
    return multi_gen(*args)
   
if __name__ == '__main__':
    nreps=100
    s=[]
    poss_s = [10**i for i in list(np.arange(-6,2.05,0.05))]
    poss_m = [10**i for i in list(np.arange(-8.0,0.05,0.05))]
    m=poss_m*nreps*len(poss_s)
    for ps in poss_s:
        s+=[ps]*nreps*len(poss_m)

    q = [0.01]*len(s)
    qt = [0.01]*len(s)
    n = [1000]*len(s)
    u = [0.000001]*len(s)
    num_gens = [10000]*len(s)    
        
    p = Pool(int(sys.argv[1])) 
    # make tuples of args
    job_args = [(item_q, s[i],qt[i],m[i],n[i],u[i],num_gens[i]) for i, item_q in enumerate(q)] 
    # map to pool
    sim = p.map(product_helper, job_args)

    outfile = open('drift_sims.csv','w')
    
    for p,v in vars(sim[0]).iteritems():
        outfile.write(str(p)+',')
    outfile.write("\n")
    for j in sim:
        for p,v in vars(j).iteritems():
            outfile.write(str(v)+',')
        outfile.write("\n")
    outfile.close()