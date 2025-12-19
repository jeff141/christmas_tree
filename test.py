RAINBOW_COLORS_HEX = [  # 定义烟花随机颜色的十六进制列表
    '#E6E6E6','#FCEC83','#BEE6DE','#FC5D5D','#8C8080'
]
def hex_to_rgb(hex_str):
    """将字符串格式的颜色 '#RRGGBB' 转换为 Pygame 需要的 (R, G, B) 元组"""
    hex_str = hex_str.lstrip('#')  # 去掉 # 号
    return tuple(int(hex_str[i:i + 2], 16) for i in (0, 2, 4))  # 每两位转为一个 10 进制整数


# 将所有十六进制颜色预先转换好备用
RAINBOW_COLORS = [hex_to_rgb(c) for c in RAINBOW_COLORS_HEX]
print(RAINBOW_COLORS)