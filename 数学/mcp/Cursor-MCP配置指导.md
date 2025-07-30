# Cursor MCP配置指导

## 🎯 **Cursor中配置MCP寸止工具**

### 📋 **检测到您使用的是Cursor IDE**

Cursor是基于VSCode的AI编程IDE，支持MCP协议，但配置方式略有不同。

### 🔧 **配置步骤**

#### 步骤1：打开Cursor设置
1. 在Cursor中按 `Ctrl+,` 打开设置
2. 或者按 `Ctrl+Shift+P` 然后输入 "Preferences: Open Settings (JSON)"

#### 步骤2：添加MCP配置
将`cursor-mcp-settings.json`中的内容添加到Cursor的settings.json中：

```json
{
  "mcp.servers": {
    "寸止": {
      "command": "python",
      "args": ["寸止.py"],
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}",
        "PYTHONIOENCODING": "utf-8"
      }
    }
  },
  "mcp.client": {
    "timeout": 30000,
    "retries": 3,
    "logLevel": "info",
    "autoReconnect": true
  }
}
```

#### 步骤3：检查MCP支持
1. 在Cursor中按 `Ctrl+Shift+P`
2. 搜索 "MCP" 相关命令
3. 如果没有找到，可能需要启用MCP功能

### 🔍 **Cursor MCP功能启用**

#### 方法1：通过设置启用
在settings.json中添加：
```json
{
  "mcp.enabled": true,
  "mcp.autoStart": true
}
```

#### 方法2：通过命令面板
1. 按 `Ctrl+Shift+P`
2. 输入 "MCP: Enable"
3. 选择启用MCP功能

### 🧪 **测试MCP连接**

#### 1. 重启Cursor
配置完成后重启Cursor以加载新配置

#### 2. 检查MCP状态
- 按 `Ctrl+Shift+P`
- 输入 "MCP: Show Status"
- 查看寸止服务器是否连接成功

#### 3. 测试寸止工具
- 按 `Ctrl+Shift+P`
- 输入 "MCP: List Tools"
- 应该能看到"寸止询问"和"寸止确认"工具

### ⚠️ **常见问题**

#### 问题1：找不到MCP命令
**解决方案**：
- 确保Cursor版本支持MCP
- 检查是否需要安装MCP扩展
- 尝试更新Cursor到最新版本

#### 问题2：Python路径错误
**解决方案**：
- 确保Python在系统PATH中
- 修改配置中的python命令为完整路径
- 检查工作目录设置

#### 问题3：编码问题
**解决方案**：
- 确保所有文件使用UTF-8编码
- 设置PYTHONIOENCODING环境变量

### 🎯 **下一步**

配置完成后，您应该能够：
1. 在Cursor中看到MCP工具列表
2. 使用寸止询问和寸止确认功能
3. 严格按照AURA-X协议进行AI交互

### 📞 **如果需要帮助**

如果在配置过程中遇到问题，请告诉我：
- Cursor的版本号
- 具体的错误信息
- MCP相关命令是否可用

我将根据具体情况提供进一步的帮助。
