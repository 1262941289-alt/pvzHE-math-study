# 文件内容搜索引擎 🔍

一个功能强大的文件内容搜索工具，支持多种搜索模式和输出格式。

---

## ✨ 主要功能

### 🔹 搜索模式
- **关键词搜索**: 精确或模糊匹配关键词
- **正则表达式搜索**: 支持复杂的模式匹配
- **多关键词搜索**: 支持 AND/OR 逻辑操作
- **模糊搜索**: 基于相似度的智能匹配

### 🔹 输出格式
- **控制台输出**: 彩色格式化显示
- **JSON格式**: 便于程序处理
- **HTML报告**: 美观的网页格式
- **Web界面**: 直观的浏览器操作

### 🔹 高级特性
- 自动编码检测
- 上下文行显示
- 文件类型过滤
- 目录排除功能
- 大小写敏感选项
- 全词匹配模式

---

## 🚀 快速开始

### 安装依赖

```bash
pip install chardet flask
```

### 基本使用

#### 1. 命令行搜索

```bash
# 关键词搜索
python search_engine.py -k "函数" -p "数学"

# 正则表达式搜索
python search_engine.py -r "def\s+\w+" -e py

# 多关键词搜索
python search_engine.py -m "原函数" "积分" -o AND

# 模糊搜索
python search_engine.py -f "不定积分" -t 0.7
```

#### 2. Web界面搜索

```bash
# 启动Web服务
python search_web.py

# 浏览器访问
http://localhost:5000
```

---

## 📋 命令行参数详解

### 搜索模式参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `-k, --keyword` | 关键词搜索 | `-k "函数定义"` |
| `-r, --regex` | 正则表达式搜索 | `-r "def\s+\w+"` |
| `-m, --multiple` | 多关键词搜索 | `-m "函数" "定义"` |
| `-f, --fuzzy` | 模糊搜索 | `-f "不定积分"` |

### 搜索选项参数

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `-p, --path` | 搜索路径 | 当前目录 | `-p "/home/user/docs"` |
| `-e, --extensions` | 文件扩展名过滤 | 所有支持的类型 | `-e py js md` |
| `-x, --exclude` | 排除目录 | .git, __pycache__ 等 | `-x .git node_modules` |
| `-c, --context` | 上下文行数 | 0 | `-c 3` |
| `-i, --ignore-case` | 忽略大小写 | False | `-i` |
| `-w, --whole-word` | 全词匹配 | False | `-w` |
| `-o, --operator` | 多关键词操作符 | AND | `-o OR` |
| `-t, --threshold` | 模糊搜索阈值 | 0.6 | `-t 0.8` |

### 输出选项参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--json` | 输出JSON格式 | `--json > result.json` |
| `--html` | 输出HTML文件 | `--html result.html` |
| `--max-results` | 最大结果数量 | `--max-results 50` |
| `--no-context` | 不显示上下文 | `--no-context` |

---

## 💡 使用示例

### 示例1: 搜索Python函数定义

```bash
python search_engine.py -r "def\s+\w+\(" -e py -c 2
```

**说明**: 在Python文件中搜索函数定义，显示2行上下文

### 示例2: 搜索数学相关内容

```bash
python search_engine.py -m "函数" "导数" "积分" -o OR -p "数学" -i
```

**说明**: 在数学目录下搜索包含"函数"、"导数"或"积分"的内容，忽略大小写

### 示例3: 模糊搜索并输出HTML

```bash
python search_engine.py -f "微积分" -t 0.7 --html result.html
```

**说明**: 模糊搜索"微积分"相关内容，相似度阈值0.7，输出HTML报告

### 示例4: 搜索配置文件

```bash
python search_engine.py -k "port" -e json yml yaml ini cfg -w
```

**说明**: 在配置文件中搜索"port"关键词，使用全词匹配

---

## 🌐 Web界面功能

### 功能特点
- 🎨 现代化UI设计
- 📱 响应式布局
- ⚡ 实时搜索结果
- 🔧 丰富的搜索选项
- 📊 结果统计显示

### 使用步骤
1. 启动Web服务: `python search_web.py`
2. 打开浏览器访问: `http://localhost:5000`
3. 输入搜索内容和选项
4. 点击"开始搜索"查看结果

---

## 📁 支持的文件类型

### 文本文件
- `.txt` - 纯文本文件
- `.md` - Markdown文档
- `.json` - JSON数据文件
- `.xml` - XML文档
- `.yml`, `.yaml` - YAML配置文件

### 编程语言
- `.py` - Python
- `.js` - JavaScript
- `.html` - HTML
- `.css` - CSS
- `.java` - Java
- `.cpp`, `.c`, `.h` - C/C++
- `.cs` - C#
- `.php` - PHP
- `.rb` - Ruby
- `.go` - Go
- `.rs` - Rust
- `.swift` - Swift
- `.kt` - Kotlin
- `.scala` - Scala

### 脚本和配置
- `.sh` - Shell脚本
- `.bat` - 批处理文件
- `.ini`, `.cfg`, `.conf` - 配置文件

---

## ⚙️ 高级配置

### 自定义文件类型

可以通过修改 `FileSearchEngine` 类中的 `supported_extensions` 属性来添加更多文件类型：

```python
engine = FileSearchEngine()
engine.supported_extensions.add('.log')  # 添加日志文件支持
```

### 性能优化

对于大型项目，建议：
1. 使用文件扩展名过滤 (`-e` 参数)
2. 排除不必要的目录 (`-x` 参数)
3. 限制结果数量 (`--max-results` 参数)
4. 减少上下文行数 (`-c` 参数)

---

## 🔧 故障排除

### 常见问题

**Q: 搜索结果为空？**
A: 检查搜索路径、文件扩展名过滤和关键词拼写

**Q: 中文搜索乱码？**
A: 工具会自动检测文件编码，如仍有问题请检查文件编码格式

**Q: 正则表达式报错？**
A: 检查正则表达式语法，可以使用在线工具验证

**Q: Web界面无法访问？**
A: 确保Flask已安装，检查端口5000是否被占用

### 性能建议

- 大文件搜索时适当增加上下文行数
- 使用具体的文件扩展名过滤提高搜索速度
- 排除不相关的目录减少搜索范围

---

## 📄 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个工具！

### 开发环境设置

```bash
git clone <repository>
cd file-search-engine
pip install -r requirements.txt
```

### 运行测试

```bash
python -m pytest tests/
```

---

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 📧 Email: your-email@example.com
- 🐛 Issues: GitHub Issues
- 💬 讨论: GitHub Discussions

---

**享受高效的文件搜索体验！** 🎉
