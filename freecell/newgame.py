
import cardmovemanager as Cmg

class CurData:
    huase= ("♣","♠","◆","♥")
    paidian=("A","2","3","4","5","6","7","8","9","10","J","Q","K")

    def __init__(self):
        self.board =  [[0 for i in range(25)] for j in range(8)]
        self.bp = [0 for i in range(8)]
        self.freePos = [-1,-1,-1,-1]
        self.finish = [0,0,0,0]

    def checkFinishCell(self):
        upCards=1
        recover = []
        while upCards>0:
            upCards=0
            for i in range(0,8):
                if self.bp[i]>0:
                    card=self.board[i][self.bp[i]-1]
                    cardhuase = card//13
                    cardPoint = card%13
                    if card<26:
                        corresponding1=2
                        corresponding2=3
                    else:
                        corresponding1=0
                        corresponding2=1

                    if cardPoint == self.finish[card//13] and cardhuase == card//13\
                        and (cardPoint <2 or (self.finish[corresponding1]>=cardPoint and self.finish[corresponding2]>=cardPoint)):
                        self.bp[i] -=1
                        self.finish[card//13] +=1
                        upCards +=1
                        recover.append(i)
                        recover.append(self.bp[i])
                        recover.append(card)

            for i in range(0,4):
                if self.freePos[i]>=0:
                    card=self.freePos[i]
                    cardPoint = card%13
                    if card<26:
                        corresponding1=2
                        corresponding2=3
                    else:
                        corresponding1=0
                        corresponding2=1

                    if cardPoint == self.finish[card//13] and (cardPoint <2 or (self.finish[corresponding1]>=cardPoint and self.finish[corresponding2]>=cardPoint)):
                        self.freePos[i]=-1
                        self.finish[card//13] +=1
                        upCards +=1
                        recover.append(8+i)
                        recover.append(0)
                        recover.append(card)
        return recover

    def canMoveCards(self,movetoFreeCol):
        b=1
        if(movetoFreeCol):
            b=0
        kongdang=0
        konglie=0
        for i in range(0,4):
            if(self.freePos[i] == -1):
                kongdang +=1
        for i in range(0,8):
            if(self.bp[i] == 0):
                konglie +=1
        return (kongdang+1)*(konglie+b)


    def ghost(self,cData):
        for i in range(0,8):
            cData.bp[i]=self.bp[i]
            for j in range(0,21):
                cData.board[i][j]=self.board[i][j]
        for i in range(0,4):
            cData.freePos[i]=self.freePos[i]
            cData.finish[i]=self.finish[i]



class NewGame:
    transfrom = (0,2,3,1)
    cellStr= ("1","2","3","4","5","6","7","8","a","b","c","d","h","h","h","h")

    @staticmethod
    def getGame(no):
        curDataRoot = CurData()
        board_data= NewGame.xGame(no)
        print(curDataRoot)
        for i in range(0,8):
            curDataRoot.bp[i]= (59-i)//8
        cur_col = 0
        cur_col_no=0
        for i in range(0,52):
            card = board_data[i]
            curDataRoot.board[cur_col][cur_col_no] = NewGame.transfrom[card%4]*13+(card//4)
            cur_col += 1
            if cur_col == 8:
                cur_col_no += 1
                cur_col = 0
        return curDataRoot


    @staticmethod
    def xGame(no):
        board_data = [0 for i in range(52)]
        wLeft=52
        holdrand = no
        a = 214013 
        b = 2531011
        deck = [0 for i in range(52)]
        for i in range(0,52):
            deck[i] = i
        card = [[0 for i in range(21)] for j in range(9)]
        for col in range(0,9):
            for pos in range(0,21):
                card[col][pos] = -1
        for i in range(0,52):
            holdrand   =   holdrand   *   a   +   b
            j = ((holdrand   >>   16)   &   0x7fff)%wLeft
            card[(i % 8) + 1][ i // 8] = deck[j]
            wLeft -= 1
            deck[j] = deck[wLeft]
        for i in range(0,52): 
            board_data[i] = card[(i % 8) + 1][ i // 8]
        return board_data

    @staticmethod
    def printAnswer(answer):
        answerStr = ""
        for i in range(0,len(answer)):
            md = Cmg.MoveData(answer[i])
            answerStr = answerStr + NewGame.cellStr[md.mf]+NewGame.cellStr[md.mt]+" "
            if((i+1)%10==0):
                answerStr = answerStr +"\r\n"

        answerStr = answerStr + "\r\n"
        return answerStr

    @staticmethod
    def moveCD(cfrom,target):
        return NewGame.cellStr[cfrom]+NewGame.cellStr[target]

