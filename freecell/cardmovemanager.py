import pygame
import sys
import random
from pygame.locals import *
import copy
import os
import newgame as ng
import kdjl as fc

WHITE = (255, 255, 255)

class COORD:
    def __init__(self):
        self.x = 0
        self.y = 0

class MoveData:
    def __init__(self,move_from_to_cnt):
        self.moveFFTC = move_from_to_cnt
        self.mf=move_from_to_cnt//1000000
        #self.mf2=(move_from_to_cnt%1000000)/10000
        self.mt=(move_from_to_cnt%10000)//100
        self.cards=move_from_to_cnt%100


class Step:
    TIME_TYPE_STR = ("移","复","回")
    #时序
    TIME_DRAG=0
    TIME_RESET=1
    TIME_RECYCLE=2

    def __init__(self):
        self.step = -1
        self.subType = Step.TIME_DRAG
        self.subStep = 0
        self.subStepLimit = 10

class Move:
    def __init__(self):
        self.move_from_to_cnt = -1
        self.curData= None
        self.mapstr = 0
        self.parent = None

    @staticmethod
    def init_move(m0,cData,mf,mt,cards):
        m1 = Move()
        m1.parent=m0
        m1.move_from_to_cnt = mf*1000000+mt*100+cards
        m1.curData=cData
        
        if(fc.kdjl3.QUICK_SCAN):
            for i in range(0,8):
                m1.curData.bp[i]=m0.curData.bp[i]
            for i in range(0,4):
                m1.curData.finish[i]=m0.curData.finish[i]
        else:
            m0.curData.ghost(m1.curData)
        
        #free --> board; free-->curData.finish
        #board --> free; board-->curData.finish; board -->board
        if(mf>7):
            if(mt>11):
                #=================== free-->curData.finish
                m1.curData.finish[m0.curData.freePos[mf-8]//13] +=1
                m1.curData.freePos[mf-8]=-1
            else:
                #=================== free --> board
                m1.curData.board[mt][m1.curData.bp[mt]] = m1.curData.freePos[mf-8]
                m1.curData.freePos[mf-8] = -1
                m1.curData.bp[mt] +=1
        else:
            if(mt>11):
                #===================== board-->curData.finish
                #if(cardPoint == finish[card/13] && cardhuase == card/13
                m1.curData.finish[m0.curData.board[mf][m1.curData.bp[mf]-1]//13] +=1
                m1.curData.bp[mf] -=1
            elif(mt>7):
                #===================== board-->free
                m1.curData.freePos[mt-8] = m1.curData.board[mf][m1.curData.bp[mf]-1]
                m1.curData.bp[mf]-=1
            else:
                #===================== board-->board
                m1.curData.board[mt][m1.curData.bp[mt]-1+cards] = m1.curData.board[mf][m1.curData.bp[mf]-1]
                m1.curData.bp[mf]-=cards
                m1.curData.bp[mt]+=cards
        return m1
	

    def mapStr(self):
        l=1
        sumOdd = 0
        sumEven=0
        free=0
        freeRed=0
        freeBlack=0

        if(fc.kdjl3.QUICK_SCAN):
            for i in range(0,4):
                l=l*7+self.curData.finish[i]
            for i in range(0,8):
                l=l*15+self.curData.bp[i]
        else:
            for i in range(0,4):
                l=l*7+self.curData.finish[i]
                card = self.curData.freePos[i]
                if (card == -1):
                    free +=1
                else:
                    if(card < 26):
                        freeBlack += card%13
                    else:
                        freeRed += card%13; 

            for i in range(0,8):
                l=l*15+(self.curData.bp[i]%15)
                if(self.curData.bp[i] > 0):
                    if(i%2==0):
                        sumEven += self.curData.board[i][self.curData.bp[i]-1]%13
                    else:
                        sumOdd += self.curData.board[i][self.curData.bp[i]-1]%13

        l = (((((l*13+sumOdd%13)*13+sumEven%13)*25+freeBlack)*25)+freeRed)*5+free
        self.mapstr = l
        return l


    #恢复牌局：父节点牌局，经过一次移动
    def recover1Move(self,cData,moveCode):
        self.move_from_to_cnt = moveCode
        md = MoveData(moveCode)
        mf = md.mf
        if md.cards==1:
            if mf>7:
                if md.mt>11:
                    #=================== free-->cData.finish
                    cData.finish[cData.freePos[mf-8]//13] +=1
                    cData.freePos[mf-8] = -1
                else:
                    #=================== free --> board
                    cData.board[md.mt][cData.bp[md.mt]]=cData.freePos[mf-8]
                    cData.bp[md.mt] +=1
                    cData.freePos[mf-8]=-1

            else:
                if md.mt>11:
                    #===================== board-->cData.finish
                    cData.finish[cData.board[mf][cData.bp[mf]-1]//13] +=1
                    cData.board[mf][cData.bp[mf]-1]=-1
                    cData.bp[mf] -=1
                elif md.mt>7:
                    #===================== board-->free
                    cData.freePos[md.mt-8]=cData.board[mf][cData.bp[mf]-1]
                    cData.board[mf][cData.bp[mf]-1]=-1
                    cData.bp[mf]-=1
                else:
                    #===================== board-->board
                    cData.board[md.mt][cData.bp[md.mt]]=cData.board[mf][cData.bp[mf]-1]
                    cData.bp[mf] -=1
                    cData.bp[md.mt] +=1
        else:
            for k in range(0,md.cards): 
                cData.board[md.mt][cData.bp[md.mt]+k] = cData.board[mf][cData.bp[mf]-md.cards+k]
            cData.bp[mf]-=md.cards
            cData.bp[md.mt]+=md.cards

    def recover1MoveWithFinishCheck(self,moveCode):
        self.recover1Move(self.curData,moveCode)
        recover = self.curData.checkFinishCell()
        return recover

    def genData(self,m0,cData):
        self.curData = cData
        m0.curData.ghost(cData)
        
        mp=self
        moves=[]
        while(mp.parent!=None):
            moves.append(mp.move_from_to_cnt)
            mp=mp.parent
        moves.reverse()

        for i in range(0,len(moves)):
            self.recover1MoveWithFinishCheck(moves[i])

        return moves
    def genFromParent(self,cData):
        self.curData = cData
        self.parent.curData.ghost(self.curData)
        self.recover1MoveWithFinishCheck(self.move_from_to_cnt)


    def pressedCards(self):
        pressed=0
        for i in range(0,8):
            for j in range(self.curData.bp[i]-1,0,-1):
                if(Move.isCanMove(self.curData.board[i][j-1],self.curData.board[i][j])):
                    pass
                else:
                    pressed+=j
                    break

        return pressed

    @staticmethod
    def isCanMove(card1,card2):
        if((card2%13 == card1%13 -1) and (card2>25 and card1<=25 or card2<=25 and card1>25)):
            return True
        return False

    def isRegularCol(self,col):
        for j in range(self.curData.bp[col]-1,0,-1):
            if(Move.isCanMove(self.curData.board[col][j-1],self.curData.board[col][j])):
                pass
            else:
                return False

        return True

	#cards中一段能否移动到card1的判断：
    @staticmethod
    def canMoveCards(card1,cards):
        if(cards[1]%13 > card1%13 - 1 and cards[1]%13 - cards[0] < card1%13 - 1):
            if((cards[1]%13 - card1%13)%2 == 0):
                if(cards[1]>25 and card1>25 or cards[1]<=25 and card1<=25):
                    return card1%13-1 + cards[0] - cards[1]%13
            else:
                if(cards[1]>25 and card1<=25 or cards[1]<=25 and card1>25):
                    return card1%13-1 + cards[0] - cards[1]%13

        return 0




class CMG: #CardMoveManager
    card_width=63
    card_height=88
    free_cell_left_blank=23
    free_cell_interval=91
    free_cell_top=27
    finish_cell_left_blank=440
    finish_cell_interval=91
    finish_cell_top=27
    board_col_left_blank=67
    board_col_interval=86
    board_col_top=160
    font = None
    screen = None
    gameinfo = None
    dragImg = None
    background = None
    cardImgs = None
    shake_sound = None

    def __init__(self,screen,cData,gameAnswer):
        #初始化图像，声效
        #abpath="D:/Tools/Vsd-python/freecell/img/"
        abpath=os.path.dirname(os.path.abspath(__file__))+"\\img\\"
        if CMG.font == None:
            #print("#############OS.PATH=%s"% os.path.dirname(os.path.abspath(__file__)))
            CMG.font = pygame.font.Font(abpath+'font.ttf', 36)
            CMG.screen = screen
            print("<screen>",screen)
            CMG.dragImg = pygame.image.load(abpath+"xx.png").convert_alpha()
            CMG.background = pygame.image.load(abpath+'kdjl.jpg').convert()
            #CMG.gameinfo = pygame.image.load(abpath+'kdjlsm.jpg').convert()
            CMG.cardImgs = []
            for c in range(0,52):
                src = abpath+'card_%d.jpg' % c
                cardImg = pygame.image.load(src).convert()
                cardImg = pygame.transform.scale(cardImg, (63*1.2, 88*1.2))
                CMG.cardImgs.append(cardImg)
                del cardImg
            CMG.shake_sound = pygame.mixer.Sound(abpath+'shake.wav')
            
        self.init_game_info(cData,gameAnswer)

    def init_game_info(self,cData,gameAnswer):
        self.moveStart = COORD()
        self.moveEnd = COORD()
        self.dragLast = COORD()
        self.dragCr = COORD()

        #生成一步移动
        self.mv = Move()
        self.mv.curData = cData
        self.rootData = copy.deepcopy(cData)
        self.cData_before = ng.CurData()

        #生成解局步骤
        self.answer = gameAnswer
        self.recover = []

        self.step = Step()
        self.move_from_col = 0
        self.move_cards = 0

    def preface(self):
        #pass
        self.screen.blit(self.gameinfo,(0,0))

    def printBoard(self,cData,moveFrom):
        for i in range(0,8):
            bp = cData.bp[i]
            if i == moveFrom:
                 bp=cData.bp[i] - self.move_cards
            for j in range(0,bp):
                self.screen.blit(self.cardImgs[self.mv.curData.board[i][j]],\
                    (CMG.board_col_left_blank+CMG.board_col_interval*i,CMG.board_col_top+j*20))

    def printFreeFinish(self,cData,moveFrom):
        for i in range(0,4):
            if i != (moveFrom - 8) and cData.freePos[i] != -1:
                self.screen.blit(self.cardImgs[cData.freePos[i]],(CMG.free_cell_left_blank+CMG.free_cell_interval*i,CMG.free_cell_top))
        for i in range(0,4):
            if cData.finish[i] > 0:
                self.screen.blit(self.cardImgs[13*i+cData.finish[i]-1],(CMG.finish_cell_left_blank+CMG.finish_cell_interval*i,CMG.finish_cell_top))


    def printAll(self):
        self.screen.blit(self.background, (0, 0))
        if self.step.subType == Step.TIME_RESET:
            self.printFreeFinish(self.mv.curData,-1)
            self.printBoard(self.mv.curData,-1)
            self.screen.blit(self.dragImg\
                ,((self.dragLast.x*(10-self.step.subStep)+self.dragCr.x*self.step.subStep)/10\
                ,(self.dragLast.y*(10-self.step.subStep)+self.dragCr.y*self.step.subStep)/10))
        elif self.step.subType == Step.TIME_RECYCLE:
            self.printFreeFinish(self.cData_before,-1)
            self.printBoard(self.cData_before,-1)

            show_cards=self.step.subStep
            if self.step.subStep > (self.step.subStepLimit - 9):
                show_cards=int(self.step.subStepLimit - 9)
            for i in range(0,show_cards):
                col=self.recover[i*3]
                row=self.recover[i*3+1]
                card=self.recover[i*3+2]
                if col >7:
                    x=CMG.free_cell_left_blank+CMG.free_cell_interval*(col-8)
                    y=CMG.free_cell_top
                else:
                    x=CMG.board_col_left_blank+CMG.board_col_interval*col
                    y=CMG.board_col_top+row*20

                if (self.step.subStep <= self.step.subStepLimit - 9) and (i== self.step.subStep-1):
                    if col>7:
                        self.cData_before.freePos[col-8]=-1
                    else:
                        self.cData_before.bp[col] -= 1
                
                goal_x=CMG.finish_cell_left_blank+(card//13)*CMG.finish_cell_interval
                goal_y=CMG.finish_cell_top
                cur_steps=self.step.subStepLimit-i
                cur_x=(x*(cur_steps-(self.step.subStep-i))+goal_x*(self.step.subStep-i))/cur_steps
                cur_y=(y*(cur_steps-(self.step.subStep-i))+goal_y*(self.step.subStep-i))/cur_steps
                self.screen.blit(self.cardImgs[card],(cur_x,cur_y))
                
            self.screen.blit(self.dragImg,(self.dragLast.x,self.dragLast.y))
        else:
            self.printFreeFinish(self.mv.curData,self.move_from_col)
            self.printBoard(self.mv.curData,self.move_from_col)
            if self.move_cards>1 or self.move_from_col < 8:
                for j in range(0,self.move_cards):
                    self.screen.blit(self.cardImgs[self.mv.curData.board[self.move_from_col][self.mv.curData.bp[self.move_from_col]-self.move_cards+j]]\
                    ,((self.moveStart.x*(10-self.step.subStep)+self.moveEnd.x*self.step.subStep)//10
                    ,(self.moveStart.y*(10-self.step.subStep)+self.moveEnd.y*self.step.subStep)//10+j*40))
            else:
                self.screen.blit(self.cardImgs[self.mv.curData.freePos[self.move_from_col-8]]\
                ,((self.moveStart.x*(10-self.step.subStep)+self.moveEnd.x*self.step.subStep)//10
                ,(self.moveStart.y*(10-self.step.subStep)+self.moveEnd.y*self.step.subStep)//10))

            self.screen.blit(self.dragImg\
                ,((self.moveStart.x*(10-self.step.subStep)+self.moveEnd.x*self.step.subStep)//10+40
                ,(self.moveStart.y*(10-self.step.subStep)+self.moveEnd.y*self.step.subStep)//10))

            if self.step.subStep == 10:
                self.dragLast.x = self.moveEnd.x+40
                self.dragLast.y = self.moveEnd.y
        myfont = pygame.font.Font(None, 70)
        textImage = myfont.render("STEP: %d/%d"% (self.step.step,len(self.answer)), True, WHITE)
        self.screen.blit(textImage,(350,500))

    def getCrood(self,md,fromTo):
        cr = COORD()
        if fromTo == 1:
            col = md.mf
        else:
            col = md.mt
        if col >11:
            cr.x = CMG.finish_cell_left_blank+CMG.finish_cell_interval*(md.mt-12)
            cr.y = CMG.finish_cell_top
        elif col >7:
            cr.x = CMG.free_cell_left_blank+CMG.free_cell_interval*(col-8)
            cr.y = CMG.free_cell_top
        else:
            cr.x = CMG.board_col_left_blank+CMG.board_col_interval*col
            if fromTo == 1:
                cr.y = CMG.board_col_top+(self.mv.curData.bp[col]-md.cards-1)*20
            else:
                cr.y = CMG.board_col_top+self.mv.curData.bp[col]*20

        return cr


    def moveAll(self):
        if self.step.step == len(self.answer) and self.step.subType == Step.TIME_RECYCLE\
            and self.step.subStep >= self.step.subStepLimit:
            return False
            
        #结局结束判别
        if self.step.step == len(self.answer) and self.step.subType == Step.TIME_RECYCLE\
            and self.step.subStep == self.step.subStepLimit-1:
            self.step.subStep +=1
            cData_before = copy.deepcopy(self.mv.curData)
            return False

        #step=-1开局第一步，或者一次移牌刚好结束
        if self.step.step == -1 or self.step.subType == Step.TIME_DRAG and self.step.subStep == 10:
            self.shake_sound.play()
            if self.step.step>-1:
                self.cData_before = copy.deepcopy(self.mv.curData)
                self.mv.recover1Move(self.cData_before, self.answer[self.step.step])
                self.recover = self.mv.recover1MoveWithFinishCheck(self.answer[self.step.step])
                if len(self.recover) > 0:
                    self.step.subType = Step.TIME_RECYCLE
                    self.step.subStepLimit = len(self.recover)//3+9

            self.step.step +=1
            self.step.subStep=0
            if self.step.step == len(self.answer):
                pass
            else:
                md = MoveData(self.answer[self.step.step])
                self.move_from_col = md.mf
                self.move_cards = md.cards

                self.moveStart = self.getCrood(md,1)
                self.moveEnd = self.getCrood(md,2)

                if len(self.recover) == 0:
                    self.step.subType = Step.TIME_RESET
                    self.step.subStepLimit = 10
                    self.dragCr.x = self.moveStart.x+40
                    self.dragCr.y = self.moveStart.y

        elif self.step.subType == Step.TIME_RECYCLE:
            self.step.subStep +=1
            if self.step.subStep == self.step.subStepLimit:
                self.step.subType = Step.TIME_RESET
                self.step.subStep = 0
                self.step.subStepLimit = 10
                if self.step.step < len(self.answer):
                    self.dragCr.x = self.moveStart.x+40
                    self.dragCr.y = self.moveStart.y

        elif self.step.subType == Step.TIME_RESET:
            self.step.subStep +=1
            if self.step.subStep == self.step.subStepLimit:
                self.step.subType = Step.TIME_DRAG
                self.step.subStep = 0
                self.step.subStepLimit = 10
        else:
        	self.step.subStep +=1
        
        return True
