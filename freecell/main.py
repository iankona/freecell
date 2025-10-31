import pygame
import sys
import os
import random
import time
from pygame.locals import *
import tkinter as tk
from tkinter import *
import tkinter.messagebox  # 要使用messagebox先要导入模块
import newgame as ng
import cardmovemanager as Cmg
import kdjl as fc


#------------------------------------------------
#tkinter,pygame混合区 START
#------------------------------------------------
root = tk.Tk()
root.geometry("800x720+900+0")
root.resizable(0,0)

embed = tk.Frame(root, width = 800, height = 570) #creates embed frame for pygame window
embed.grid(columnspan = (800), rowspan = 730) # Adds grid
embed.pack(side = TOP) #packs window to the left

buttonwin = tk.Frame(root, width = 800, height = 150)
buttonwin.pack(side = BOTTOM)

os.environ['SDL_WINDOWID'] = str(embed.winfo_id())
os.environ['SDL_VIDEODRIVER'] = 'windib'

screen = pygame.display.set_mode((800,570))
#screen.fill(pygame.Color(255,255,255))

#pygame.init()
pygame.display.init()
pygame.mixer.init()
pygame.font.init()
#加载音乐音效
#pygame.mixer.music.load(os.path.dirname(os.path.abspath(__file__))+"\\img\\bg_music.ogg")
#pygame.mixer.music.set_volume(0.2)
#------------------------------------------------
#tkinter,pygame混合区 END
#------------------------------------------------

#参数，因为函数内要使用之外的变量，需要globe，因此全部打包
class PARAM:
    kdjl33 = fc.kdjl3()
    cmg = None
    STATUS = 0
    STATUS_LAST = 0
    SUB_STATUS = 0
    status_unchange = 0
    TICK_UNUSE = 1
    TICK_LOAD = 1
    TICK_NORMAL = 5
    TICK_STEP = 30
    game_no = random.randint(1,100000)
    load_start = 0
    load_end = 0
    load_cur = 0
    load_msg = ""
    load_bar_last = 0
    load_start_time = 0
    def per(self,cur):
	    return int((cur+1-self.load_start)/(self.load_end+1-self.load_start)*100)
    def next_per(self):
        return self.per(self.load_cur+1)-self.load_bar_last

#按钮动作区 =====================================
def pause_start():
    global param
    param.SUB_STATUS = 1

def pause_end():
    global param
    param.SUB_STATUS = 0

def exit_game():
    global param
    param.STATUS = 100

def get_game_no(inputcell):
    if inputcell.get().isdigit():
        no = int(inputcell.get())
        if 0<no and no<1000000:
            return no
    return -1

def sel_game():
    global param
    no = get_game_no(inputno)
    if no == -1:
        pass
    else:
        param.STATUS = 1

def next_game():
    global param
    no = get_game_no(inputno)
    if no == -1 or no == 999999:
        pass
    else:
        inputno.set(int(inputno.get())+1)
        param.STATUS = 1

def show_step():
    global param
    param.STATUS = 90
    param.SUB_STATUS = 0
    if inputspd.get().isdigit():
        spd = int(inputspd.get())
        if 10<spd and spd<100:
            param.TICK_STEP = spd

def load_test():
    global param
    startno = get_game_no(inputload1)
    endno = get_game_no(inputload2)
    if 0<startno and startno < endno and endno < 999999:
        param.load_start = startno
        param.load_end = endno
        param.load_cur = startno
        param.load_msg = ""
        param.load_bar_last = 0
        btnwin_txt3.delete(0.0,'end')
        btnwin_txt3.insert(END,"○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○")
        param.load_start_time = time.time()
        param.STATUS = 70
    else:
        tk.messagebox.showinfo(title='输入有误', message='1-999999之间，且开始号小于结束号')

#控件定义区 =====================================
btnwin_txt = tk.Text(buttonwin,width = 30,height = 10)
btnwin_txt.place(x=0,y=0)
btnwin_txt3 = tk.Text(buttonwin,width = 40,height = 10)
btnwin_txt3.place(x=220,y=0)

chkfastsrh = tk.IntVar()
btnwin_srh_c = tk.Checkbutton(buttonwin, text='快搜',variable=chkfastsrh, onvalue=1, offvalue=0)
chkfastsrh.set(1)
btnwin_srh_c.place(x=620,y=0)
chkfreeless = tk.IntVar()
btnwin_fels_c = tk.Checkbutton(buttonwin, text='理顺断开移动',variable=chkfreeless, onvalue=1, offvalue=0)
btnwin_fels_c.place(x=680,y=0)
btnwin_no_l = tk.Label(buttonwin, text='编号：')
btnwin_no_l.place(x=510,y=35)
inputno = StringVar()
btnwin_no_e = tk.Entry(buttonwin, show=None,width=6,textvariable = inputno)
btnwin_no_e.place(x=570,y=35)
btnwin_sel_b = tk.Button(buttonwin,text = '选择该局', width=7, command=sel_game)
btnwin_sel_b.place(x=620,y=30)
btnwin_next_b = tk.Button(buttonwin,text = '下一局', width=7, command=next_game)
btnwin_next_b.place(x=680,y=30)

btnwin_spd_l = tk.Label(buttonwin, text='速度(11-99)：')
btnwin_spd_l.place(x=510,y=65)
inputspd = StringVar()
btnwin_spd_e = tk.Entry(buttonwin, show=None,width=3,textvariable = inputspd)
btnwin_spd_e.place(x=590,y=65)
inputspd.set(11)

btnwin_ans_b = tk.Button(buttonwin,text = '解局执行', width=7, command=show_step)
btnwin_ans_b.place(x=620,y=60)
button_pau_b1 = tk.Button(buttonwin,text = '暂停', width=7, command=pause_start)
button_pau_b1.place(x=680,y=60)
button_pau_b2 = Button(buttonwin,text = '继续', width=7, command=pause_end)
button_pau_b2.place(x=740,y=60)

inputload1 = StringVar()
btnwin_load_e1 = tk.Entry(buttonwin, show=None,width=6,textvariable = inputload1)
btnwin_load_e1.place(x=510,y=100)
inputload2 = StringVar()
btnwin_load_e2 = tk.Entry(buttonwin, show=None,width=6,textvariable = inputload2)
btnwin_load_e2.place(x=560,y=100)
button_load_b = Button(buttonwin,text = '负载测试', width=7, command=load_test)
button_load_b.place(x=620,y=100)
button_exit_b = Button(buttonwin,text = '退出画面', width=7, command=exit_game)
button_exit_b.place(x=740,y=100)

#状态，参数，循环中使用，比如STATUS=0:初次进入，1:...100:退出
param = PARAM()
param.cmg = Cmg.CMG(screen,None,[])
#param.cmg.preface()
inputno.set(param.game_no)

#root.update() #貌似不需要

#------------------------------------------------
#主函数，使用pygame框架，无限LOOP对各种事件然后相应处理
#------------------------------------------------
def main():
    global param
    #pygame.mixer.music.play(-1)
    clock = pygame.time.Clock()

    while True:
        #这段event代码是必须的，哪怕在这个程序中不需要，不执行的话整个框架转不动
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            #点击鼠标游戏暂停
            elif event.type == MOUSEBUTTONDOWN:
                pass
            #空格引爆全屏炸弹
            elif event.type == KEYDOWN:
                pass
            #每30秒随机发放一个补给包

        #画面按钮按下后，修改param.STATUS,实际动作这里实现
        if  param.STATUS == 100:
            #退出按钮
            if tk.messagebox.askokcancel('提示', '要退出画面吗'):
                break
            btnwin_txt3.insert("3.3","***")
            param.STATUS = 0
        elif param.STATUS == 90:
            #解局演示
            if param.SUB_STATUS == 0:
                if param.cmg.moveAll() == False:
                    param.STATUS = 10
                param.cmg.printAll()
        elif param.STATUS == 70:
            #负载测试
            t_start = time.time()
            while time.time()-t_start< 0.8:
                try:
                    curDataRoot = ng.NewGame.getGame(param.load_cur)
                    answer = param.kdjl33.freecell(curDataRoot)
                    if len(answer) == 0:
                        param.load_msg = param.load_msg + "没有解决：no=%d \n" % (param.load_cur)
                except Exception as e:
                    print(str(param.load_cur),type(e),e)

                param.load_cur += 1
                if param.load_cur >= param.load_end:
                    break

            pers = param.next_per()
            if pers > 0:
                btnwin_txt3.delete("1.%d" % (100-pers),'end')
                btnwin_txt3.insert("1.%d" % (param.load_bar_last),'●'*pers)
                param.load_bar_last += pers
            inputload1.set(str(param.load_cur))
            if param.load_cur >= param.load_end:
                param.STATUS = 0
                btnwin_txt3.insert('end',param.load_msg)
                btnwin_txt3.insert('end',"耗时：%.3f" % (time.time()-param.load_start_time))

        elif param.STATUS == 1:
            #选择某一局：这一局或者下一局
            curDataRoot = ng.NewGame.getGame(int(inputno.get()))
            if chkfastsrh.get():
                fc.kdjl3.QUICK_SCAN = True
            else:
                fc.kdjl3.QUICK_SCAN = False
            if chkfreeless.get():
                fc.kdjl3.freecol_less_move = True
            else:
                fc.kdjl3.freecol_less_move = False
            answer = param.kdjl33.freecell(curDataRoot)
            param.cmg.init_game_info(curDataRoot,answer)
            btnwin_txt.delete(0.0,'end')
            btnwin_txt.insert(END,ng.NewGame.printAnswer(answer))
            btnwin_txt3.insert(END,fc.kdjl3.systemOutMsg)
            param.STATUS = 10
        elif param.STATUS == 10:
            param.cmg.printAll()
            

        #显示游戏画面
        pygame.display.flip()
        #设置帧率：长期画面不操作，设置成最闲
        if param.STATUS == param.STATUS_LAST:
            param.status_unchange += 1
        else:
            param.STATUS_LAST = param.STATUS
            param.status_unchange = 0
        #根据param.STATUS，设置帧率
        if param.STATUS == 90:
            clock.tick(param.TICK_STEP)
        elif param.STATUS == 70:
            clock.tick(param.TICK_LOAD)
        elif param.status_unchange > 1000:
            clock.tick(param.TICK_UNUSE)
        else:
            clock.tick(param.TICK_NORMAL)
            
        root.update()

main()
