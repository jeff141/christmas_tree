# 圣诞树动画程序

> 🎄 一个用 Python 编写的 Windows 透明圣诞树动画工具，支持背景音乐、真透明窗口与置顶显示，营造节日氛围。

**作者：一坨肉**  
**邮箱：1561074588@qq.com**  
**开源协议：MIT（使用时请保留作者署名）**

---

### 安装依赖
 ```
pip install -r requirements.txt
```
### 打包成exe
```
pyinstaller -F -w --add-data "static;static" christmas_tree.py
```
## 

💡 说明：

请确保项目目录中包含 bgm.mp3（背景音乐）和 icon.ico（程序图标）；
使用 --windowed 避免弹出黑框；
程序依赖 Windows 特有 API（如 win32gui），仅支持 Windows 系统运行。



## License
This project is licensed under the MIT License - see the LICENSE file for details.

© 2025 一坨肉. All rights reserved.