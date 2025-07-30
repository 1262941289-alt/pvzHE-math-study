#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
编辑器搜索集成工具
将我们的搜索引擎集成到各种编辑器中
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List
from search_engine import FileSearchEngine

class EditorSearchIntegration:
    """编辑器搜索集成"""
    
    def __init__(self, workspace_path: str = "."):
        self.workspace_path = Path(workspace_path)
        self.search_engine = FileSearchEngine(workspace_path)
    
    def create_vscode_extension_config(self):
        """创建VSCode扩展配置"""
        vscode_dir = self.workspace_path / ".vscode"
        vscode_dir.mkdir(exist_ok=True)
        
        # 创建自定义命令
        commands_config = {
            "commands": [
                {
                    "command": "extension.advancedSearch",
                    "title": "高级搜索",
                    "category": "搜索"
                },
                {
                    "command": "extension.fuzzySearch", 
                    "title": "模糊搜索",
                    "category": "搜索"
                },
                {
                    "command": "extension.regexSearch",
                    "title": "正则搜索", 
                    "category": "搜索"
                }
            ],
            "keybindings": [
                {
                    "command": "extension.advancedSearch",
                    "key": "ctrl+alt+f",
                    "when": "editorTextFocus"
                },
                {
                    "command": "extension.fuzzySearch",
                    "key": "ctrl+alt+shift+f",
                    "when": "editorTextFocus"
                }
            ]
        }
        
        # 更新任务配置以支持编辑器搜索
        tasks_file = vscode_dir / "tasks.json"
        if tasks_file.exists():
            with open(tasks_file, 'r', encoding='utf-8') as f:
                tasks_config = json.load(f)
        else:
            tasks_config = {"version": "2.0.0", "tasks": []}
        
        # 添加编辑器搜索任务
        editor_search_tasks = [
            {
                "label": "编辑器搜索: 当前选中文本",
                "type": "shell",
                "command": "python",
                "args": [
                    "editor_search_integration.py",
                    "--search-selection"
                ],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": True,
                    "panel": "new"
                }
            },
            {
                "label": "编辑器搜索: 交互式搜索",
                "type": "shell", 
                "command": "python",
                "args": [
                    "workspace_jumper.py",
                    "${input:searchTerm}"
                ],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": True,
                    "panel": "new"
                }
            }
        ]
        
        # 移除旧的编辑器搜索任务
        tasks_config["tasks"] = [
            task for task in tasks_config.get("tasks", [])
            if not task.get("label", "").startswith("编辑器搜索:")
        ]
        
        # 添加新任务
        tasks_config["tasks"].extend(editor_search_tasks)
        
        # 添加输入配置
        if "inputs" not in tasks_config:
            tasks_config["inputs"] = []
        
        # 添加搜索词输入
        search_input = {
            "id": "searchTerm",
            "description": "输入搜索关键词",
            "default": "",
            "type": "promptString"
        }
        
        # 检查是否已存在，避免重复
        existing_inputs = [inp.get("id") for inp in tasks_config["inputs"]]
        if "searchTerm" not in existing_inputs:
            tasks_config["inputs"].append(search_input)
        
        # 保存配置
        with open(tasks_file, 'w', encoding='utf-8') as f:
            json.dump(tasks_config, f, indent=2, ensure_ascii=False)
        
        return tasks_file
    
    def create_sublime_text_config(self):
        """创建Sublime Text配置"""
        # Sublime Text用户配置目录
        if os.name == 'nt':  # Windows
            sublime_dir = Path.home() / "AppData/Roaming/Sublime Text 3/Packages/User"
        elif sys.platform == 'darwin':  # macOS
            sublime_dir = Path.home() / "Library/Application Support/Sublime Text 3/Packages/User"
        else:  # Linux
            sublime_dir = Path.home() / ".config/sublime-text-3/Packages/User"
        
        if not sublime_dir.exists():
            print(f"⚠️  Sublime Text配置目录不存在: {sublime_dir}")
            return None
        
        # 创建自定义命令
        commands_file = sublime_dir / "AdvancedSearch.sublime-commands"
        commands = [
            {
                "caption": "高级搜索: 关键词搜索",
                "command": "exec",
                "args": {
                    "cmd": ["python", str(self.workspace_path / "workspace_jumper.py"), "$selection"],
                    "working_dir": str(self.workspace_path)
                }
            },
            {
                "caption": "高级搜索: 正则表达式搜索", 
                "command": "exec",
                "args": {
                    "cmd": ["python", str(self.workspace_path / "search_engine.py"), "-r", "$selection"],
                    "working_dir": str(self.workspace_path)
                }
            }
        ]
        
        with open(commands_file, 'w', encoding='utf-8') as f:
            json.dump(commands, f, indent=2, ensure_ascii=False)
        
        # 创建快捷键绑定
        keymap_file = sublime_dir / "AdvancedSearch.sublime-keymap"
        keybindings = [
            {
                "keys": ["ctrl+alt+f"],
                "command": "exec",
                "args": {
                    "cmd": ["python", str(self.workspace_path / "workspace_jumper.py"), "$selection"],
                    "working_dir": str(self.workspace_path)
                }
            }
        ]
        
        with open(keymap_file, 'w', encoding='utf-8') as f:
            json.dump(keybindings, f, indent=2, ensure_ascii=False)
        
        return commands_file, keymap_file
    
    def create_vim_config(self):
        """创建Vim配置"""
        vim_config = f'''
" 高级搜索集成
" 添加到 ~/.vimrc 或 ~/.config/nvim/init.vim

" 搜索当前词
nnoremap <leader>fs :!python {self.workspace_path}/workspace_jumper.py <cword><CR>

" 搜索选中文本
vnoremap <leader>fs y:!python {self.workspace_path}/workspace_jumper.py <C-R>"<CR>

" 交互式搜索
nnoremap <leader>fi :!python {self.workspace_path}/workspace_jumper.py 

" 正则搜索
nnoremap <leader>fr :!python {self.workspace_path}/search_engine.py -r 

" 模糊搜索
nnoremap <leader>ff :!python {self.workspace_path}/search_engine.py -f 

" 函数：在Vim中打开搜索结果
function! OpenSearchResult(file, line)
    execute 'edit ' . a:file
    execute a:line
endfunction
'''
        
        vim_config_file = self.workspace_path / "vim_search_config.vim"
        with open(vim_config_file, 'w', encoding='utf-8') as f:
            f.write(vim_config)
        
        return vim_config_file
    
    def search_selection(self, text: str = None):
        """搜索选中的文本"""
        if not text:
            # 尝试从剪贴板获取
            try:
                import pyperclip
                text = pyperclip.paste().strip()
            except ImportError:
                text = input("请输入搜索文本: ").strip()
        
        if not text:
            print("❌ 没有要搜索的文本")
            return
        
        print(f"🔍 搜索选中文本: {text}")
        
        # 执行搜索
        results = self.search_engine.search_keyword(text, context_lines=2)
        
        if not results:
            print("❌ 未找到匹配结果")
            return
        
        # 显示结果
        print(f"🎯 找到 {len(results)} 个结果:")
        for i, result in enumerate(results[:10], 1):
            print(f"\n[{i}] 📁 {result.file_path}:{result.line_number}")
            print(f"    {result.line_content.strip()}")
        
        # 询问是否要跳转
        try:
            choice = input("\n输入数字跳转到结果 (回车跳过): ").strip()
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(results):
                    from line_jumper import AdvancedLineJumper
                    jumper = AdvancedLineJumper()
                    success, message = jumper.jump_to_line(
                        results[index].absolute_path, 
                        results[index].line_number
                    )
                    print("✅" if success else "❌", message)
        except (KeyboardInterrupt, EOFError):
            pass
    
    def setup_all_editors(self):
        """设置所有编辑器集成"""
        print("🔧 设置编辑器搜索集成...")
        
        # VSCode
        try:
            vscode_config = self.create_vscode_extension_config()
            print(f"✅ VSCode配置已创建: {vscode_config}")
        except Exception as e:
            print(f"❌ VSCode配置失败: {e}")
        
        # Sublime Text
        try:
            sublime_configs = self.create_sublime_text_config()
            if sublime_configs:
                print(f"✅ Sublime Text配置已创建: {sublime_configs}")
            else:
                print("⚠️  Sublime Text未安装或配置目录不存在")
        except Exception as e:
            print(f"❌ Sublime Text配置失败: {e}")
        
        # Vim
        try:
            vim_config = self.create_vim_config()
            print(f"✅ Vim配置已创建: {vim_config}")
            print("   请将配置内容添加到您的 ~/.vimrc 文件中")
        except Exception as e:
            print(f"❌ Vim配置失败: {e}")
        
        print("\n🎉 编辑器集成设置完成！")
        print("\n💡 使用方法:")
        print("1. VSCode: Ctrl+Shift+P → 'Tasks: Run Task' → 选择编辑器搜索任务")
        print("2. Sublime Text: Ctrl+Shift+P → 输入 '高级搜索'")
        print("3. Vim: <leader>fs (搜索当前词), <leader>fi (交互式搜索)")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="编辑器搜索集成工具")
    parser.add_argument('--setup', action='store_true', help='设置所有编辑器集成')
    parser.add_argument('--search-selection', action='store_true', help='搜索选中文本')
    parser.add_argument('--text', help='要搜索的文本')
    parser.add_argument('-p', '--path', default='.', help='工作区路径')
    
    args = parser.parse_args()
    
    integration = EditorSearchIntegration(args.path)
    
    if args.setup:
        integration.setup_all_editors()
    elif args.search_selection:
        integration.search_selection(args.text)
    else:
        print("使用 --setup 设置编辑器集成，或 --search-selection 搜索选中文本")

if __name__ == "__main__":
    main()
