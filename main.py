import json, pygame, time, random
from pygame import Vector2 as v2
from pygame.locals import *
# Cores
blue = (0, 0, 255)
yellow = (255, 255, 0)
red = (255, 0, 0)
purple = (160, 32, 240)
pink = (255, 192, 203)
black = (0, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)
gray = (200, 200, 200)
# Coordenadas Base
centro = (-22.5106172, -44.070486)
nafil = (-22.5000163,-44.1074262)
pontoMin = pygame.math.Vector2(centro)-pygame.math.Vector2(0.1, 0.1)
pontoMax = pygame.math.Vector2(centro)+pygame.math.Vector2(0.1, 0.1)

def ArquivoJson():
    with open('venv/Data/Pontos.json',  'r', encoding='utf8') as s:
        return json.load(s)

def ConvertGeoPixel(geo, mapSize):
    def LerpPos(num, min, max):
        temp = (num - min) / (max - min)
        return temp
    x = LerpPos(geo[1], pontoMin[1], pontoMax[1])
    y = 1 - LerpPos(geo[0], pontoMin[0], pontoMax[0])
    posX = mapSize[0] * x
    posY = mapSize[1] * y
    return (posX, posY)

class Tempo:
    def Remains(self, seconds):
        t = None
        h = seconds // 3600
        m = seconds % 3600 // 60
        s = seconds % 60
        if seconds >= 3600:
            t = f'{h}h{m}m{s}s'
        elif seconds >= 60:
            t = f'{m}m{s}s'
        else:
            t = t = f'{s}s'
        return t

    def Print(self, seconds, delay):
        hor = (seconds + delay) // 3600
        if hor < 10:
            hor = f'0{hor}'
        else:
            hor = f'{hor}'
        min = ((seconds + delay) % 3600 ) // 60
        if min < 10:
            min = f'0{min}'
        else:
            min = f'{min}'
        sec = (seconds + delay) % 60
        if sec < 10:
            sec = f'0{sec}'
        else:
            sec = f'{sec}'
        t = f'{hor}:{min}:{sec}'
        return t
    def Sec(self):
        hor = time.localtime().tm_hour * 3600
        min = time.localtime().tm_min * 60
        sec = time.localtime().tm_sec
        t = hor + min + sec
        return t


    # Classe para registros

class Registro:
    def __init__(self, id , mapaSize, arquivo ):
        self.arquivo = random.choice(arquivo)
        self.id = id
        self.geo = (self.arquivo['Geo'][0], self.arquivo['Geo'][1])
        self.bairro = self.arquivo['Bairro']
        self.zona = self.arquivo['Zona']
        self.pos = ConvertGeoPixel(self.geo, mapaSize)
        self.moto = '-'
        self.pedido = Tempo().Sec()
        self.saida = '-'
        self.previsao = '-'
        self.chegada = '-'
        self.status = 'Aguardando'
    def Dict(self):
        return {'id': self.id,
                'geo': self.geo,
                'bairro': self.bairro,
                'zona': self.zona,
                'pos': self.pos,
                'moto': self.moto,
                'pedido': self.pedido,
                'saida': self.saida,
                'previsão': self.previsao,
                'chegada': self.chegada,
                'status': self.status,}

class Moto:
    def __init__(self, name):
        self.name = name
        self.img = pygame.image.load(f'venv/Images/moto1.png')
        self.img = pygame.transform.scale(self.img, (30,30))
        self.rota = None
        self.indice = 0
        self.saida = 0
        self.proxima = 0
        self.chegada = 0
        self.pos = (0, 0)
        self.records = [[]]
    def Dict(self):
        return {'img': self.img, 'indice': self.indice, 'saida': self.saida, 'proxima': self.proxima,
            'chegada': self.chegada}

class Rota:
    def __init__(self, sales, first, zona):
        self.sales = sales
        self.first = first
        self.zona = zona
        self.moto = None
        self.status = 'aberto'

def Button( display, color, x, y, width, height, text='', fontSize=int):
    mouse = pygame.mouse.get_pos()
    # Outline
    pygame.draw.rect(display, 1, (x-2, y-2, width+4, height+4), 0)
    # Rect
    pygame.draw.rect(display, color, (x, y, width, height), 0)

    if text != '':
        font = pygame.font.SysFont('arial', fontSize)
        text = font.render(text, 1, (0, 0, 0))
        display.blit(text, (x + (width/2 - text.get_width()/2), y + (height/2 - text.get_height()/2)))

    if mouse[0] > x and mouse[0] < x + width:
        if mouse[1] > y and mouse[1] < y + height:
            return True
        return False

class App:
    # Global Variables
    windowWidth = 1200
    windowHeight = 800

    def __init__(self):
        self._running = True

    def on_init(self):
        pygame.init()
        pygame.font.init()
        self.gameDisplay = pygame.display.set_mode((self.windowWidth, self.windowHeight))
        pygame.display.set_caption('Simulador de Entregas')


        self.font = pygame.font.SysFont('arial', 32)
        self.fontMedium = pygame.font.SysFont('arial', 18)
        self.fontMediumBold = pygame.font.SysFont('arial', 18).bold
        self.fontSmall = pygame.font.SysFont('arial', 12)
        self.mapFile = pygame.image.load('venv/Images/mapa13.jpg').convert()
        self.mapScreen = pygame.transform.scale(self.mapFile,
                                                (int(self.mapFile.get_width() * 0.6), int(self.mapFile.get_height() * 0.6)))
        self.fps = 30
        self.mapPos = (-self.mapScreen.get_width()/2 + self.windowWidth/2, -self.mapScreen.get_height()/2 + self.windowHeight/2)
        self.lastRange = None
        self.currentRange = None

        self.report = False
        self.rectReport = [self.windowWidth*9/10, 600]
        self.reportPos = [self.windowWidth/20, self.windowHeight/20]
        self.currentReportPos = self.reportPos
        self.saleDelay = 0
        self.sales = []
        self.salesTables = [[]]
        self.indiceTab = 0
        self.arquivo = ArquivoJson()
        self._running = True

        self.baseImg = pygame.image.load('venv/Images/N.png').convert()
        self.baseImg = pygame.transform.scale(self.baseImg, (30, 30))
        self.basePos = ConvertGeoPixel(nafil, self.mapScreen.get_size())
        self.motos = []
        self.numMotos = 8
        for i in range(self.numMotos):
            self.motos.append(Moto(f'{i+1}'))

        self.routes = []
        self.limiteSaidas = 4

    def AjusteRota(self, list):
        listaNova = [self.sales[0].id]
        order = list[1:-1]
        while len(order) > 0:
            temp_list = []
            for s in range(len(order)):
                a = self.sales[listaNova[-1]].pos
                b = self.sales[order[s]].pos
                dist = pow(pow(a[0] - b[0], 2) + pow(a[1] - b[1], 2), 1 / 2)
                new = (round(dist, 2), s)
                temp_list.append(new)
            temp_list.sort()
            listaNova.append(order[temp_list[0][1]])
            order.pop(temp_list[0][1])
        listaNova.append(self.sales[0].id)
        return listaNova

    def on_event(self, event):
        if event.type == QUIT:
            self._running = False

    def viewMap(self, pos):
        pygame.Surface.blit(self.gameDisplay, self.mapScreen, pos)
        if not self.report:
            mouse = pygame.mouse.get_pos()
            butReport = Button(self.gameDisplay, green, self.windowWidth - 210, 10, 150, 50, 'Relatório', 24)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if butReport:
                        self.report = not self.report

    def viewReport(self):
        if self.report:
            # Função para exibir Texto em forma de tabela
            def textSpawn(text, range: int, pos, bold):
                localText = text
                font = self.fontMedium
                font.bold = bold
                local = pygame.font.Font.render(font, localText, 1, black)
                pygame.Surface.blit(self.gameDisplay, local, (pos[0] + range/2 - local.get_width()/2, pos[1]))
                pygame.draw.rect(self.gameDisplay, black, (pos[0]-2, pos[1], range, local.get_height()), 1)
                return range

            # Retorna posiçao do mouse
            mouse = pygame.mouse.get_pos()
            # Mostra uma tela branca sobreposta ao mapa
            self.reportSurface = pygame.Surface(self.rectReport)
            self.reportSurface.fill(white)
            pygame.draw.rect(self.gameDisplay, black, [self.currentReportPos[0] - 2, self.currentReportPos[1] - 2, self.rectReport[0] + 4, self.rectReport[1] + 4], 2)
            self.gameDisplay.blit(self.reportSurface, self.currentReportPos)

            # Mostra Cabeçalho dos Registros
            head = textSpawn('Id', 50, (self.currentReportPos[0] + 10, self.currentReportPos[1] + 80), True)
            head = head + textSpawn('Bairro', 300, (self.currentReportPos[0] + 10 + head, self.currentReportPos[1] + 80), True)
            head = head + textSpawn('Zona', 80, (self.currentReportPos[0] + 10 + head, self.currentReportPos[1] + 80), True)
            head = head + textSpawn('Moto', 60, (self.currentReportPos[0] + 10 + head, self.currentReportPos[1] + 80), True)
            head = head + textSpawn('Pedido', 90, (self.currentReportPos[0] + 10 + head, self.currentReportPos[1] + 80), True)
            head = head + textSpawn('Saida', 90, (self.currentReportPos[0] + 10 + head, self.currentReportPos[1] + 80), True)
            head = head + textSpawn('Previsão', 90, (self.currentReportPos[0] + 10 + head, self.currentReportPos[1] + 80), True)
            head = head + textSpawn('Chegada', 90, (self.currentReportPos[0] + 10 + head, self.currentReportPos[1] + 80), True)
            textSpawn('Status', 150, (self.currentReportPos[0] + 10 + head, self.currentReportPos[1] + 80), True)


            # Mostra Registros
            #for i in range(len(self.salesTables[self.indiceTab])):
            reportPrint = self.salesTables
            # Mostra Registros
            for i in range(len(self.salesTables[self.indiceTab])):
                def ConvertTime(tempo):
                    if type(tempo) == int:
                        return Tempo().Print(tempo, 0)
                    else:
                        return tempo
                saleData = self.salesTables[self.indiceTab][i]
                count = textSpawn(f'{saleData.id}', 50, (self.currentReportPos[0] + 10, self.currentReportPos[1] + 100 + (20 * i)), False)
                count = count + textSpawn(f'{saleData.bairro}', 300, (self.currentReportPos[0] + count + 10, self.currentReportPos[1] + 100 + (20 * i)), False)
                count = count + textSpawn(f'{saleData.zona}', 80, (self.currentReportPos[0] + count + 10, self.currentReportPos[1] + 100 + (20 * i)), False)
                count = count + textSpawn(f'{saleData.moto}', 60, (self.currentReportPos[0] + count + 10, self.currentReportPos[1] + 100 + (20 * i)), False)
                count = count + textSpawn(f'{Tempo().Print( saleData.pedido, 0)}', 90, (self.currentReportPos[0] + count + 10, self.currentReportPos[1] + 100 + (20 * i)), False)
                count = count + textSpawn(f'{ConvertTime(saleData.saida)}', 90, (self.currentReportPos[0] + count + 10, self.currentReportPos[1] + 100 + (20 * i)), False)
                count = count + textSpawn(f'{ConvertTime( saleData.previsao)}', 90, (self.currentReportPos[0] + count + 10, self.currentReportPos[1] + 100 + (20 * i)), False)
                count = count + textSpawn(f'{ConvertTime( saleData.chegada)}', 90, (self.currentReportPos[0] + count + 10, self.currentReportPos[1] + 100 + (20 * i)), False)
                count = count + textSpawn(f'{saleData.status}', 150, (self.currentReportPos[0] + count + 10, self.currentReportPos[1] + 100 + (20 * i)), False)
            # Mostra Botão de Fechar
            fechar = Button(self.gameDisplay, gray, self.windowWidth * 19 / 20 - 45, self.windowHeight / 20 + 5,40, 40, 'X', 32)
            # Botoes das Abas
            botaoSize = (50, 50)
            # Botão de Voltar
            voltar = False
            if self.indiceTab - 1 >= 0:
                voltar = Button(self.gameDisplay, gray,
                                self.windowWidth/2 - 100 - botaoSize[0]/2, self.currentReportPos[1] + self.rectReport[1] - 80 , botaoSize[0], botaoSize[1], '<', 32)
            # Botão de Proximo
            proximo = False
            if self.indiceTab + 1 < len(reportPrint):
                proximo = Button(self.gameDisplay, gray,
                                self.windowWidth/2 + 100 - botaoSize[0]/2, self.currentReportPos[1] + self.rectReport[1] - 80, botaoSize[0], botaoSize[1], '>', 32)

            # Controle de Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if fechar:
                        self.report = not self.report
                    if voltar:
                        self.indiceTab -= 1
                    if proximo:
                        self.indiceTab += 1
                if event.type == pygame.KEYDOWN:
                    if event.key == K_PAGEDOWN and self.indiceTab < len(self.salesTables)-1:
                        self.indiceTab += 1
                    if event.key == K_PAGEUP and self.indiceTab > 0:
                        self.indiceTab -= 1

    def direcaoNormal(self, tupla ):
        if tupla[0] != 0 or tupla[1] != 0:
            coef = 1/(pow(pow(tupla[0],2)+pow(tupla[1],2),1/2))
            return (tupla[0] * coef, tupla[1] * coef)
        else:
            return (0, 0)
# Retorna vetor distancia entre dois pontos
    def vetorDistancia(self, pontoA , pontoB):
        dist = pygame.math.Vector2(pontoA) - pygame.math.Vector2(pontoB)
        return dist
# Mover Mapa
    def moveMap(self):
        if not self.report:
            if (0 < pygame.mouse.get_pos()[0] < self.windowWidth) and (0 < pygame.mouse.get_pos()[0] < self.windowHeight):
                if pygame.mouse.get_pressed()[0]:
                    self.currentRange = self.vetorDistancia(self.mapPos, pygame.mouse.get_pos() )
                    if pygame.math.Vector2(self.currentRange) != pygame.math.Vector2(self.lastRange):
                        ajuste = pygame.math.Vector2(self.currentRange) - pygame.math.Vector2(self.lastRange)
                        self.mapPos = pygame.math.Vector2(self.mapPos) - pygame.math.Vector2(ajuste)
                        if self.mapPos[0] > 0:
                            self.mapPos = (0, self.mapPos[1])
                        if self.mapPos[0] < self.windowWidth - self.mapScreen.get_width():
                            self.mapPos = (self.windowWidth - self.mapScreen.get_width(), self.mapPos[1])
                        if self.mapPos[1] > 0:
                            self.mapPos = (self.mapPos[0], 0)
                        if self.mapPos[1] < self.windowHeight - self.mapScreen.get_height():
                            self.mapPos = (self.mapPos[0], self.windowHeight - self.mapScreen.get_height())
                else:
                    self.lastRange = self.vetorDistancia(self.mapPos, pygame.mouse.get_pos() )

    def moveMoto(self):
        def textSpawn(text, pos):
            font = self.fontSmall
            local = pygame.font.Font.render(font, text, 1, black)
            pygame.Surface.blit(self.gameDisplay, local, (pos[0] - local.get_width()/2, pos[1]))

        def LerpMove( inicial, final, speed):
            vetorTemp = v2(final)-v2(inicial)
            denominador = abs(vetorTemp[0])+abs(vetorTemp[1])
            x = 0
            if denominador != 0:
                x = 1/denominador
            vetorMove = x * v2(vetorTemp) * speed
            return vetorMove

        pygame.Surface.blit(self.gameDisplay, self.baseImg, v2(self.basePos)+v2(self.mapPos)-v2(15, 15))
        for i in self.motos:
            if i.rota != None:
                rota = self.routes[i.rota]
                if rota.status == 'Saiu para entrega':
                    if i.indice == 0 and len(self.sales) > 0:
                        i.pos = self.sales[0].pos
                        i.indice += 1
                    else:
                        venda = rota.sales[i.indice]
                        distancia = pygame.math.Vector2.distance_to(v2(i.pos), v2(self.sales[venda].pos))
                        move = LerpMove(i.pos, self.sales[venda].pos, 1)
                        imgTemp = pygame.transform.flip(i.img, move[0] < 0, False)
                        i.pos = v2(i.pos) + LerpMove(i.pos, self.sales[venda].pos, 1)
                        posicao = v2(i.pos) + v2(self.mapPos)
                        destino = v2(self.sales[venda].pos) + v2(self.mapPos)
                        pygame.draw.circle(self.gameDisplay, red, destino, 5)
                        pygame.draw.line(self.gameDisplay, red, posicao, destino, 2)
                        pygame.Surface.blit(self.gameDisplay, imgTemp, v2(i.pos) + v2(self.mapPos) - v2(15, 15))
                        tempoChegada = Tempo().Remains(round(distancia/self.fps))
                        font = self.fontSmall
                        txt_moto = pygame.font.Font.render(font, f'Moto {i.name}', 1, black)
                        txt_chegada = pygame.font.Font.render(font, f'{self.sales[venda].bairro} - {tempoChegada}', 1, black)
                        pygame.Surface.blit(self.gameDisplay, txt_moto, (posicao[0] - txt_moto.get_width()/2, posicao[1] - (15 + txt_moto.get_height())))
                        pygame.Surface.blit(self.gameDisplay, txt_chegada, (posicao[0] - txt_chegada.get_width()/2, posicao[1]+15))

                        if distancia < 0.5:
                            if i.indice < len(rota.sales)-1:
                                self.sales[venda].chegada = Tempo().Sec()
                                status = ['Ok', 'Não Estava', 'Ok', 'Devolvido', 'Ok']
                                self.sales[venda].status = random.choice(status)
                                i.indice += 1
                            else:
                                novo = Moto(i.name)
                                index = self.motos.index(i)
                                self.motos[index] = novo

    def routeControl(self):
        if self.sales == []:
            base = Registro(0, (self.mapScreen.get_width(), self.mapScreen.get_height()), self.arquivo)
            base.pos = ConvertGeoPixel(nafil, self.mapScreen.get_size())
            base.id = 0
            base.bairro = 'Nafil'
            base.zona = 'Nafil'
            self.sales = [base]

        temp = Registro(len(self.sales), (self.mapScreen.get_width(), self.mapScreen.get_height()), self.arquivo)
        self.sales.append(temp)
        newRote = Rota([0, temp.id], temp.pedido, temp.zona)

        if len(self.routes) == 0:
            self.routes.append(newRote)
        else:
            new = True
            for i in range(len(self.routes)):
                obj = self.routes[i]

                for m in self.motos:
                    if m.rota == None and obj.moto == None:
                        obj.moto = m
                        m.rota = i

                if temp.zona == obj.zona and len(obj.sales) < self.limiteSaidas + 1:
                    obj.sales.append(temp.id)
                    new = False
                    if len(obj.sales) >= self.limiteSaidas + 1:
                        obj.sales.append(0)
                        obj.sales = self.AjusteRota(obj.sales)
                        obj.status = 'Fechado sem moto'
                        if obj.moto != None:
                            horario = Tempo().Sec()
                            for j in range(len(obj.sales)):

                                sale = self.sales[obj.sales[j]]
                                sale_left = self.sales[obj.sales[j-1]]
                                inter_temp = pygame.math.Vector2.distance_to(v2(sale.pos), v2(sale_left.pos))
                                sale.saida = Tempo().Sec()
                                horario = horario + round(inter_temp / self.fps) + 2
                                sale.previsao = horario
                                sale.moto = obj.moto.name
                                sale.status = 'Saiu para entrega'
                                obj.status = 'Saiu para entrega'

            if new:
                self.routes.append(newRote)

        # Separar em Abas
        newTab = True
        for i in range(len(self.salesTables)):
            if self.salesTables[i] == []:
                self.salesTables[i] = [temp]
                newTab = False
            elif len(self.salesTables[i]) < 20:
                self.salesTables[i].append(temp)
                newTab = False
        if newTab:
            local = [temp]
            self.salesTables.append(local)

    def spawnSale(self, timeSpawn):
        if self.saleDelay < timeSpawn * self.fps:
            self.saleDelay += 1
        else:
            self.routeControl()
            self.saleDelay = 0
# Executando o Game
    def mainLoop(self):
        self.on_init()
        self.viewMap(self.mapPos)

        while self._running:
            self.viewMap(self.mapPos)
            self.moveMoto()
            self.viewReport()
            self.spawnSale(1)
            self.moveMap()

            pygame.display.flip()
            pygame.time.Clock().tick(self.fps)
game = App()
game.mainLoop()
