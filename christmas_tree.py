import pygame  # 导入 pygame 游戏库，用于绘图和交互
import random  # 导入随机数库，用于随机位置、颜色和速度
import win32gui  # 导入 Windows 窗口操作库
import win32con  # 导入 Windows 常量库（如窗口样式标志）
import win32api  # 导入 Windows 系统 API 接口
import os      # 导入系统库，用于处理文件路径
import sys     # 导入系统库，用于获取运行环境信息

# --- 0. 打包路径兼容函数 (关键步骤) ---
def resource_path(relative_path):
    """
    获取资源的绝对路径，兼容 PyInstaller 打包后的路径。
    打包成单个 EXE 时，资源会被解压到一个临时文件夹中，
    该函数能确保程序无论在开发环境还是打包后都能找到素材。
    """
    if hasattr(sys, '_MEIPASS'):
        # 如果是 PyInstaller 运行环境，路径指向临时解压目录
        return os.path.join(sys._MEIPASS, relative_path)
    # 如果是普通的 Python 运行环境，路径指向当前文件夹
    return os.path.join(os.path.abspath("."), relative_path)

# --- 1. 初始化与窗口设置 ---
pygame.init()  # 初始化 pygame 所有的模块
pygame.mixer.init()  # 特别初始化音频混音器（用于放歌）

info = pygame.display.Info()  # 获取当前显示器的分辨率信息
WIDTH, HEIGHT = info.current_w, info.current_h  # 设置窗口宽高为全屏
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME | pygame.RESIZABLE)  # 创建无边框且可调节大小的窗口

# 设置窗口透明和置顶 (Windows 系统专用)
hwnd = pygame.display.get_wm_info()['window']  # 获取 pygame 窗口的句柄（窗口身份证）
# 设置窗口样式为分层窗口（LAYERED），这是实现透明的前提
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                       win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
MAGIC_COLOR = (10, 10, 10)  # 定义一种特殊的黑色作为透明通道色
# 将窗口中所有颜色为 MAGIC_COLOR 的部分设为完全透明
# noinspection PyUnresolvedReferences
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*MAGIC_COLOR), 0, win32con.LWA_COLORKEY)
# 将窗口设为“永远置顶”，确保它在其他软件上面
win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

# --- 2. 音乐播放 ---
try:
    # 注意：所有文件路径都要用 resource_path() 包裹起来
    pygame.mixer.music.load(resource_path('static/last_christmas.mp3'))
    pygame.mixer.music.set_volume(0.5)  # 设置背景音乐音量 (0.0 到 1.0)
    pygame.mixer.music.play(-1)  # 开始播放，-1 代表无限循环
except Exception as e:
    print(f"音乐加载失败: {e}")

# --- 3. 颜色配置 ---
# 树木颜色参考
RAINBOW_COLORS = [(239, 66, 76), (236, 93, 16), (183, 200, 203), (154, 203, 52), (40, 91, 212), (227, 166, 174), (249, 82, 122), (255, 111, 97), (110, 206, 218), (255, 209, 102), (6, 214, 160), (17, 138, 178), (7, 59, 76)]
# 烟花专用颜色：暖黄、淡青、浅粉等
FIREWORK_COLORS = [(230, 230, 230), (252, 236, 131), (190, 230, 222), (252, 93, 93), (140, 128, 128)]

SCALE_BASIC = 6  # 圣诞树基础缩放倍率
TRUNK_SLIM_X = 3  # 树干横向额外缩小的倍率（让树干变细）
SNOW_STRETCH_X = 3.5  # 底部雪堆横向拉伸倍率（让雪堆变宽扁）

def load_part(path, scale_y, extra_scale_x=1):
    """通用图片加载函数：加载 -> 计算缩放尺寸 -> 平滑缩放"""
    try:
        # 使用 resource_path 确保打包后能找到图片
        img = pygame.image.load(resource_path(path)).convert_alpha()
        w, h = img.get_size()  # 获取原图尺寸
        new_w = int(w / (scale_y / extra_scale_x))  # 计算缩放后的宽度
        new_h = int(h / scale_y)  # 计算缩放后的高度
        return pygame.transform.smoothscale(img, (new_w, new_h))  # 返回缩放后的高质量图片
    except Exception as exception:
        print(f"加载图片失败 ({path}): {exception}")
        s = pygame.Surface((50, 50), pygame.SRCALPHA)  # 加载失败时创建一个灰色方块占位
        pygame.draw.rect(s, (200, 200, 200), s.get_rect())
        return s

# 加载树冠、树干和雪基座图片
crown_img = load_part('static/crown.png', SCALE_BASIC)
# noinspection PyTypeChecker
trunk_img = load_part('static/trunk.png', SCALE_BASIC, 1 / TRUNK_SLIM_X)
# noinspection PyTypeChecker
snow_img = load_part('static/snow.png', SCALE_BASIC, SNOW_STRETCH_X)

try:
    snowflake_raw = pygame.image.load(resource_path('static/snowflake.png')).convert_alpha()  # 加载雪花素材
except:
    snowflake_raw = pygame.Surface((20, 20), pygame.SRCALPHA)  # 加载失败则手动画一个白点
    pygame.draw.circle(snowflake_raw, (255, 255, 255), (10, 10), 10)

# --- 4. 圣诞场景类 ---
class ChristmasTree:
    """定义单棵圣诞树的属性和绘制逻辑"""
    def __init__(self, bottom_center_x):
        self.t_rect = trunk_img.get_rect()
        self.c_rect = crown_img.get_rect()
        self.s_rect = snow_img.get_rect()
        # 计算位置
        self.s_x = bottom_center_x - self.s_rect.width // 2
        self.s_y = HEIGHT - self.s_rect.height
        self.t_x = bottom_center_x - self.t_rect.width // 2
        self.t_y = HEIGHT - self.t_rect.height - (self.s_rect.height // 4)
        self.c_x = bottom_center_x - self.c_rect.width // 2
        self.c_y = self.t_y - self.c_rect.height + 100

    def draw(self, surface):
        surface.blit(snow_img, (self.s_x, self.s_y))
        surface.blit(trunk_img, (self.t_x, self.t_y))
        surface.blit(crown_img, (self.c_x, self.c_y))

class Snowflake:
    """定义单片雪花的下落逻辑"""
    def __init__(self):
        self.reset()
        self.y = random.randint(0, HEIGHT)
    def reset(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-100, -10)
        self.size = random.randint(15, 35)
        self.speed = random.uniform(0.7, 2.0)
    def update(self):
        self.y += self.speed
        if self.y > HEIGHT: self.reset()
    def draw(self, surface):
        s_img = pygame.transform.scale(snowflake_raw, (self.size, self.size))
        surface.blit(s_img, (self.x, self.y))

class ChristmasScene:
    """管理整个场景：包含多棵树和雪花群"""
    def __init__(self, tree_count=18):
        self.trees = [ChristmasTree(random.randint(100, WIDTH - 100)) for _ in range(tree_count)]
        # 按照 Y 坐标排序，实现近大远小和正确遮挡
        self.trees.sort(key=lambda t: t.s_y)
        self.snowflakes = [Snowflake() for _ in range(80)]
    def update(self):
        for s in self.snowflakes: s.update()
    def draw(self, surface):
        for tree in self.trees: tree.draw(surface)
        for s in self.snowflakes: s.draw(surface)

# --- 5. 垂柳烟花类设计 ---
class FireworkParticle:
    """烟花爆炸后的单根‘柳条’粒子"""
    def __init__(self, x, y, color):
        self.path = [(x, y)]  # 线条位置历史
        self.color = color
        self.vx = random.uniform(-6.0, 6.0)  # 水平冲力（决定了 X 轴宽度）
        self.vy = random.uniform(-4.5, 1.5)  # 纵向冲力
        self.alpha = 255  # 透明度
        self.gravity = 0.038  # 重力
        self.max_path_len = 25  # 柳条长度

    def update(self):
        curr_x, curr_y = self.path[-1]
        new_x, new_y = curr_x + self.vx, curr_y + self.vy
        self.vy += self.gravity  # 重力影响
        self.vx *= 0.99  # 空气阻力
        self.path.append((new_x, new_y))
        if len(self.path) > self.max_path_len: self.path.pop(0)
        self.alpha -= 1.3  # 逐渐变透明
        if self.alpha < 0: self.alpha = 0

    def draw(self, surface):
        if self.alpha <= 0 or len(self.path) < 2: return
        for i in range(len(self.path) - 1):
            p1, p2 = self.path[i], self.path[i+1]
            local_alpha = int(self.alpha * (i / len(self.path)))
            pygame.draw.line(surface, (*self.color, local_alpha), p1, p2, 2)

class Firework:
    """烟花生命周期管理"""
    def __init__(self):
        self.reset()
    def reset(self):
        self.x = random.randint(WIDTH // 6, WIDTH * 5 // 6)
        self.y = HEIGHT
        self.speed = random.uniform(6, 11)
        self.colors = random.sample(FIREWORK_COLORS, random.randint(1, 3))
        self.exploded = False
        self.particles = []
        self.trail = []
    def update(self):
        if not self.exploded:
            self.y -= self.speed
            self.trail.append([self.x, self.y, 255])
            for t in self.trail: t[2] -= 12
            self.trail = [t for t in self.trail if t[2] > 0]
            if self.y <= HEIGHT * 0.35:
                self.exploded = True
                for _ in range(130):
                    self.particles.append(FireworkParticle(self.x, self.y, random.choice(self.colors)))
        else:
            for p in self.particles: p.update()
            if not any(p.alpha > 0 for p in self.particles): self.reset()
    def draw(self, surface):
        if not self.exploded:
            for t in self.trail:
                pygame.draw.circle(surface, (255, 255, 255, t[2]), (int(t[0]), int(t[1])), 2)
            pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), 3)
        else:
            for p in self.particles: p.draw(surface)

# --- 6. 主程序运行 ---
scene = ChristmasScene(tree_count=18)
fireworks = [Firework() for _ in range(4)]
clock = pygame.time.Clock()
font = pygame.font.SysFont('SimHei', 18)
running = True

# 预设按钮矩形
exit_btn_rect = pygame.Rect(0, 0, 0, 0)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 按钮点击逻辑
            if exit_btn_rect.collidepoint(event.pos): running = False

    screen.fill(MAGIC_COLOR)  # 清除上一帧
    CUR_W, CUR_H = screen.get_size()

    # UI 位置计算
    panel_w, panel_h = 200, 100
    margin = 20
    cw_x, cw_y = CUR_W - panel_w - margin, CUR_H - panel_h - margin
    exit_btn_rect = pygame.Rect(cw_x + 45, cw_y + 42, 110, 32)

    # 1. 绘制烟花 (最底层)
    for fw in fireworks:
        fw.update()
        fw.draw(screen)

    # 2. 绘制场景 (覆盖烟花)
    scene.update()
    scene.draw(screen)

    # 3. 绘制 UI 面板 (最顶层)
    pygame.draw.rect(screen, (20, 50, 20), (cw_x, cw_y, panel_w, panel_h), border_radius=12)
    pygame.draw.rect(screen, (212, 175, 55), (cw_x, cw_y, panel_w, panel_h), 2, border_radius=12)
    txt = font.render("点击下方按钮退出", True, (255, 255, 255))
    screen.blit(txt, txt.get_rect(center=(cw_x + panel_w // 2, cw_y + 22)))
    pygame.draw.rect(screen, (180, 40, 40), exit_btn_rect, border_radius=6)
    btn_txt = font.render("退出程序", True, (255, 255, 255))
    screen.blit(btn_txt, btn_txt.get_rect(center=exit_btn_rect.center))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()