#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VSCode集成模块
为搜索引擎提供VSCode工作区集成功能
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from search_engine import FileSearchEngine, SearchResult

class VSCodeIntegration:
    """VSCode集成类"""
    
    def __init__(self, workspace_path: str = "."):
        self.workspace_path = Path(workspace_path)
        self.search_engine = FileSearchEngine(workspace_path)
        
    def find_vscode_settings(self) -> Optional[Path]:
        """查找VSCode设置文件"""
        vscode_dir = self.workspace_path / ".vscode"
        if vscode_dir.exists():
            return vscode_dir
        return None
    
    def create_search_task(self, keyword: str, task_name: str = None) -> Dict:
        """创建VSCode任务配置"""
        if task_name is None:
            task_name = f"搜索: {keyword}"
        
        task = {
            "label": task_name,
            "type": "shell",
            "command": "python",
            "args": [
                "search_engine.py",
                "-k", keyword,
                "--interactive"
            ],
            "group": "build",
            "presentation": {
                "echo": True,
                "reveal": "always",
                "focus": False,
                "panel": "new"
            },
            "problemMatcher": []
        }
        return task
    
    def update_tasks_json(self, search_tasks: List[Dict]):
        """更新tasks.json文件"""
        vscode_dir = self.find_vscode_settings()
        if not vscode_dir:
            vscode_dir = self.workspace_path / ".vscode"
            vscode_dir.mkdir(exist_ok=True)
        
        tasks_file = vscode_dir / "tasks.json"
        
        # 读取现有任务
        existing_tasks = {"version": "2.0.0", "tasks": []}
        if tasks_file.exists():
            try:
                with open(tasks_file, 'r', encoding='utf-8') as f:
                    existing_tasks = json.load(f)
            except json.JSONDecodeError:
                pass
        
        # 添加搜索任务
        if "tasks" not in existing_tasks:
            existing_tasks["tasks"] = []
        
        # 移除旧的搜索任务
        existing_tasks["tasks"] = [
            task for task in existing_tasks["tasks"] 
            if not task.get("label", "").startswith("搜索:")
        ]
        
        # 添加新的搜索任务
        existing_tasks["tasks"].extend(search_tasks)
        
        # 保存文件
        with open(tasks_file, 'w', encoding='utf-8') as f:
            json.dump(existing_tasks, f, indent=2, ensure_ascii=False)
        
        return tasks_file
    
    def create_search_snippets(self) -> Dict:
        """创建搜索相关的代码片段"""
        snippets = {
            "搜索文件内容": {
                "prefix": "search",
                "body": [
                    "# 搜索文件内容",
                    "python search_engine.py -k \"$1\" -p \"$2\" --interactive"
                ],
                "description": "搜索文件内容的命令"
            },
            "正则搜索": {
                "prefix": "regex-search",
                "body": [
                    "# 正则表达式搜索",
                    "python search_engine.py -r \"$1\" -p \"$2\" -c 2"
                ],
                "description": "使用正则表达式搜索"
            },
            "多关键词搜索": {
                "prefix": "multi-search",
                "body": [
                    "# 多关键词搜索",
                    "python search_engine.py -m \"$1\" \"$2\" -o AND --interactive"
                ],
                "description": "多关键词搜索"
            }
        }
        return snippets
    
    def update_snippets(self):
        """更新代码片段"""
        vscode_dir = self.find_vscode_settings()
        if not vscode_dir:
            vscode_dir = self.workspace_path / ".vscode"
            vscode_dir.mkdir(exist_ok=True)
        
        snippets_file = vscode_dir / "search.code-snippets"
        snippets = self.create_search_snippets()
        
        with open(snippets_file, 'w', encoding='utf-8') as f:
            json.dump(snippets, f, indent=2, ensure_ascii=False)
        
        return snippets_file
    
    def create_keybindings(self) -> List[Dict]:
        """创建快捷键绑定"""
        keybindings = [
            {
                "key": "ctrl+shift+f",
                "command": "workbench.action.tasks.runTask",
                "args": "搜索: 快速搜索"
            },
            {
                "key": "ctrl+shift+r",
                "command": "workbench.action.tasks.runTask", 
                "args": "搜索: 正则搜索"
            }
        ]
        return keybindings
    
    def setup_workspace(self, common_searches: List[str] = None):
        """设置VSCode工作区集成"""
        if common_searches is None:
            common_searches = ["函数", "定义", "TODO", "FIXME", "BUG"]
        
        print("🔧 设置VSCode工作区集成...")
        
        # 创建搜索任务
        search_tasks = []
        for keyword in common_searches:
            task = self.create_search_task(keyword)
            search_tasks.append(task)
        
        # 添加通用搜索任务
        general_task = {
            "label": "搜索: 自定义",
            "type": "shell",
            "command": "python",
            "args": [
                "search_engine.py",
                "-k", "${input:searchKeyword}",
                "--interactive"
            ],
            "group": "build",
            "presentation": {
                "echo": True,
                "reveal": "always",
                "focus": False,
                "panel": "new"
            },
            "problemMatcher": []
        }
        search_tasks.append(general_task)
        
        # 更新tasks.json
        tasks_file = self.update_tasks_json(search_tasks)
        print(f"✅ 已更新任务配置: {tasks_file}")
        
        # 更新代码片段
        snippets_file = self.update_snippets()
        print(f"✅ 已更新代码片段: {snippets_file}")
        
        # 创建输入配置
        self.create_input_config()
        
        print("🎉 VSCode工作区集成设置完成！")
        print("\n💡 使用方法:")
        print("1. 按 Ctrl+Shift+P 打开命令面板")
        print("2. 输入 'Tasks: Run Task'")
        print("3. 选择搜索任务")
        print("4. 或者使用代码片段: 输入 'search' 然后按 Tab")
    
    def create_input_config(self):
        """创建输入配置"""
        vscode_dir = self.find_vscode_settings()
        if not vscode_dir:
            vscode_dir = self.workspace_path / ".vscode"
            vscode_dir.mkdir(exist_ok=True)
        
        # 更新tasks.json以包含输入配置
        tasks_file = vscode_dir / "tasks.json"
        
        if tasks_file.exists():
            with open(tasks_file, 'r', encoding='utf-8') as f:
                tasks_config = json.load(f)
        else:
            tasks_config = {"version": "2.0.0", "tasks": []}
        
        # 添加输入配置
        tasks_config["inputs"] = [
            {
                "id": "searchKeyword",
                "description": "输入搜索关键词",
                "default": "",
                "type": "promptString"
            }
        ]
        
        with open(tasks_file, 'w', encoding='utf-8') as f:
            json.dump(tasks_config, f, indent=2, ensure_ascii=False)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="VSCode工作区集成设置")
    parser.add_argument('-p', '--path', default='.', help='工作区路径')
    parser.add_argument('--setup', action='store_true', help='设置VSCode集成')
    parser.add_argument('--keywords', nargs='+', help='常用搜索关键词')
    
    args = parser.parse_args()
    
    integration = VSCodeIntegration(args.path)
    
    if args.setup:
        integration.setup_workspace(args.keywords)
    else:
        print("使用 --setup 参数来设置VSCode集成")
        print("例如: python vscode_integration.py --setup --keywords 函数 定义 TODO")

if __name__ == "__main__":
    main()
