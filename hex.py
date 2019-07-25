#!/usr/bin/python
'''
Created on Jan 30, 2010

@author: alcides
'''

import wx
from Minimax import *
from wx.lib.wordwrap import wordwrap
import wx.lib.sized_controls as sc
from red import *
import random

OK = 0
WIN = 1
LOSE = 2

BLANCO = 1
NEGRO = 2
minimaxscore = 0L
primero = False
juegoUsuario = False
servidor = False
miSocket = None
socketConectado = False
terminar = 0

b = Board()
bcopy = Board()
rcopy = Board()

class Hex(wx.Frame):
    
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(800, 565))
        
        self.CreateStatusBar()
        self.SetStatusText("Click en Juego --> Nuevo para empezar un juego...")
        self.SetBackgroundColour('white')

        menuBar = wx.MenuBar()
        juego = wx.Menu()
        submenuNuevo = wx.Menu()
        submenuNuevo.Append(1011, "&Usuario Vs. PC", "")
        submenuNuevo.Append(1012, "&PC Vs. PC", "")
        juego.AppendMenu(101, "&Nuevo", submenuNuevo)
        juego.Append(102, "&Salir\tCtrl+Q", "Salir del juego")
        menuBar.Append(juego, "&Juego")
        
        ayuda = wx.Menu()
        ayuda.Append(201, "&Acerca de", "")
        menuBar.Append(ayuda, "&Ayuda")

        self.SetMenuBar(menuBar)
        
        self.Bind(wx.EVT_MENU, self.MenuUserPc, id=1011)
        self.Bind(wx.EVT_MENU, self.MenuPcVsPc, id=1012)
        self.Bind(wx.EVT_MENU, self.CloseWindow, id=102)
        self.Bind(wx.EVT_MENU, self.MenuAyuda, id=201)
        self.Bind(wx.EVT_PAINT, self.DrawBoard)
        self.Bind(wx.EVT_LEFT_UP, self.onMouseUp)

        self.Centre()
        self.Show(True)
    
    
    def MenuUserPc(self, event):
        global juegoUsuario
        juegoUsuario = True
        self.newGame()
    
    
    def MenuPcVsPc(self, event):
        global juegoUsuario
        global servidor
        global operacion
        
        juegoUsuario = False
        operacion = self.msjElegir()
        
        if(operacion == ESCUCHAR):
            servidor = True
            self.prepararJuegoRed(operacion)
                                
        elif(operacion == CONECTAR):
            servidor = False
            self.prepararJuegoRed(operacion)
            
                
    def msjElegir(self):
        dlg = wx.MessageDialog(self, 'Desea ser servidor?', '',
                               wx.YES_NO | wx.YES_DEFAULT)
                
        if (dlg.ShowModal() == wx.ID_YES):
            si = 0
        else:
            si = 1
        
        self.Refresh()
        dlg.Destroy()
        return si
    
    
    def PCvsPC(self):
        global primero
        global servidor
        global miSocket
        global terminar
                
        #Se decide quien empieza
        if (servidor):
            n = random.randint(0, 1)
            primero = (n == 0)
            buff = str(n)
            miSocket.send(buff)
            print "enviado", buff
        else:
            buff = miSocket.recv(TAMBUFF)
            primero = (buff == "1")
            print "recibido", buff
        
        # Limpiamos las matrices
        for i in range(NUMROW):
            for j in range(NUMROW):
                b.negro[i][j] = False
                b.blanco[i][j] = False
        
        self.rePaintBoard()
        
        if (primero):
            b.negro[3][3] = True
            buff = "33"
            self.rePaintBoard()
            self.SetStatusText("Juega el oponente.")
            miSocket.send(buff)
            print "enviado", buff
            time.sleep(1)
            
        else:
            self.SetStatusText("Comienza el oponente. ")
        
        fin = self.status()
        print "fin:", fin
        
        
        # Ciclo donde analiza las jugadas
        while (True):
            
            buff = miSocket.recv(TAMBUFF)
            r = int(buff[:1])
            c = int(buff[1:])
            print "recibido", buff
            
            if(servidor):
                b.blanco[r][c] = True
            else:
                b.blanco[c][r] = True
            
            self.rePaintBoard()
            fin = self.status()
            
            # Juega como servidor
            if(servidor):
                if (fin == LOSE):
                    if(servidor):
                        self.mostrarMsj("Gano el oponente...")
                else:
                    self.SetStatusText("Pensando...")
                        
                    if (self.myMove()):
                        self.rePaintBoard()
                        self.SetStatusText("Es turno del oponente.")
                        fin = self.status()
                        
                        if(fin == WIN):
                            if(servidor):
                                self.mostrarMsj("Gane! :-)")
                    else:
                        self.SetStatusText("No se puede encontrar un movimiento valido.")
                    
            # Juega como cliente
            else:
                if(fin == LOSE):
                    self.mostrarMsj("Gano el oponente...")
                else:
                    self.SetStatusText("Pensando...") 
                    if (self.myMove()):
                        self.rePaintBoard()
                        self.SetStatusText("Es turno del oponente.")
                        fin = self.status()
                        
                        if(fin == WIN):
                            self.mostrarMsj("Gane! :-) Fin del juego")
                    else:
                        self.SetStatusText("No se puede encontrar un movimiento valido.")

            if( fin == LOSE or fin == WIN):
                break
                
        self.SetStatusText("Termino el juego.")
    
    
    # Creamos el Socket como Servidor u Cliente
    def prepararJuegoRed(self, op):
        global socketConectado
        global miSocket
        
        self.SetStatusText("Esperando contrincante...")
        
        # Creamos el socket
        try:
            s = socket.socket()
        except socket.error, msg:
            socketConectado = False
            print "No se pudo crear el socket:", msg
        else:
            socketConectado = True
            print "Socket creado exitosamente"
        
        # Si es servidor
        if (operacion == ESCUCHAR):
            try:
                s.bind((HOST, PUERTO))
                s.listen(1)
            except socket.error, msg:
                print "Error al escuchar o asociar:", msg
                s.close()
                s = None
                                            
            miSocket, addr = s.accept()
                                
        # Si es cliente
        else:
            try:
                s.connect((HOST, PUERTO))
                miSocket = s
            except socket.error, msg:
                print "Error al conectar el socket:", msg
                s.close()
                s = None
                
        self.PCvsPC()
        miSocket.close()
        s.close()
        miSocket = None
        s = None
        print "socket cerrado"
        
                
    def CloseWindow(self, event):
        self.Close()
        
        
    def MenuAyuda(self, event):
        info = wx.AboutDialogInfo()
        info.Name = "Hex Game"
        info.Version = "0.1"
        info.Copyright = "(C) 2009- 2010"
        info.Description = wordwrap(
            "Este juego fue desarrollado como trabajo de laboratorio de la "
            "materia "
            "\n\nEstructura de los Lenguajes",
            350, wx.ClientDC(self))
        info.Developers = [ "Romina Fernandez",
                            "Julia Talavera",
                            "Alcides Rivarola" ]
        wx.AboutBox(info)
        
        
    def popUpGanaste(self):
        global primero
        dlg = wx.MessageDialog(self, 'Desea continuar jugando?', 'Ganaste!',
                               wx.YES_NO | wx.YES_DEFAULT)
                
        if (dlg.ShowModal() == wx.ID_YES):
            primero = True
        else:
            primero = False
        
        dlg.Destroy()
        
        
    def popUpPerdiste(self):
        global primero
        dlg = wx.MessageDialog(self, 'Desea continuar jugando?', 'Perdiste!',
                               wx.YES_NO | wx.NO_DEFAULT)
        dlg.ShowModal()
        primero = False
        dlg.Destroy()
        
    def mostrarMsj(self, msj):
        dlg = wx.MessageDialog(self, msj, '', wx.OK)
        dlg.ShowModal()
        dlg.Destroy()     
                
    def newGame(self):
        
        self.Refresh()
        #self.Bind(wx.EVT_PAINT, self.DrawBoard)
        
        for i in range(NUMROW):
            for j in range(NUMROW):
                b.negro[i][j] = False
                b.blanco[i][j] = False
                b.distance[i][j] = -1
                b.vdist[i][j] = -1
        b.spreadsuccess = False
        b.SouthPole = 0
        
        if (primero and juegoUsuario):
            b.negro[3][3] = True
            self.SetStatusText("Es tu turno")
        else:
            self.SetStatusText("Haz click en una celda para empezar")
        
        self.rePaintBoard()
        
        
    def DrawBoard (self, event):
        dc = wx.PaintDC (self)
        
        dc.SetPen(wx.Pen('gray'))
        dc.SetBrush(wx.Brush('gray'))
        dc.DrawRoundedRectangle(0, 0, X0, 256, 50)
        dc.DrawRoundedRectangle(X0, 256, X0, 256, 50)
        
        # color del tablero
        dc.SetPen(wx.Pen('#ffd700'))
        #dc.SetPen(wx.Pen('white'))
        x = XINICIAL
        y = YINICIAL

        for i in range(NUMROW):
            for j in range(NUMROW):
                x = x + DISTCENTROX
                y = y + AP
                dc.SetBrush(wx.Brush('#FEFF99'))
                #dc.SetBrush(wx.Brush('#87cefa'))
                dc.DrawPolygon (((x, y), (x+XH , y), (x+XH+XV, y+AP),
                                (x+XH, y+2*AP), (x, y+2*AP), (x-XV, y+AP)))
                
            x = XINICIAL - (i*DISTCENTROX)
            y = YINICIAL + (i*AP)
            x = x - DISTCENTROX
            y = y + AP
    
    
    def MNtoXY(self, color, i, j):
        c = Punto()
        c.X = X0 + DISTCENTROX*j - DISTCENTROX*i
        c.Y = Y0 + AP*i + AP*j
        
        self.dibujarFichas(c, AP-10, color)
    
    
    def dibujarFichas (self, centro, radio, color = 2):
        dc = wx.PaintDC (self)
    
        if color == 1:
            dc.SetPen(wx.Pen('#ffd520'))
            dc.SetBrush(wx.Brush('white'))
        elif color == 2:
            dc.SetPen(wx.Pen('gray'))
            dc.SetBrush(wx.Brush('gray'))
         
        dc.DrawCircle (centro.X, centro.Y, radio)


    def onMouseUp(self, event):
        global primero
        
        c = Punto()
        c.X, c.Y = event.GetPosition()
        self.SetStatusText("")
        
        if(self.status() == WIN or self.status() == LOSE):
            self.newGame()
            return  
        
        p, c = obtenerCentro(c)
        
        if ((c.X != -1) and (c.Y != -1)):
            if ( (b.blanco[c.X][c.Y] != True) and (b.negro[c.X][c.Y] != True)):
                b.blanco[c.X][c.Y] = True
                self.rePaintBoard()
                
                if(self.status() == LOSE):
                    
                    self.popUpGanaste()
                    self.SetStatusText("Click para dar inicio al juego")
                    #self.SetStatusText("Ganaste! Click para otro juego")
                    primero = True
                else:
                    self.SetStatusText("Pensando...")
                    if(self.myMove()):
                        self.rePaintBoard()
                        self.SetStatusText("Es tu turno")
                        
                        if(self.status() == WIN):
                            self.popUpPerdiste()
                            self.SetStatusText("Click para empezar el juego")
                            #self.SetStatusText("Lo siento, pero perdiste!")
                            primero = False
                    else:
                        self.SetStatusText("Error inesperado del sistema, \
                                            favor, reinicie el juego")
            else:
                self.SetStatusText("Celda ya seleccionada")
        else:
            self.SetStatusText("Ninguna celda seleccionada") 
    
        
    def isWonNegro(self):
        t = Board()
        t.Copy(b)
        
        for i in range(NUMROW):
            if (t.negro[i][0] == True and t.distance[i][0] == -1):
                t.Connect(i, 0, 0)
                
        for i in range(NUMROW):
            if (t.distance[i][NUMROW-1] == 0):
                return True
        return False
    
    
    def isWonBlanco(self):
        t = Board()
        t.Reflect(b)
        
        for i in range(NUMROW):
            if (t.negro[i][0] == True and t.distance[i][0] == -1):
                t.Connect(i,0,0)
                
        for i in range(NUMROW):    
            if (t.distance[i][7-1]==0):
                return True
        return False
    
    
    def rePaintBoard(self):
        
        b.Evaluate()
        
        for i in range(NUMROW):
            for j in range(NUMROW):
                
                if(not(juegoUsuario) and not(servidor)):
                    if(b.negro[i][j] == True):
                        self.MNtoXY(BLANCO, j, i)
                    if(b.blanco[i][j] == True):
                        self.MNtoXY(NEGRO, j, i)    
                else:
                    if(b.negro[i][j] == True):
                        self.MNtoXY(NEGRO, i, j)
                    if(b.blanco[i][j] == True):
                        self.MNtoXY(BLANCO, i, j)
        
                    
    def myMove(self):
        
        mt = Move()
        MinimaxAlphaBeta(b, 0 , mt, MINUS_INFINITY, PLUS_INFINITY)
        
        if (mt.x != -1):           
            b.negro[mt.x][mt.y] = True
            
            if(juegoUsuario or not(juegoUsuario) and (servidor)):
                if((not(juegoUsuario) and socketConectado)):
                
                    buff = str(mt.x)+str(mt.y)
                    miSocket.send(buff)
                    print "enviado my move", buff
                    time.sleep(2)
                self.MNtoXY(NEGRO, mt.x, mt.y)
            else:
                if(socketConectado):
                    buff = str(mt.y)+str(mt.x)
                    miSocket.send(buff)
                    print "enviado my move", buff
                    time.sleep(2)
                self.MNtoXY(BLANCO, mt.y, mt.x)
                
            self.rePaintBoard()
            minimaxscore = mt.score
            return True
        
        for i in range(NUMROW):
            for j in range(NUMROW):
                if (b.negro[i][j] != True and b.blanco[i][j] != True):
                    if(juegoUsuario or not(juegoUsuario) and servidor):
                        b.negro[i][j] = True
                        self.MNtoXY(NEGRO, i, j)
                        self.rePaintBoard()
                        self.SetStatusText("Jugada random")
                    else:
                        b.blanco[j][i] = True
                        self.MNtoXY(BLANCO, j, i)
                        self.rePaintBoard()
                        self.SetStatusText("Jugada random")
                    return True
        return False
    
    
    def status(self):
        if self.isWonNegro():
            return WIN
        if self.isWonBlanco():
            return LOSE
        return OK
    

app = wx.App(0)
Hex(None, -1, '')
app.MainLoop()
