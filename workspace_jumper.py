#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作区跳转工具
专门为工作区搜索提供精确的行跳转功能
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from search_engine import FileSearchEngine, SearchResult
from line_jumper import AdvancedLineJumper

class WorkspaceJumper:
    """工作区跳转工具"""
    
    def __init__(self, workspace_path: str = "."):
        self.workspace_path = Path(workspace_path)
        self.search_engine = FileSearchEngine(workspace_path)
        self.line_jumper = AdvancedLineJumper()
        self.bookmarks = self._load_bookmarks()
    
    def _load_bookmarks(self) -> Dict:
        """加载书签"""
        bookmark_file = self.workspace_path / ".vscode" / "bookmarks.json"
        if bookmark_file.exists():
            try:
                with open(bookmark_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"bookmarks": []}
    
    def _save_bookmarks(self):
        """保存书签"""
        vscode_dir = self.workspace_path / ".vscode"
        vscode_dir.mkdir(exist_ok=True)
        
        bookmark_file = vscode_dir / "bookmarks.json"
        with open(bookmark_file, 'w', encoding='utf-8') as f:
            json.dump(self.bookmarks, f, indent=2, ensure_ascii=False)
    
    def search_and_jump(self, keyword: str, **search_kwargs) -> List[SearchResult]:
        """搜索并提供跳转选项"""
        print(f"🔍 在工作区中搜索: {keyword}")
        
        # 执行搜索
        results = self.search_engine.search_keyword(keyword, **search_kwargs)
        
        if not results:
            print("❌ 未找到匹配结果")
            return []
        
        print(f"🎯 找到 {len(results)} 个结果:")
        
        # 显示结果
        for i, result in enumerate(results[:20], 1):  # 限制显示20个结果
            print(f"\n[{i:2d}] 📁 {result.file_path}:{result.line_number}")
            print(f"     {result.line_content.strip()}")
            
            # 显示上下文
            if result.context_before:
                for ctx in result.context_before[-2:]:  # 只显示前2行上下文
                    print(f"     │ {ctx.strip()}")
            
            if result.context_after:
                for ctx in result.context_after[:2]:  # 只显示后2行上下文
                    print(f"     │ {ctx.strip()}")
        
        return results
    
    def interactive_jump(self, results: List[SearchResult]):
        """交互式跳转"""
        if not results:
            return
        
        while True:
            print("\n" + "="*60)
            print("💡 跳转选项:")
            print("  数字: 跳转到对应结果")
            print("  数字+e: 选择编辑器跳转")
            print("  数字+b: 添加到书签")
            print("  数字+s: 创建桌面快捷方式")
            print("  数字+f: 打开文件夹")
            print("  bookmarks/b: 查看书签")
            print("  editors/e: 查看可用编辑器")
            print("  quit/q: 退出")
            
            try:
                user_input = input("\n请选择操作: ").strip().lower()
                
                if user_input in ['quit', 'q']:
                    print("👋 再见！")
                    break
                
                elif user_input in ['bookmarks', 'b']:
                    self._show_bookmarks()
                    continue
                
                elif user_input in ['editors', 'e']:
                    self._show_editors()
                    continue
                
                # 解析数字命令
                if user_input.isdigit():
                    index = int(user_input) - 1
                    if 0 <= index < len(results):
                        self._jump_to_result(results[index])
                    else:
                        print("❌ 无效的序号")
                
                elif user_input.endswith('e') and user_input[:-1].isdigit():
                    index = int(user_input[:-1]) - 1
                    if 0 <= index < len(results):
                        self._jump_with_editor_choice(results[index])
                    else:
                        print("❌ 无效的序号")
                
                elif user_input.endswith('b') and user_input[:-1].isdigit():
                    index = int(user_input[:-1]) - 1
                    if 0 <= index < len(results):
                        self._add_bookmark(results[index])
                    else:
                        print("❌ 无效的序号")
                
                elif user_input.endswith('s') and user_input[:-1].isdigit():
                    index = int(user_input[:-1]) - 1
                    if 0 <= index < len(results):
                        self._create_shortcut(results[index])
                    else:
                        print("❌ 无效的序号")
                
                elif user_input.endswith('f') and user_input[:-1].isdigit():
                    index = int(user_input[:-1]) - 1
                    if 0 <= index < len(results):
                        self._open_folder(results[index])
                    else:
                        print("❌ 无效的序号")
                
                else:
                    print("❌ 无效的输入")
            
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
            except EOFError:
                print("\n👋 再见！")
                break
    
    def _jump_to_result(self, result: SearchResult):
        """跳转到搜索结果"""
        success, message = self.line_jumper.jump_to_line(
            result.absolute_path, result.line_number
        )
        print("✅" if success else "❌", message)
    
    def _jump_with_editor_choice(self, result: SearchResult):
        """选择编辑器跳转"""
        editors = list(self.line_jumper.available_editors.keys())
        if not editors:
            print("❌ 没有可用的编辑器")
            return
        
        print("\n可用编辑器:")
        for i, editor_id in enumerate(editors, 1):
            editor_info = self.line_jumper.available_editors[editor_id]
            print(f"  {i}. {editor_info['name']} ({editor_id})")
        
        try:
            choice = input("选择编辑器 (数字): ").strip()
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(editors):
                    editor_id = editors[index]
                    success, message = self.line_jumper.jump_to_line(
                        result.absolute_path, result.line_number, editor_id
                    )
                    print("✅" if success else "❌", message)
                else:
                    print("❌ 无效的选择")
            else:
                print("❌ 请输入数字")
        except (ValueError, KeyboardInterrupt):
            print("❌ 操作取消")
    
    def _add_bookmark(self, result: SearchResult):
        """添加书签"""
        bookmark_name = input("输入书签名称 (回车使用默认): ").strip()
        if not bookmark_name:
            bookmark_name = f"{os.path.basename(result.file_path)}:{result.line_number}"
        
        bookmark = {
            "name": bookmark_name,
            "file": result.file_path,
            "line": result.line_number,
            "content": result.line_content.strip(),
            "timestamp": str(Path().cwd())
        }
        
        self.bookmarks["bookmarks"].append(bookmark)
        self._save_bookmarks()
        print(f"✅ 书签已添加: {bookmark_name}")
    
    def _create_shortcut(self, result: SearchResult):
        """创建桌面快捷方式"""
        shortcut_name = input("输入快捷方式名称 (回车使用默认): ").strip()
        if not shortcut_name:
            shortcut_name = f"{os.path.basename(result.file_path)}_line_{result.line_number}"
        
        success, message = self.line_jumper.create_desktop_shortcut(
            result.absolute_path, result.line_number, shortcut_name
        )
        print("✅" if success else "❌", message)
    
    def _open_folder(self, result: SearchResult):
        """打开文件夹"""
        success, message = self.line_jumper.open_file_location(result.absolute_path)
        print("✅" if success else "❌", message)
    
    def _show_bookmarks(self):
        """显示书签"""
        bookmarks = self.bookmarks.get("bookmarks", [])
        if not bookmarks:
            print("📚 暂无书签")
            return
        
        print("\n📚 书签列表:")
        for i, bookmark in enumerate(bookmarks, 1):
            print(f"  [{i}] {bookmark['name']}")
            print(f"      📁 {bookmark['file']}:{bookmark['line']}")
            print(f"      📝 {bookmark['content']}")
        
        try:
            choice = input("\n跳转到书签 (输入数字，回车跳过): ").strip()
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(bookmarks):
                    bookmark = bookmarks[index]
                    success, message = self.line_jumper.jump_to_line(
                        bookmark['file'], bookmark['line']
                    )
                    print("✅" if success else "❌", message)
                else:
                    print("❌ 无效的书签序号")
        except (ValueError, KeyboardInterrupt):
            pass
    
    def _show_editors(self):
        """显示可用编辑器"""
        editors = self.line_jumper.list_available_editors()
        if editors:
            print("\n🔧 可用编辑器:")
            for i, editor in enumerate(editors, 1):
                print(f"  {i}. {editor}")
        else:
            print("❌ 未检测到支持的编辑器")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="工作区跳转工具")
    parser.add_argument('keyword', help='搜索关键词')
    parser.add_argument('-p', '--path', default='.', help='工作区路径')
    parser.add_argument('-c', '--context', type=int, default=2, help='上下文行数')
    parser.add_argument('-e', '--extensions', nargs='+', help='文件扩展名过滤')
    parser.add_argument('-i', '--ignore-case', action='store_true', help='忽略大小写')
    
    args = parser.parse_args()
    
    # 创建工作区跳转工具
    jumper = WorkspaceJumper(args.path)
    
    # 搜索并跳转
    results = jumper.search_and_jump(
        args.keyword,
        context_lines=args.context,
        extensions=args.extensions,
        case_sensitive=not args.ignore_case
    )
    
    if results:
        jumper.interactive_jump(results)

if __name__ == "__main__":
    main()
