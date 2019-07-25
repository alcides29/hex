

AP = 30
XINICIAL = 328
YINICIAL = 16 #50
XH = 36
XV = 18
DISTCENTROX = XH + XV
X0 = 400
Y0 = 76 #110


def obtenerCentro(c):
    
    punto = Punto()
    mn = Punto()
    x = c.X
    y = c.Y
    centroX = XINICIAL + XV + DISTCENTROX
    centroY = YINICIAL + 2*AP
    
    for i in range(7):
        for j in range (7):        
    
            centroX = X0 + DISTCENTROX*j - DISTCENTROX*i
            centroY = Y0 + AP*i + AP*j
            if( (x*x + y*y - 2*centroX*x - 2*centroY*y +
                centroX*centroX + centroY*centroY) < (AP*AP)):
                # coordenadas en pixeles
                punto.X = centroX
                punto.Y = centroY
                # coordenadas en m n
                mn.X = i
                mn.Y = j
                #print "Entro en la posicion: ", punto.X, punto.Y                    
    return punto, mn


class Punto:
    X = -1
    Y = -1