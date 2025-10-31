import copy
import time
import newgame as ng
import cardmovemanager as Cmg

class kdjl3:
    systemOut = 1    #0：不输出，1：输出到控制台，2：输出到log.txt
    maxFloor = 85
    curFloor = 0
    move_gen_seq =((1,2,3,4,5),(2,1,3,4,5),(2,1,4,3,5),(2,5,1,3,4),(1,2,5,3,4),(2,4,3,1,5))
    cur_seq = 2
    regular_less_move = False 
    freecol_less_move = False 
    moveGenerator = 1
    QUICK_SCAN = True
    systemOutMsg=None
    moveGen = None


    def freecell(self,curDataRoot):
        srh=[]
        #记录当前为止所有移动产生局面的编号，一面进入重复局面
        srhMap={}
        answer=[]
        cur_floor=0

        floor_ptr = [0 for i in range(100)]
        root0=Cmg.Move()
        dummy=Cmg.Move()
        curDataRootCopy= copy.deepcopy(curDataRoot)
        #curData0= ng.CurData()
        #curData1= ng.CurData()
        curDataList = []
        for i in range(0,kdjl3.maxFloor+2):
            curData = ng.CurData()
            curDataList.append(curData)
        if kdjl3.moveGen == None:
            kdjl3.moveGen = MoveGen()

        for i in range(0,100):
            floor_ptr[i]=0
        #第一层搜索数据生成
        root0.curData=curDataRoot
        moves = []
        moves.append(root0)
        moves.append(dummy)
        srh.append(moves)

        #递归搜索
        t_start = time.time()
        #self.recursive_floor(root0,curData0,curData1,srh,srhMap,floor_ptr,cur_floor)
        self.recursive_floor(root0,curDataList,srh,srhMap,floor_ptr,cur_floor)

        #结果表示
        kdjl3.systemOutMsg = "#-------------------------------\n搜索节点数:%d    耗时：%.3f\n" % (len(srhMap),time.time()-t_start)
        for j in range(1,len(srh)):
            answer.append(srh[j][floor_ptr[j]].move_from_to_cnt)

        return answer

    #def recursive_floor(self,root0,curData0,curData1,srh,srhMap,floor_ptr,cur_floor):
    def recursive_floor(self,root0,curDataList,srh,srhMap,floor_ptr,cur_floor):
        moves = []
        floor = None
        root = None
        rtn = 0
        genMoves = None

        #取出当前层的当前节点
        floor = srh[cur_floor]
        root = floor[floor_ptr[cur_floor]]
        if(cur_floor>0):
            #genMoves = root.genData(root0,curData0)
            root.genFromParent(curDataList[cur_floor])
        #if(cur_floor>0):
        #    root.genData(root0,curData0)

        #牌局解决判断
        if root.curData.finish[0]==13 and root.curData.finish[1]==13 and root.curData.finish[2]==13 and root.curData.finish[3]==13:
            return 1
        #/*
        if root.pressedCards()==0:
            return 1

        #发展子节点
        #systemOutStr ="["+str(root.mapstr)+"]ROUTE:"+ self.printWithTab(cur_floor,genMoves)
        #moves = kdjl3.moveGen.getAllMoves(srhMap,root,curData1)
        moves = kdjl3.moveGen.getAllMoves(srhMap,root,curDataList[cur_floor+1])
        #systemOutStr = systemOutStr + self.printMoves(moves)
        #print(systemOutStr)

        #无法继续发展？判别
        if len(moves)>0 and cur_floor<kdjl3.maxFloor:
            #下一层能展开，而且层数<150(设定的最大展开层数)
            cur_floor +=1
            srh.append(moves)
            #System.out.print(" " + moves.get(0).move_from_to_cnt)
            for i in range(0,len(moves)):
                floor_ptr[cur_floor] = i
                #rtn = self.recursive_floor(root0,curData0,curData1,srh,srhMap,floor_ptr,cur_floor)
                rtn = self.recursive_floor(root0,curDataList,srh,srhMap,floor_ptr,cur_floor)
                if rtn == 1:
                    return 1
            #同一层节点全部展开，且挨个搜索后都没有结果，移去这一层(这一层的后代早在之前的递归中已被移除)，返回0
            srh.remove(moves)

        return 0


    #DEBUG用：节点本身map值：来到该节点所经过移动 CHILD：显示该节点的子节点
    # [3319517996571178253]ROUTE:28 15 1a 81 2b a2 27 72 	CHILD:[1:3a:3319517595526250627][2:4a:3319517969835338127][3:6a:3319517996452593937]
    def printWithTab(self,floorNo,genMoves):
        return self.genMovesStr(genMoves)
    def genMovesStr(self,genMoves):
        sstr=""
        if(genMoves != None):
            for i in range(0,len(genMoves)):
                md = Cmg.MoveData(genMoves[i])
                sstr = sstr + ng.NewGame.moveCD(md.mf,md.mt)+" "

        return sstr
    def printMoves(self,moves):
        sstr=""
        for i in range(0,len(moves)):
            md = Cmg.MoveData(moves[i].move_from_to_cnt)
            sstr = sstr + "[%d:%s:%s]" % (i+1,ng.NewGame.moveCD(md.mf,md.mt),moves[i].mapstr)

        return ("\tCHILD:" + sstr)



class MoveGen:
    def getAllMoves(self,srhMap,root,cData):
        moves= []

        cards = []
        for i in range(0,12):
            colcard = self.getCards(srhMap,root,i)
            cards.append(colcard)

        for seq in range(0,5):
            if kdjl3.move_gen_seq[kdjl3.cur_seq][seq] == 1:
                #移入回收列
                for i in range(0,12):
                    move = self.Moveto(srhMap,root,cData,i,15,cards[i])
                    if move != None:
                        moves.append(move)

            if(kdjl3.move_gen_seq[kdjl3.cur_seq][seq] == 2):
                #移入牌列
                for l in range(0,8):
                    for i in range(0,12):
                        if(cards[i][0]>0):
                            move = self.Moveto(srhMap,root,cData,i,l,cards[i])
                            if(move != None):
                                moves.append(move)

            if(kdjl3.move_gen_seq[kdjl3.cur_seq][seq] == 3):
                #移入空档区
                for i in range(0,8):
                    if(cards[i][0]==1 or (cards[i][0] > 0 and kdjl3.freecol_less_move)):
                        move = self.Moveto(srhMap,root,cData,i,11,cards[i])
                        if(move != None):
                            moves.append(move)

            if(kdjl3.move_gen_seq[kdjl3.cur_seq][seq] == 4):
                #移动到空列
                for i in range(0,12):
                    if(i<8 and root.isRegularCol(i)):
                        continue
                    if(cards[i][0]>0):
                        move = self.MovetoFreeCol(srhMap,root,cData,i,cards)
                        if(move != None):
                            moves.append(move)

            if(kdjl3.move_gen_seq[kdjl3.cur_seq][seq] == 5):
                # 牌列之间移动：理顺的牌比如3,4,...10；之前【移入牌列】方法，需要目标列是J，才能移动
                #         实际是4,5,...10都行。不能抹杀这种可能，特别是移动列较长，压住了重要的牌
                for l in range(0,8):
                    if(cards[l][0]>0):
                        for i in range(0,8):
                            if(l==i):
                                continue
                            if(cards[i][0]>0):
                                rtn = Cmg.Move.canMoveCards(root.curData.board[l][root.curData.bp[l]-1],cards[i]) 
                                if(rtn > 0 and rtn<= root.curData.canMoveCards(False)):
                                    move=self.newMove(srhMap,root,cData,i,l,rtn)
                                    if(move != None):
                                        moves.append(move)

        return moves


    # 把牌列从移动开始列移动目标列：空档，回收列，只能是移一张
    # 回收列调用，只需要指定目标列是15，空档，只需要指定目标列是11
    def Moveto(self,srhMap,root,cData,cfrom,target,cards):
        move=None
        if cards[0] == 0:
            return move
        if(target < 8):
            if(root.curData.bp[target] > 0):
                if(Cmg.Move.isCanMove(root.curData.board[target][root.curData.bp[target]-1],cards[1]) and cards[0] <= root.curData.canMoveCards(False)):
                    move = self.newMove(srhMap,root,cData,cfrom,target,cards[0])

        elif(target == 11):
            for l in range(8,12):
                if(root.curData.freePos[l-8] == -1):
                    move = self.newMove(srhMap,root,cData,cfrom,l,1)
                    break

        else:
            if( cards[2] % 13 == root.curData.finish[cards[2]//13]):
                move = self.newMove(srhMap,root,cData,cfrom,cards[2]//13+12,1)

        return move


    # 取得移动牌列数据
    # int[0:牌张数；1:理顺牌的开始牌；2:最上边的那张牌]：
    #         对于没有理顺的列，或者空档区的牌:牌张数为1，对于空档或空列:牌张数为0
    def getCards(self,srhMap,root,curCol):
        if (curCol < 8):
            if(root.curData.bp[curCol] > 0):
                if(root.curData.bp[curCol] == 1):
                    return [1,root.curData.board[curCol][0],root.curData.board[curCol][0]]
                for j in range(root.curData.bp[curCol]-1,0,-1):
                    if(Cmg.Move.isCanMove(root.curData.board[curCol][j-1],root.curData.board[curCol][j])):
                        pass
                    else:
                        return [root.curData.bp[curCol]-j,root.curData.board[curCol][j],root.curData.board[curCol][root.curData.bp[curCol]-1]]

                return [root.curData.bp[curCol],root.curData.board[curCol][0],root.curData.board[curCol][root.curData.bp[curCol]-1]]

        elif(curCol < 12 and root.curData.freePos[curCol-8] != -1):
            return [1,root.curData.freePos[curCol-8],root.curData.freePos[curCol-8]]
        return [0,-1,-1]


    # 生成一步移动：成功:非null，失败:null
    def newMove(self,srhMap,m0,cData,mf,mt,cards):
        move=Cmg.Move.init_move(m0,cData,mf,mt,cards)
        mapStr=move.mapStr()

        if srhMap.get(mapStr)== None:
            srhMap.update({mapStr:0})
            move.curData=None
        else:
            return None
        return move


     # 移动到空列
    def MovetoFreeCol(self,srhMap,root,cData,cfrom,cards):
        move=None
        for i in range(0,8):
            if(root.curData.bp[i] == 0):
                if(cfrom > 7):
                    for j in range(0,8):
                        if(cards[j][0]>0 and Cmg.Move.isCanMove(cards[cfrom][1],cards[j][1])):
                            move=self.newMove(srhMap,root,cData,cfrom,i,cards[cfrom][0])
                            break
                        elif(kdjl3.freecol_less_move and cards[j][0]>1):
                            for c in range(cards[j][0] - 1,0,-1):
                                if( Cmg.Move.isCanMove(cards[cfrom][1],root.curData.board[j][root.curData.bp[j]-c])):
                                    move=self.newMove(srhMap,root,cData,cfrom,i,1)
                                    break

                    for j in range(0,4):
                        if(root.curData.freePos[j] != -1 and Cmg.Move.isCanMove(cards[cfrom][1],root.curData.freePos[j])):
                            move=self.newMove(srhMap,root,cData,cfrom,i,1)

                else:
                    canMove = root.curData.canMoveCards(True)
                    if(cards[cfrom][0] <= canMove):
                        move = self.newMove(srhMap,root,cData,cfrom,i,cards[cfrom][0])
                    elif(kdjl3.regular_less_move):
                        move = self.newMove(srhMap,root,cData,cfrom,i,canMove)

                break

        return move
