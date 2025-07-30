# AI助手知识库使用指南

## 目录结构
```
.ai_knowledge/
├── config/
│   └── system.json          # 系统配置
├── rules/
│   ├── core_rules.json      # 核心规则
│   └── user_rules.json      # 用户自定义规则
├── preferences/
│   └── user_preferences.json # 用户偏好
├── patterns/
│   └── (模式文件)
├── context/
│   └── project_context.json  # 项目上下文
├── knowledge_manager.py      # 管理脚本
└── README.md               # 本文档
```

## 基本使用方法

### 1. 查看当前知识库内容
```bash
python .ai_knowledge/knowledge_manager.py
```

### 2. 添加新规则
在Python中：
```python
from knowledge_manager import KnowledgeManager
km = KnowledgeManager()
km.add_rule("新的规则内容", priority=8)
```

### 3. 添加新偏好
```python
km.add_preference("编程语言", "Python", weight=0.9, description="优先使用Python")
```

## 文件格式说明

### 规则文件格式
```json
{
  "id": "规则组ID",
  "type": "prohibition|requirement|guideline",
  "category": "分类",
  "title": "标题",
  "rules": [
    {
      "id": "规则ID",
      "content": "规则内容",
      "priority": 1-10,
      "active": true,
      "created_at": "创建时间"
    }
  ]
}
```

### 偏好文件格式
```json
{
  "preferences": [
    {
      "key": "偏好键",
      "value": "偏好值", 
      "weight": 0.0-1.0,
      "description": "描述"
    }
  ]
}
```

## 使用场景

### 场景1：记住用户要求
当用户说"请记住：不要生成测试代码"时：
1. 调用 `km.add_rule("不要生成测试代码", priority=9)`
2. 规则自动保存到知识库
3. 以后AI会自动遵守这个规则

### 场景2：记住用户偏好
当用户说"我喜欢简洁的代码风格"时：
1. 调用 `km.add_preference("代码风格", "简洁", weight=0.8)`
2. 偏好自动保存
3. AI会根据这个偏好调整回答

## 注意事项

1. **文件编码**：所有JSON文件使用UTF-8编码
2. **备份**：定期备份知识库文件
3. **权限**：确保AI助手有读写权限
4. **版本控制**：建议将知识库纳入版本控制

## 扩展功能

### 自动加载
AI助手启动时自动加载知识库内容

### 智能搜索
根据关键词搜索相关规则和偏好

### 冲突检测
检测规则之间的冲突并提醒用户
