# GitHub仓库设置指南

## 🎯 目标
建立GitHub仓库来强化记忆功能，实现学习资料的版本控制和云端备份。

## 📋 前置条件
- 已安装Git
- 拥有GitHub账号
- 当前在 `d:\pvzHE` 目录中

## 🔧 详细步骤

### 1. 本地Git仓库初始化
```bash
# 进入项目目录
cd d:\pvzHE

# 初始化Git仓库
git init

# 配置用户信息（请替换为您的信息）
git config user.name "您的GitHub用户名"
git config user.email "您的GitHub邮箱"
```

### 2. 在GitHub创建远程仓库
1. 访问 https://github.com
2. 登录您的账号
3. 点击右上角 "+" → "New repository"
4. 填写仓库信息：
   - Repository name: `pvzHE-math-study`
   - Description: `数学学习资料和MCP协议管理`
   - 选择 "Private"（保护学习资料隐私）
   - **不要**勾选 "Add a README file"
   - **不要**勾选 "Add .gitignore"
   - **不要**勾选 "Choose a license"
5. 点击 "Create repository"

### 3. 连接本地和远程仓库
```bash
# 添加远程仓库（替换为您的实际用户名）
git remote add origin https://github.com/您的用户名/pvzHE-math-study.git

# 设置主分支名称
git branch -M main

# 验证远程仓库连接
git remote -v
```

### 4. 准备和提交文件
```bash
# 检查当前状态
git status

# 添加重要文件到版本控制
git add .gitignore
git add 数学/
git add *.py
git add *.md
git add *.json
git add *.vim
git add *.code-snippets

# 检查将要提交的文件
git status

# 创建初始提交
git commit -m "Initial commit: 数学学习资料和MCP协议文档"
```

### 5. 推送到GitHub
```bash
# 首次推送到远程仓库
git push -u origin main

# 验证推送成功
git log --oneline -5
```

### 6. 验证设置
```bash
# 运行测试脚本
python test_github_memory_setup.py
```

## 🧠 记忆功能强化

设置完成后，记忆功能将得到以下强化：

### 本地记忆
- `记忆` MCP工具可以在Git根目录中正常工作
- 存储学习规则、偏好和上下文信息
- 支持项目级别的知识管理

### 云端备份
- 学习资料自动备份到GitHub
- 版本历史完整保存
- 多设备同步学习进度

### 协作增强
- MCP协议文档版本控制
- 学习笔记的迭代改进
- 知识库的持续优化

## 🔍 常见问题

### Q: 推送时要求输入用户名密码怎么办？
A: GitHub已不支持密码认证，需要使用Personal Access Token：
1. 访问 GitHub Settings → Developer settings → Personal access tokens
2. 生成新的token，选择适当的权限
3. 使用token替代密码进行认证

### Q: 如何处理大文件？
A: 已在.gitignore中排除了大文件（PDF、图片等），只保留重要的文档和代码。

### Q: 如何同步多设备？
A: 在其他设备上使用：
```bash
git clone https://github.com/您的用户名/pvzHE-math-study.git
```

## 📝 下一步操作

1. **验证设置**：运行 `python test_github_memory_setup.py`
2. **测试记忆功能**：使用 `记忆` MCP工具存储一些测试信息
3. **优化协议**：根据使用情况调整AURA协议配置
4. **建立工作流**：制定定期提交和同步的习惯

## 🎉 完成标志

当以下条件都满足时，说明设置成功：
- ✅ 本地Git仓库已初始化
- ✅ 远程GitHub仓库已创建并连接
- ✅ 重要文件已提交并推送
- ✅ 测试脚本全部通过
- ✅ 记忆功能可以正常使用
