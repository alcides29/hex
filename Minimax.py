'''
Created on Jan 20, 2010

@author: alcides
'''

from Board import *
from Move import *
from App import *


MAXLEVEL = 1
PLUS_INFINITY = (1L<<63)-1L  #9223372036854775807
MINUS_INFINITY = -(1L<<63)  #9223372036854775808


def MinimaxAlphaBeta(b, level, m, alpha, beta):
    # decide whether we are maximising or minimising, depending on whether
    # the level is even or odd
    maximising = ((level/2)*2 == level)
    #print "maximising:", maximising
    
    b.Evaluate()
    r = Board()
    r.Reflect(b)
    r.Evaluate()
    m.score =  b.Score() - 2*r.Score()
    #print "estoy aqui :-)"
    
    if ( (level == MAXLEVEL) or (m.score >= IMMEDIATE_WIN)):
        #print "casi maximizing"
        if (maximising):
            # We are calculating the opponent's score. Reverse the score
            m.score = -m.score
        else:
            # express a preference for moves that get you there quickest
            m.score = m.score - level
    else:  # carry on for another level
        m.x=-1
        m.y=-1
                
        bb = Board()
        alphaN = alpha
        betaN = beta
        
        if (level>0):
            bb.Reflect(b)
        else:
            bb.Copy(b)
        
        
        mm = Move()
        i = 0
        while(i<NUMROW and (alphaN < betaN)):
            j = 0
            while(j<NUMROW and (alphaN < betaN)):
                #print"negro", bb.negro[i][j], "blanco", bb.blanco[i][j]
                if((bb.negro[i][j] != True) and (bb.blanco[i][j] != True)):
                    bb.negro[i][j]= True
                        
                    
                    #print "Entra en otro nivel alpha beta"
                    MinimaxAlphaBeta(bb, level+1, mm, alphaN, betaN)
                    #print "aqui 2"
                    if (maximising):
                        if (mm.score>alphaN):
                            alphaN = mm.score
                            m.x  = i
                            m.y  = j
                    else:
                        if (mm.score<betaN):
                            m.x=i
                            m.y=j
                            betaN = mm.score
                    bb.negro[i][j] = False
                j = j +1
            i = i + 1
        
        if (maximising):
            m.score = alphaN
            #print "estoy aqui :-)"
        else:
            
            m.score = betaN