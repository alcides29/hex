'''
Created on Jan 17, 2010

@author: alcides
'''

import time


NUMROW = 7
GUARANTEED_WIN = 10000000L
IMMEDIATE_WIN = 1000000000L
COPY = 1
REFLECT = 2
UNSET = (NUMROW*NUMROW + 1)
        
class Board:
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.blanco = []
        self.negro = []
        self.distance = []
        
        # number of balls needed taking into account guaranteed connections.
        self.vdist = []  
        self.spreadsuccess = False
        self.SouthPole = 0
        
        for i in range(NUMROW):
            self.blanco.append([])
            self.negro.append([])
            self.distance.append([])
            self.vdist.append([])
            for j in range(NUMROW):
                self.blanco[i].append([False])
                self.negro[i].append([False])
                self.distance[i].append([-1])
                self.vdist[i].append([-1])
            
    
    def Board1(self, original, action):
        if (action == REFLECT):
            self.Reflect(original)
        if (action == COPY):
            self.Copy(original)
    
    def Copy(self, original):
        for i in range(NUMROW):
            for j in range(NUMROW):
                self.negro[i][j] = original.negro[i][j]
                self.blanco[i][j] = original.blanco[i][j]
                self.distance[i][j] = -1
    
    def Reflect(self, original):
        for i in range(NUMROW):
            for j in range(NUMROW):
                self.negro[i][j] = original.blanco[j][i]
                self.blanco[i][j] = original.negro[j][i]
                self.distance[i][j] = -1
    
    def Connect(self, m, n, value):
        if(self.negro[m][n] == True) and (self.distance[m][n] == -1):
            self.distance[m][n] = value
            if (m > 0):
                self.Connect(m-1, n, value)
                if (n>0):
                    self.Connect(m-1, n-1, value)
            if (n>0):
                self.Connect( m, n-1, value)
            if (n < NUMROW-1):
                self.Connect( m, n+1, value)
                if (m<NUMROW-1):
                    self.Connect( m+1, n+1, value )
            if (m<NUMROW-1):
                self.Connect(m+1, n, value )
                
    def TestConnect(self, m, n, value):
        if (self.distance[m][n] == -1 and self.negro[m][n] == True):
            self.Connect(m, n, value)
    
    def TestSpread(self, m, n, value):
        if ( (self.distance[m][n] == -1) and self.blanco[m][n] != True):
            self.distance[m][n] = value + 1
            self.spreadsuccess = True
            
    def Spread(self, value):
        for m in range(NUMROW):
            for n in range(NUMROW):
                if (self.distance[m][n] == value):
                    if (m>0):
                        self.TestConnect(m-1, n, value)
                        if (n>0):
                            self.TestConnect(m-1,n-1,value)
                    if (n>0):
                        self.TestConnect(m,n-1,value)
                    if (n < NUMROW-1):
                        self.TestConnect(m,n+1,value)
                        if (m<NUMROW-1):
                            self.TestConnect(m+1,n+1,value)
                    if (m<NUMROW-1):
                        self.TestConnect(m+1,n,value)
        
        #see if we have reached the end row
        for m in range(NUMROW):
            if (self.distance[m][NUMROW-1] != -1):
                return
        
        self.spreadsuccess = False
        for m in range(NUMROW):
            for n in range(NUMROW):
                if (self.distance[m][n] == value):
                    if (m>0):
                        self.TestSpread(m-1,n,value)
                        if (n>0):
                            self.TestSpread(m-1,n-1,value)
                    if (n>0):
                        self.TestSpread(m,n-1,value)
                    if (n<NUMROW-1):
                        self.TestSpread(m,n+1,value)
                        if (m<NUMROW-1):
                            self.TestSpread(m+1,n+1,value)
                    if (m<NUMROW-1):
                        self.TestSpread(m+1,n,value)


    def TwoBridgeTest(self, m, n, value):
        if (value<0):
            return False
        if (m>0 and n>1):
            if (self.blanco[m-1][n-1] != True and self.blanco[m][n-1] != True
                and (self.vdist[m-1][n-2] == value) and self.negro[m-1][n-2] == True):
                return True
        if (m>1 and n>0):
            if (self.blanco[m-1][n-1] != True and self.blanco[m-1][n] != True
                and (self.vdist[m-2][n-1] == value) and self.negro[m-2][n-1] == True):
                return True
        if (m>0 and n<NUMROW-1):
            if (self.blanco[m-1][n] != True and self.blanco[m][n+1] != True
                and (self.vdist[m-1][n+1] == value) and self.negro[m-1][n+1] == True):
                return True
        if (m<NUMROW-1 and n<NUMROW-2):
            if (self.blanco[m+1][n+1] != True and self.blanco[m][n+1] != True
                and (self.vdist[m+1][n+2] == value) and self.negro[m+1][n+2] == True):
                return True
        if (m<NUMROW-2 and n<NUMROW-1):
            if (self.blanco[m+1][n+1] != True and self.blanco[m+1][n] != True
                and (self.vdist[m+2][n+1] == value) and self.negro[m+2][n+1] == True):
                return True
        if (m<NUMROW-1 and n>0):
            if (self.blanco[m+1][n] != True and self.blanco[m][n-1] != True
                 and (self.vdist[m+1][n-1] == value) and self.negro[m+1][n-1] == True):
                return True
        return False
    
    
    def PropagateVdist(self, m, n, value):
        
        if (self.vdist[m][n]<=value):
            return
        self.vdist[m][n]=value
    
        if (n == NUMROW-1 and self.SouthPole > value):
            self.SouthPole = value
            return
        if (n==NUMROW-2 and self.SouthPole > value and m<NUMROW-2):
            if (self.negro[m][n] == True and self.blanco[m][NUMROW-1] != True
                and self.blanco[m+1][NUMROW-1] != True):
                self.SouthPole=value
                return    
        if (n<NUMROW-1):
            if (m<NUMROW-1):
                self.TestPropagateVdist(m+1,n+1,value)
            self.TestPropagateVdist(m,n+1,value)
        if (m<NUMROW-1):
            self.TestPropagateVdist(m+1,n,value)
        if (m>0):
            self.TestPropagateVdist(m-1,n,value)
            if (n>0):
                self.TestPropagateVdist(m-1,n-1,value)
        if (n>0):
            self.TestPropagateVdist(m,n-1,value)
    
    
    def TestPropagateVdist(self, m, n, value):
        if (self.negro[m][n] == True):
            self.PropagateVdist(m,n,value)
        elif (self.blanco[m][n] != True):
            self.PropagateVdist(m,n,value+1)
    
    
    def Vtest(self, m, n, value):
        if (value<0):
            return False
    
        if (n>0):
            if (self.blanco[m][n-1] != True):
                if (self.vdist[m][n-1]==value):
                    return True
        if (m>0):
            if (n>0):
                if (self.blanco[m-1][n-1] != True):
                    if (self.vdist[m-1][n-1] == value):
                        return True
            if (self.blanco[m-1][n] != True):
                if (self.vdist[m-1][n]==value):
                    return True
        if (n<NUMROW-1):
            if (self.blanco[m][n+1] != True):
                if (self.vdist[m][n+1]==value):
                    return True
            if (m<NUMROW-1):
                if (self.blanco[m+1][n+1] != True):
                    if (self.vdist[m+1][n+1]==value):
                        return True
        if (m<NUMROW-1):
            if (self.blanco[m+1][n] != True):
                if (self.vdist[m+1][n]==value):
                    return True
        return False
        
    def Vspread(self, m, n, value):
        if ((self.vdist[m][n]==value) != True):
            return
        nextvalue = value+1
        if (n>0):
            if (self.blanco[m][n-1] != True):
                if (self.vdist[m][n-1]>nextvalue):
                    self.vdist[m][n-1]=nextvalue
        if (m>0):
            if (n>0):
                if (self.blanco[m-1][n-1] != True):
                    if (self.vdist[m-1][n-1]>nextvalue):
                        self.vdist[m-1][n-1]=nextvalue
            if (self.blanco[m-1][n] != True):
                if (self.vdist[m-1][n]>nextvalue):
                    self.vdist[m-1][n]=nextvalue
        if (n<NUMROW-1):
            if (self.blanco[m][n+1] != True):
                if (self.vdist[m][n+1]>nextvalue):
                    self.vdist[m][n+1]=nextvalue
            if (m<NUMROW-1):
                if (self.blanco[m+1][n+1] != True):
                    if (self.vdist[m+1][n+1]>nextvalue):
                        self.vdist[m+1][n+1]=nextvalue
        if (m<NUMROW-1):
            if (self.blanco[m+1][n] != True):
                if (self.vdist[m+1][n]>nextvalue):
                    self.vdist[m+1][n]=nextvalue
                    
    #/*---------------------------------------------------------------------------*/
    def Vassign(self, n):
        
        
        if (n > 0):
            i = NUMROW - 1
            while( i >= 0 and self.SouthPole == UNSET):
                j = NUMROW - 1
                while(j >= 0 and self.SouthPole == UNSET):
                    self.Vspread(i, j, n-1)
                    j = j -1
                i = i -1
        #print "n:", n
        #time.sleep(0.5)
        more=True
        while (more == True):
            more = False
            i = NUMROW - 1
            #print 'southpole', self.SouthPole
            while( i >= 0 and self.SouthPole == UNSET):
                j = NUMROW - 1
                while(j >= 0 and self.SouthPole == UNSET):
                    
                    #if n == 50:
                    #    print 'vdist', self.vdist[i][j], 'n', n
                    #time.sleep(1)
                    
                    if (self.vdist[i][j]>n):
                        #print 'negro', self.negro[i][j]
                        if (self.negro[i][j] == True):
                            doit=True
                            if (self.Vtest(i,j,n) != True ):
                                #print 'estamos aqui'
                                if (self.TwoBridgeTest(i,j,n) != True ):
                                    doit=False
                            if (doit == True):
                                self.vdist[i][j]=n
                                if (j==(NUMROW-1)):
                                    self.SouthPole=n
                                    #print "n1", n, "SouthPole", self.SouthPole
                                if (j==(NUMROW-2) and i<NUMROW-1):
                                    if(self.blanco[i][NUMROW-1] != True and self.blanco[i+1][NUMROW-1] != True):
                                        self.SouthPole=n
                                        #print "n2", n, "SouthPole", self.SouthPole
                                more=True
                    j = j -1
                i = i -1
            #print 'more', more
            
        #print 'check for 2-connected cells on bottom edge'
        for i in range(NUMROW-1):
            if (self.negro[i][NUMROW-2] == True and self.vdist[i][NUMROW-2]==n and self.blanco[i][NUMROW-1] != True and self.blanco[i+1][NUMROW-1] != True):
                self.SouthPole = n
                #print "n3", n, "SouthPole", self.SouthPole
 
        #print 'check for 3-connected cells on bottom edge'
        zrow = NUMROW-3
        if (NUMROW>=4):
            for i in range(NUMROW-3):
                if (self.negro[i][zrow] == True and self.vdist[i][zrow]==n and
                    ( ( self.blanco[i+1][zrow] != True and self.blanco[i+2][zrow+1] != True and self.blanco[i+3][zrow+2] != True ) or self.negro[i][zrow+2] == True or self.negro[i+2][zrow+2] == True)
                    and self.blanco[i][zrow+1] != True and self.blanco[i+1][zrow+1] != True
                    and self.blanco[i][zrow+2] != True and self.blanco[i+1][zrow+2] != True and self.blanco[i+2][zrow+2] != True):
                    self.SouthPole = n
                    #print "n4", n, "SouthPole", self.SouthPole
        
        if (NUMROW>=4):
            for i in range(1, NUMROW-2):
                if (self.negro[i][zrow] == True and self.vdist[i][zrow]==n
                    and ( (self.blanco[i-1][zrow] != True and self.blanco[i-1][zrow+1] != True and self.blanco[i-1][zrow+2] != True) or self.negro[i][zrow+2] == True or self.negro[i+2][zrow+2] == True )
                    and self.blanco[i][zrow+1] != True and self.blanco[i+1][zrow+1] != True
                    and self.blanco[i][zrow+2] != True and self.blanco[i+1][zrow+2] != True and self.blanco[i+2][zrow+2] != True):
                    self.SouthPole = n
                    #print "n6", n, "SouthPole", self.SouthPole
                    
        #print 'check for 4-connected cells on bottom edge'
        zrow = NUMROW-4
        if (NUMROW>=7):
            for i in range(2, NUMROW-4):
                if(self.negro[i][zrow] == True and self.vdist[i][zrow]==n and  self.blanco[i-1][zrow] != True
                   and self.blanco[i-2][zrow+1] != True and self.blanco[i-1][zrow+1] != True and self.blanco[i][zrow+1] != True and self.blanco[i+1][zrow+1] != True and self.blanco[i+2][zrow+1] != True
                   and self.blanco[i-2][zrow+2] != True and self.blanco[i-1][zrow+2] != True and self.blanco[i][zrow+2] != True and self.blanco[i+1][zrow+2] != True and self.blanco[i+2][zrow+2] != True and self.blanco[i+3][zrow+2] != True
                   and self.blanco[i-2][zrow+3] != True and self.blanco[i-1][zrow+3] != True and self.blanco[i][zrow+3] != True and self.blanco[i+1][zrow+3] != True and self.blanco[i+2][zrow+3] != True and self.blanco[i+3][zrow+3] != True and self.blanco[i+4][zrow+3] != True):
                    self.SouthPole = n
                    #print "n8", n, "SouthPole", self.SouthPole
            
        #print "n:", n, "SouthPole:", self.SouthPole
        
        if (self.SouthPole==UNSET):
            #for i in range(NUMROW-1, -1, -1):
            i = NUMROW - 1
            while(i >=0):
                if (self.vdist[i][NUMROW-1] < self.SouthPole):
                    self.SouthPole = self.vdist[i][NUMROW-1]
                    #print 'southpole = vdist', self.SouthPole
                i = i - 1 
    #/*---------------------------------------------------------------------------*/
    def Reached(self):
        reached = False
        for i in range(NUMROW):
            if(self.distance[i][NUMROW-1] != -1):
                reached= True
        return reached                    

    #/*---------------------------------------------------------------------------*/
        
    
    def Evaluate(self):
        dis_start = 1 # starting value to calculate vdist
        self.SouthPole = UNSET
        n = 0
        
        for i in range(NUMROW):
            for j in range(NUMROW):
                self.distance[i][j] = -1
                self.vdist[i][j] = UNSET
    
        for i in range(NUMROW):
            #print"evaluate negro i 0:", self.negro[i][0]
            if (self.negro[i][0] == True):
                self.Connect(i, 0, 0)
                self.vdist[i][0] = 0
                dis_start = 0
                #print "aqui eval"
            elif(self.blanco[i][0] != True):
                self.distance[i][0] = 1
                self.vdist[i][0] = 1
        
        # check for 2-connected cells on top edge
        for i in range(1, NUMROW):
            #print "negro:", self.negro[i][1], "!blanco:", self.blanco[i][0], "!blanco", self.blanco[i-1][0] 
            if ((self.negro[i][1] == True) and (self.blanco[i][0] != True)
                and (self.blanco[i-1][0] != True)):
                self.vdist[i][1]=0
                #print "2-connected cells"
                dis_start=0
    
        # check for 3-connected cells on top edge
        for i in range(2, NUMROW-1):
            if (self.negro[i][2] == True and ((self.blanco[i+1][2] == True
                                       and self.blanco[i+1][1] != True
                                       and self.blanco[i+1][0] != True)
            or self.negro[i-2][0] == True or self.negro[i][0] == True)
            and self.blanco[i][1] != True and self.blanco[i-1][1] != True
            and self.blanco[i-2][0]  != True and self.blanco[i-1][0]  != True
            and self.blanco[i][0] != True):
                self.vdist[i][2]=0
                dis_start=0
                #print "3-connected cells"
        
        #print "vamos bien"
        for i in range(3, NUMROW):
            if (self.negro[i][2] == True and ((self.blanco[i-1][2] != True
                                       and self.blanco[i-2][1] != True
                                       and self.blanco[i-3][0] != True)
            or self.negro[i-2][0] == True or self.negro[i][0] == True)
            and self.blanco[i-1][1] != True and self.blanco[i][1] != True 
            and self.blanco[i-2][0] != True and self.blanco[i-1][0] != True
            and self.blanco[i][0] != True):
                self.vdist[i][2]=0
                dis_start=0
    
        #check for 4-connected cells on top edge
        for i in range(4, NUMROW-2):
            if (self.negro[i][3] == True and self.blanco[i+1][3] != True
                and self.blanco[i-2][2] != True and self.blanco[i-1][2] != True
                and self.blanco[i][2] != True and self.blanco[i+1][2] != True
                and self.blanco[i+2][2] != True and self.blanco[i-3][1] != True
                and self.blanco[i-2][1] != True and self.blanco[i-1][1] != True
                and self.blanco[i][1] != True and self.blanco[i+1][1] != True
                and self.blanco[i+2][1] != True and self.blanco[i-4][0] != True
                and self.blanco[i-3][0] != True and self.blanco[i-2][0] != True
                and self.blanco[i-1][0] != True and self.blanco[i][0] != True
                and self.blanco[i+1][0] != True and self.blanco[i+2][0] != True):
                self.vdist[i][3]=0
                dis_start=0
        
        self.spreadsuccess = True
        
        #print "!Reached:", self.Reached(), "spreadsuccess:", self.spreadsuccess
        while ((self.Reached() != True) and (self.spreadsuccess == True)):
            self.Spread(n)
            if (n==0):
                self.spreadsuccess=True
            n = n + 1
        
        #print"if Reached", self.Reached()
        if self.Reached() == True:
            self.SouthPole=UNSET
            
            while (self.SouthPole == UNSET):
                #print "dis_start", dis_start
                self.Vassign(dis_start)
                dis_start = dis_start + 1
                #if dis_start > 50:
                #    break
                #print "southpole after:", self.SouthPole
        
        #print "completamos el evaluate"

    #/*---------------------------------------------------------------------------*/
    
    def CellsToHome(self):
        score = NUMROW*NUMROW + 1
        for i in range(NUMROW):
            if (self.distance[i][NUMROW-1] != -1
                and self.distance[i][NUMROW-1] < score):
                score = self.distance[i][NUMROW-1] 
        
        return score

    # /*---------------------------------------------------------------------------*/
    
    def Score(self):
        h = self.CellsToHome()
        if h == 0:
            score = IMMEDIATE_WIN
        else:
            if self.SouthPole == 0:
                score = GUARANTEED_WIN*10 - 100*h
            else:
                score = -100000*self.SouthPole -1000*h 
        return score