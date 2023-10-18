"""
坦克大战游戏需求：
1.项目中有哪些类
  a.坦克类(我方坦克、敌方坦克)-----射击、移动类、显示坦克的方法
  b.子弹类-----移动、显示子弹的方法
  c.墙壁类-----是否可以通过
  d.爆炸效果类-----展示爆炸效果
  e.音效类-----播放音乐
  f.主类-----开始游戏、结束游戏
"""
import pygame
import time
import random
from pygame.sprite import Sprite

SCREEN_WIDTH = 760
SCREEN_HEIGHT = 500
BG_COLOR = pygame.Color(0, 0, 0)  # lightblue  (0,0,0)表示黑色，每个整数(范围是0到255)代表了RGB（红、绿、蓝）颜色通道的值
TEXT_COLOR = pygame.Color(173, 216, 230)


class BaseItem(Sprite):
    def __init__(self):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)


class MainGame:
    window = None
    running = True
    my_tank = None
    enemyTankList = []
    enemyTankCount = 5
    my_tank_BulletList = []
    enemy_tank_BulletList = []
    explodeList = []
    wallList = []

    def __init__(self):
        pass

    def startGame(self):
        """加载主窗口
        1.初始化显示模块
        2.设置窗口的大小及显示---返回的 Surface可以像常规 Surface一样进行绘制，但最终会在监视器上看到更改
        3.设置当前窗口标题
        4.pygame.display.update()更新软件显示的屏幕部分,加上while循环，使之始终保持刷新状态
        5.给窗口设置填充色 fill(color, rect=None, special_flags=0) -> Rect 如果没有给出rect参数，则整个Surface将被填充
        6.点击窗口关闭按钮没有反应---注意将getEvent方法放到while中，使之始终保持捕获.新增类属性running = True以解决pygame.quit()所带来的
        pygame.error: display Surface quit问题.(推荐使用pygame.quit()而不是exit())
        7.左上角文字绘制：pygame.Surface.blit(source, dest, area=None, special_flags=0) -> Rect
        source：源表面，你希望从中复制内容的表面.  dest：目标表面，表示你要将内容绘制到哪里.
        area：可选参数，表示要绘制的源表面的区域。如果提供了这个参数，只有该区域的内容会被复制到目标表面。如果省略了这个参数，整个源表面将被复制.
        8.初始化我方坦克,在while循环中调用坦克显示的方法.对坦克的移动进行优化并引入time模块time.sleep(0.02)使得长按功能添加后降低坦克移动速度
        9.新增初始化敌方坦克方法,并将敌方坦克添加到列表中.接着在while中新增展示敌方坦克方法---直接遍历敌方坦克列表
        10.新增敌方/我方坦克发射子弹功能
        11.我方子弹与敌方坦克的碰撞----使用pygame模块中的精灵类 Sprite类
        12.敌方子弹与我方坦克的碰撞，并添加爆炸效果
        13.让我方坦克重生----按下Exc键我方坦克重生
        14.添加墙壁----a.子弹不能穿墙(子弹击中墙壁时，子弹消失，墙的hp减少) b.坦克不能穿墙
        15.敌我双方坦克发生碰撞---敌方碰我方 and 我方碰敌方
        16.添加音效
        """
        pygame.display.init()
        MainGame.window = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        pygame.display.set_caption('Kevin的专属坦克大战游戏')
        # self.createMyTank()
        MainGame.my_tank = MyTank(360, 360)
        music = Music('music/start.wav')
        music.play()
        self.createEnemyTank()
        self.createWall()
        while MainGame.running:
            time.sleep(0.02)
            MainGame.window.fill(BG_COLOR)
            if MainGame.my_tank and MainGame.my_tank.live:
                MainGame.my_tank.displayTank()
            else:
                # del MainGame.my_tank
                MainGame.my_tank = None
            self.displayEnemyTank()
            self.displayMyBullet()
            self.displayEnemyBullet()
            self.displayExplode()
            self.displayWall()
            self.getEvent()
            MainGame.window.blit(self.getTextSurface("敌方坦克剩余数量: {0}".format(len(MainGame.enemyTankList))), (10, 10))
            if MainGame.my_tank and MainGame.my_tank.live:
                if MainGame.my_tank.switch:
                    MainGame.my_tank.move_Tank()
                    MainGame.my_tank.Tank_hit_Wall()
                    MainGame.my_tank.myTank_hit_enemyTank()
            pygame.display.update()
        pygame.quit()

    @staticmethod
    def createMyTank():
        MainGame.my_tank = MyTank(360, 360)
        music = Music('music/start.wav')
        music.play()

    @staticmethod
    def createEnemyTank():
        top = 100
        for i in range(MainGame.enemyTankCount):
            left = random.randint(0, 600)
            speed = random.randint(1, 4)
            enemy = EnemyTank(left, top, speed)
            MainGame.enemyTankList.append(enemy)

    @staticmethod
    def createWall():
        for i in range(5):
            wall = Wall(i * 160, 220)
            MainGame.wallList.append(wall)

    @staticmethod
    def displayEnemyTank():
        for enemyTank in MainGame.enemyTankList:
            if enemyTank.live:
                enemyTank.displayTank()
                # enemyTank.move_Tank()
                enemyTank.randMove()
                enemyTank.Tank_hit_Wall()
                if MainGame.my_tank and MainGame.my_tank.live:
                    enemyTank.enemyTank_hit_myTank()
                enemyBullet = enemyTank.shot()
                if enemyBullet:
                    MainGame.enemy_tank_BulletList.append(enemyBullet)
            else:
                MainGame.enemyTankList.remove(enemyTank)

    @staticmethod
    def displayMyBullet():
        """循环遍历我方子弹存储列表,优化如下：
        1.如果子弹碰到墙壁，让子弹消失----判断当前的子弹是否是活着状态，如果是则进行显示及移动，否则将其从列表中删除
        2.最多可以发射3颗子弹，不能一直发射----getEvent()方法中增加判断：当前我方子弹列表长度小于3使才可以创建
        判断我方子弹是否与敌方坦克发生碰撞
        """
        for myBullet in MainGame.my_tank_BulletList:
            if myBullet.live:
                myBullet.displayBullet()
                myBullet.move_Bullet()
                myBullet.myBullet_hit_enemyTank()
                myBullet.hitWall()
            else:
                MainGame.my_tank_BulletList.remove(myBullet)

    @staticmethod
    def displayEnemyBullet():
        for enemyBullet in MainGame.enemy_tank_BulletList:
            if enemyBullet.live:
                enemyBullet.displayBullet()
                enemyBullet.move_Bullet()
                enemyBullet.enemyBullet_hit_myTank()
                enemyBullet.hitWall()
            else:
                MainGame.enemy_tank_BulletList.remove(enemyBullet)

    @staticmethod
    def displayExplode():
        for explode in MainGame.explodeList:
            if explode.live:
                explode.displayExplide()
            else:
                MainGame.explodeList.remove(explode)

    @staticmethod
    def displayWall():
        for wall in MainGame.wallList:
            if wall.live:
                wall.displayWall()
            else:
                MainGame.wallList.remove(wall)

    @staticmethod
    def endGame():
        print("Thank you for your use and we look forward to seeing you again!")
        MainGame.running = False

    @staticmethod
    def getTextSurface(text):
        """左上角文字绘制
        1.初始化字体模块
        2.从系统字体创建字体font对象 SysFont（name, size, bold=False, italic=False）-> Font
        在使用前可以使用pygame.font.get_fonts来获取所有可用的字体
        3.在新Surface上绘制文本 pygame.font.Font.render(text, antialias, color, background=None) -> Surface
        这将创建一个新的表面，并在上面渲染指定的文本.  font.render返回的是一个小的surface,需要将它绘制到大的Surface上
        """
        pygame.font.init()
        # print(pygame.font.get_fonts())
        font = pygame.font.SysFont('kaiti', 18)
        textSurface = font.render(text, True, TEXT_COLOR)
        return textSurface

    def getEvent(self):
        """
        先获取所有事件，接着判断是鼠标点击关闭窗口还是键盘的操作(上、下、左、右、空格)，移动坦克时应先切换方向
        避免长按按键移动坦克的同时按压并松开空格键发射子弹造成坦克移动中断,所以应当在if event.type == pygame.KEYUP:中判断
        松开的键是上下左右键时才改变开关状态"""
        eventList = pygame.event.get()
        for event in eventList:
            if event.type == pygame.QUIT:
                self.endGame()
            if event.type == pygame.KEYDOWN:
                if MainGame.my_tank and MainGame.my_tank.live:
                    if event.key == pygame.K_LEFT:
                        MainGame.my_tank.direction = 'L'
                        MainGame.my_tank.switch = True
                        # MainGame.my_tank.move_Tank()
                        print("按下左键，坦克向左移动")
                    elif event.key == pygame.K_RIGHT:
                        MainGame.my_tank.direction = 'R'
                        MainGame.my_tank.switch = True
                        # MainGame.my_tank.move_Tank()
                        print("按下右键，坦克向右移动")
                    elif event.key == pygame.K_UP:
                        MainGame.my_tank.direction = 'U'
                        MainGame.my_tank.switch = True
                        # MainGame.my_tank.move_Tank()
                        print("按下上键，坦克向上移动")
                    elif event.key == pygame.K_DOWN:
                        MainGame.my_tank.direction = 'D'
                        MainGame.my_tank.switch = True
                        # MainGame.my_tank.move_Tank()
                        print("按下下键，坦克向下移动")
                    elif event.key == pygame.K_SPACE:
                        if len(MainGame.my_tank_BulletList) < 3:
                            my_tank_Bullet = Bullet(MainGame.my_tank)
                            MainGame.my_tank_BulletList.append(my_tank_Bullet)
                            music = Music('music/hit.wav')
                            music.play()
                        print("发射子弹")
                else:
                    if event.key == pygame.K_ESCAPE:
                        self.createMyTank()
            if event.type == pygame.KEYUP:
                if MainGame.my_tank and MainGame.my_tank.live:
                    if (event.key == pygame.K_UP or event.key == pygame.K_DOWN or event.key == pygame.K_LEFT or
                            event.key == pygame.K_RIGHT):
                        MainGame.my_tank.switch = False


class Tank(BaseItem):
    """
    1.保存加载的图片，pygame.image.load(filename)-> Surface
    2.根据当前图片的方向获取图片(->Surface)，再根据返回的Surface获取区域，pygame.Rect：用于存储矩形坐标的pygame对象
    pygame.Surface.get_rect：返回一个覆盖整个表面的新矩形.该矩形将始终以(0,0)为起点，宽度和高度与图像大小相同
    矩形区域对于处理碰撞检测和定位坦克在游戏窗口中的位置非常有用
    3.对坦克移动超出边界情况进行处理，注意使距离与速度能够整除，防止出现一半在边界内一半在外的情况
    4.增加长按按键功能---不在getEvent()方法中单次调用move_Tank()方法，而是把它放到循环中.然后继续优化使之---按下移动，松开不移动
      新增开关属性switch，当按下键时在getEvent()方法中对开关进行修改，松开方向键，坦克停止移动，修改开关状态
    """

    def __init__(self, left, top):
        super().__init__()
        self.images = \
            {
                'U': pygame.image.load('image/p1tankU.gif'),
                'D': pygame.image.load('image/p1tankD.gif'),
                'L': pygame.image.load('image/p1tankL.gif'),
                'R': pygame.image.load('image/p1tankR.gif')
            }
        self.direction = 'U'
        self.image = self.images[self.direction]
        self.rect = self.image.get_rect()
        self.rect.left = left
        self.rect.top = top
        self.speed = 6
        self.switch = False
        self.live = True
        self.oldleft = self.rect.left
        self.oldtop = self.rect.top

    def move_Tank(self):
        """判断坦克的方向并进行移动"""
        self.oldleft = self.rect.left
        self.oldtop = self.rect.top
        if self.direction == 'L':
            if self.rect.left > 0:
                self.rect.left -= self.speed
        elif self.direction == 'U':
            if self.rect.top > 0:
                self.rect.top -= self.speed
        elif self.direction == 'D':
            if self.rect.top + self.rect.height < SCREEN_HEIGHT:
                self.rect.top += self.speed
        elif self.direction == 'R':
            if self.rect.left + self.rect.height < SCREEN_WIDTH:
                self.rect.left += self.speed

    def shot(self):
        return Bullet(self)

    def stay(self):
        self.rect.left = self.oldleft
        self.rect.top = self.oldtop

    def Tank_hit_Wall(self):
        """当坦克撞墙时，将坦克坐标设置为移动之前的坐标"""
        for wall in MainGame.wallList:
            if pygame.sprite.collide_rect(self, wall):
                self.stay()

    def displayTank(self):
        self.image = self.images[self.direction]
        MainGame.window.blit(self.image, self.rect)


class MyTank(Tank):
    """检测我方坦克与敌方坦克发生碰撞"""
    def __int__(self, left, top):
        super().__init__(left, top)

    def myTank_hit_enemyTank(self):
        for enemyTank in MainGame.enemyTankList:
            if pygame.sprite.collide_rect(self, enemyTank):
                self.stay()


class EnemyTank(Tank):
    """敌方坦克类"""

    def __init__(self, left, top, speed):
        super().__init__(left, top)
        self.images = \
            {
                'U': pygame.image.load('image/enemy1U.gif'),
                'D': pygame.image.load('image/enemy1D.gif'),
                'L': pygame.image.load('image/enemy1L.gif'),
                'R': pygame.image.load('image/enemy1R.gif')
            }
        self.direction = self.randDirection()
        self.image = self.images[self.direction]
        self.rect = self.image.get_rect()
        self.rect.left = left
        self.rect.top = top
        self.speed = speed
        self.switch = False
        self.step = 60

    def enemyTank_hit_myTank(self):
        if pygame.sprite.collide_rect(self, MainGame.my_tank):
            self.stay()

    @staticmethod
    def randDirection():
        num = random.randint(1, 4)
        if num == 1:
            return 'U'
        elif num == 2:
            return 'D'
        elif num == 3:
            return 'L'
        elif num == 4:
            return 'R'

    def randMove(self):
        """敌方坦克随机移动思路：新增步数属性，移动时步数递减，当步数<=0时修改敌方坦克方向，同时让步数复位"""
        if self.step <= 0:
            self.direction = self.randDirection()
            self.step = 60
        else:
            self.move_Tank()
            self.step -= 1

    def shot(self):
        """重写shot()方法,但会引发新问题，即并非每次调用重写的该方法时都返回Bullet类对象，NoneType也会存入列表中,新增存入列表元素不为None的判断即可"""
        num = random.randint(0, 350)
        if num < 10:
            return Bullet(self)


class Bullet(BaseItem):
    def __init__(self, tank):
        """坦克(炮管)的方向决定子弹的方向
        新增子弹的状态属性live，是否碰到墙壁，如果碰到墙壁，修改此状态"""
        super().__init__()
        self.image = pygame.image.load('image/enemymissile.gif')
        self.direction = tank.direction
        self.rect = self.image.get_rect()
        if self.direction == 'U':
            self.rect.left = tank.rect.left + tank.rect.width / 2 - self.rect.width / 2
            self.rect.top = tank.rect.top - self.rect.height
        elif self.direction == 'D':
            self.rect.left = tank.rect.left + tank.rect.width / 2 - self.rect.width / 2
            self.rect.top = tank.rect.top + tank.rect.height
        elif self.direction == 'L':
            self.rect.left = tank.rect.left - self.rect.height
            self.rect.top = tank.rect.top + tank.rect.width / 2 - self.rect.width / 2
        elif self.direction == 'R':
            self.rect.left = tank.rect.left + self.rect.height
            self.rect.top = tank.rect.top + tank.rect.width / 2 - self.rect.width / 2
        self.speed = 6
        self.live = True

    def move_Bullet(self):
        if self.direction == 'L':
            if self.rect.left > 0:
                self.rect.left -= self.speed
            else:
                self.live = False
        elif self.direction == 'U':
            if self.rect.top > 0:
                self.rect.top -= self.speed
            else:
                self.live = False
        elif self.direction == 'D':
            if self.rect.top + self.rect.height < SCREEN_HEIGHT:
                self.rect.top += self.speed
            else:
                self.live = False
        elif self.direction == 'R':
            if self.rect.left + self.rect.width < SCREEN_WIDTH:
                self.rect.left += self.speed
            else:
                self.live = False

    def displayBullet(self):
        MainGame.window.blit(self.image, self.rect)

    def hitWall(self):
        for wall in MainGame.wallList:
            if pygame.sprite.collide_rect(self, wall):
                self.live = False
                wall.hp -= 1
                if wall.hp <= 0:
                    wall.live = False

    def myBullet_hit_enemyTank(self):
        """循环遍历敌方坦克列表，判断我方子弹与敌方坦克是否发生碰撞
        pygame.sprite.collide_rect(left, right)-> bool，使用矩形检测两个精灵之间的碰撞，精灵必须具有"rect"属性"""
        for enemyTank in MainGame.enemyTankList:
            if pygame.sprite.collide_rect(enemyTank, self):
                enemyTank.live = False
                self.live = False
                explode = Explode(enemyTank)
                MainGame.explodeList.append(explode)

    def enemyBullet_hit_myTank(self):
        if MainGame.my_tank and MainGame.my_tank.live:
            if pygame.sprite.collide_rect(MainGame.my_tank, self):
                MainGame.my_tank.live = False
                self.live = False
                explode = Explode(MainGame.my_tank)
                MainGame.explodeList.append(explode)


class Wall:
    def __init__(self, left, top):
        self.image = pygame.image.load('image/steels.gif')
        self.rect = self.image.get_rect()
        self.rect.left = left
        self.rect.top = top
        self.live = True
        self.hp = 4

    def displayWall(self):
        MainGame.window.blit(self.image, self.rect)


class Explode:
    """爆炸效果类----爆炸的位置由当前子弹打中的坦克位置决定"""

    def __init__(self, tank):
        self.rect = tank.rect
        self.images = \
            [
                pygame.image.load('image/blast0.gif'),
                pygame.image.load('image/blast1.gif'),
                pygame.image.load('image/blast2.gif'),
                pygame.image.load('image/blast3.gif'),
                pygame.image.load('image/blast4.gif'),
            ]
        self.index = 0
        self.image = self.images[self.index]
        self.live = True

    def displayExplide(self):
        """根据索引获取爆炸对象，再添加到主窗口"""
        if self.index < len(self.images):
            self.image = self.images[self.index]
            self.index += 1
            MainGame.window.blit(self.image, self.rect)
        else:
            self.live = False
            self.index = 0


class Music:
    def __init__(self, filename):
        self.filename = filename
        pygame.mixer.init()
        pygame.mixer.music.load(self.filename)

    @staticmethod
    def play():
        pygame.mixer.music.play()


if __name__ == '__main__':
    MainGame().startGame()
    # MainGame().getTextSurface()
