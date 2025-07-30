#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试控制台搜索工具
在调试控制台中使用我们的搜索引擎
"""

import sys
import os
import json
from pathlib import Path
from typing import List, Dict, Any
from search_engine import FileSearchEngine, SearchResult

class DebugConsoleSearch:
    """调试控制台搜索类"""
    
    def __init__(self, workspace_path: str = "."):
        self.workspace_path = Path(workspace_path)
        self.search_engine = FileSearchEngine(workspace_path)
        self.last_results = []
        self.display_mode = "full"  # 显示模式: "full"=完整路径, "filename"=仅文件名, "content"=仅内容

    def set_display_mode(self, mode: str = "full"):
        """设置显示模式

        Args:
            mode: "full"=完整路径, "filename"=仅文件名, "content"=仅内容
        """
        if mode not in ["full", "filename", "content"]:
            print("❌ 无效的显示模式！请使用: 'full', 'filename', 'content'")
            return

        self.display_mode = mode
        mode_names = {
            "full": "完整路径",
            "filename": "仅文件名",
            "content": "仅内容"
        }
        print(f"✅ 搜索显示模式已设置为: {mode_names[mode]}")

    def toggle_display_mode(self):
        """循环切换显示模式"""
        modes = ["full", "filename", "content"]
        current_index = modes.index(self.display_mode)
        next_index = (current_index + 1) % len(modes)
        self.display_mode = modes[next_index]

        mode_names = {
            "full": "完整路径",
            "filename": "仅文件名",
            "content": "仅内容"
        }
        print(f"🔄 搜索显示模式已切换为: {mode_names[self.display_mode]}")

    def get_display_mode(self):
        """获取当前显示模式"""
        mode_names = {
            "full": "完整路径",
            "filename": "仅文件名",
            "content": "仅内容"
        }
        print(f"ℹ️ 当前搜索显示模式: {mode_names[self.display_mode]}")
        return self.display_mode

    def search(self, keyword: str, display_mode: str = None, **kwargs) -> List[SearchResult]:
        """搜索函数 - 调试控制台友好"""
        # 使用传入的参数或默认配置
        mode = display_mode if display_mode is not None else self.display_mode

        print(f"🔍 搜索: {keyword}")

        # 执行搜索
        results = self.search_engine.search_keyword(keyword, **kwargs)
        self.last_results = results

        if not results:
            print("❌ 未找到匹配结果")
            return []

        print(f"🎯 找到 {len(results)} 个结果:")

        # 显示前10个结果
        for i, result in enumerate(results[:10], 1):
            if mode == "full":
                # 完整路径模式
                print(f"[{i:2d}] {result.file_path}:{result.line_number}")
                print(f"     {result.line_content.strip()}")
            elif mode == "filename":
                # 仅文件名模式
                filename = Path(result.file_path).name
                print(f"[{i:2d}] {filename}:{result.line_number}")
                print(f"     {result.line_content.strip()}")
            else:  # content
                # 仅内容模式
                print(f"[{i:2d}] {result.line_content.strip()}")

        if len(results) > 10:
            print(f"... 还有 {len(results) - 10} 个结果")

        print(f"\n💡 使用 jump(数字) 跳转到结果")
        print(f"💡 使用 show(数字) 显示更多上下文")

        return results
    
    def s(self, keyword: str, **kwargs) -> List[SearchResult]:
        """搜索的简短别名"""
        return self.search(keyword, **kwargs)

    def sc(self, keyword: str, **kwargs) -> List[SearchResult]:
        """纯内容搜索 - 只显示内容，不显示路径"""
        return self.search(keyword, display_mode="content", **kwargs)

    def sf(self, keyword: str, **kwargs) -> List[SearchResult]:
        """文件名搜索 - 显示文件名、行号和内容"""
        return self.search(keyword, display_mode="filename", **kwargs)
    
    def jump(self, index: int) -> bool:
        """跳转到搜索结果"""
        if not self.last_results:
            print("❌ 没有搜索结果，请先执行搜索")
            return False
        
        if not (1 <= index <= len(self.last_results)):
            print(f"❌ 无效索引，请输入 1-{len(self.last_results)}")
            return False
        
        result = self.last_results[index - 1]
        
        # 尝试跳转
        try:
            from line_jumper import AdvancedLineJumper
            jumper = AdvancedLineJumper()
            success, message = jumper.jump_to_line(result.absolute_path, result.line_number)
            
            if success:
                print(f"✅ 已跳转到: {result.file_path}:{result.line_number}")
                return True
            else:
                print(f"❌ 跳转失败: {message}")
                # 回退：显示文件内容
                self.show_file_content(result)
                return False
        except ImportError:
            print("⚠️  line_jumper 不可用，显示文件内容:")
            self.show_file_content(result)
            return False
    
    def j(self, index: int) -> bool:
        """跳转的简短别名"""
        return self.jump(index)
    
    def show(self, index: int, context: int = 5) -> None:
        """显示搜索结果的上下文"""
        if not self.last_results:
            print("❌ 没有搜索结果，请先执行搜索")
            return
        
        if not (1 <= index <= len(self.last_results)):
            print(f"❌ 无效索引，请输入 1-{len(self.last_results)}")
            return
        
        result = self.last_results[index - 1]
        
        print(f"\n📁 {result.file_path}:{result.line_number}")
        print("=" * 50)
        
        try:
            with open(result.absolute_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            start_line = max(0, result.line_number - context - 1)
            end_line = min(len(lines), result.line_number + context)
            
            for i in range(start_line, end_line):
                line_num = i + 1
                line_content = lines[i].rstrip()
                
                if line_num == result.line_number:
                    print(f"➤ {line_num:4d}: {line_content}")
                else:
                    print(f"  {line_num:4d}: {line_content}")
        
        except Exception as e:
            print(f"❌ 无法读取文件: {e}")
    
    def show_file_content(self, result: SearchResult, context: int = 10):
        """显示文件内容（当无法跳转时）"""
        try:
            with open(result.absolute_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            start_line = max(0, result.line_number - context - 1)
            end_line = min(len(lines), result.line_number + context)
            
            print(f"\n📄 {result.file_path} (第 {result.line_number} 行)")
            print("=" * 60)
            
            for i in range(start_line, end_line):
                line_num = i + 1
                line_content = lines[i].rstrip()
                
                if line_num == result.line_number:
                    print(f"➤ {line_num:4d}: {line_content}")
                else:
                    print(f"  {line_num:4d}: {line_content}")
        
        except Exception as e:
            print(f"❌ 无法读取文件: {e}")
    
    def regex_search(self, pattern: str, display_mode: str = None, **kwargs) -> List[SearchResult]:
        """正则表达式搜索"""
        # 使用传入的参数或默认配置
        mode = display_mode if display_mode is not None else self.display_mode

        print(f"🔍 正则搜索: {pattern}")

        results = self.search_engine.search_regex(pattern, **kwargs)
        self.last_results = results

        if not results:
            print("❌ 未找到匹配结果")
            return []

        print(f"🎯 找到 {len(results)} 个结果:")

        for i, result in enumerate(results[:10], 1):
            if mode == "full":
                # 完整路径模式
                print(f"[{i:2d}] {result.file_path}:{result.line_number}")
                print(f"     {result.line_content.strip()}")
            elif mode == "filename":
                # 仅文件名模式
                filename = Path(result.file_path).name
                print(f"[{i:2d}] {filename}:{result.line_number}")
                print(f"     {result.line_content.strip()}")
            else:  # content
                # 仅内容模式
                print(f"[{i:2d}] {result.line_content.strip()}")

        if len(results) > 10:
            print(f"... 还有 {len(results) - 10} 个结果")

        return results
    
    def r(self, pattern: str, **kwargs) -> List[SearchResult]:
        """正则搜索的简短别名"""
        return self.regex_search(pattern, **kwargs)

    def rc(self, pattern: str, **kwargs) -> List[SearchResult]:
        """纯内容正则搜索 - 只显示内容，不显示路径"""
        return self.regex_search(pattern, display_mode="content", **kwargs)

    def rf(self, pattern: str, **kwargs) -> List[SearchResult]:
        """文件名正则搜索 - 显示文件名、行号和内容"""
        return self.regex_search(pattern, display_mode="filename", **kwargs)
    
    def fuzzy_search(self, keyword: str, threshold: float = 0.7, display_mode: str = None, **kwargs) -> List[SearchResult]:
        """模糊搜索"""
        # 使用传入的参数或默认配置
        mode = display_mode if display_mode is not None else self.display_mode

        print(f"🔍 模糊搜索: {keyword} (相似度 >= {threshold})")

        results = self.search_engine.fuzzy_search(keyword, threshold, **kwargs)
        self.last_results = results

        if not results:
            print("❌ 未找到匹配结果")
            return []

        print(f"🎯 找到 {len(results)} 个结果:")

        for i, result in enumerate(results[:10], 1):
            if mode == "full":
                # 完整路径模式
                print(f"[{i:2d}] {result.file_path}:{result.line_number}")
                print(f"     {result.line_content.strip()}")
            elif mode == "filename":
                # 仅文件名模式
                filename = Path(result.file_path).name
                print(f"[{i:2d}] {filename}:{result.line_number}")
                print(f"     {result.line_content.strip()}")
            else:  # content
                # 仅内容模式
                print(f"[{i:2d}] {result.line_content.strip()}")

        if len(results) > 10:
            print(f"... 还有 {len(results) - 10} 个结果")

        return results
    
    def f(self, keyword: str, threshold: float = 0.7, **kwargs) -> List[SearchResult]:
        """模糊搜索的简短别名"""
        return self.fuzzy_search(keyword, threshold, **kwargs)

    def fc(self, keyword: str, threshold: float = 0.7, **kwargs) -> List[SearchResult]:
        """纯内容模糊搜索 - 只显示内容，不显示路径"""
        return self.fuzzy_search(keyword, threshold, display_mode="content", **kwargs)

    def ff(self, keyword: str, threshold: float = 0.7, **kwargs) -> List[SearchResult]:
        """文件名模糊搜索 - 显示文件名、行号和内容"""
        return self.fuzzy_search(keyword, threshold, display_mode="filename", **kwargs)
    
    def help(self):
        """显示帮助信息"""
        help_text = """
🔍 调试控制台搜索工具帮助

📋 基本命令:
  search(keyword)     # 关键词搜索 (别名: s)
  regex_search(pattern) # 正则搜索 (别名: r)
  fuzzy_search(keyword) # 模糊搜索 (别名: f)

📋 显示模式命令:
  sc(keyword)         # 纯内容搜索 (只显示内容)
  sf(keyword)         # 文件名搜索 (文件名:行号 + 内容)
  rc(pattern)         # 纯内容正则搜索
  rf(pattern)         # 文件名正则搜索
  fc(keyword)         # 纯内容模糊搜索
  ff(keyword)         # 文件名模糊搜索

🎯 结果操作:
  jump(数字)          # 跳转到搜索结果 (别名: j)
  show(数字)          # 显示结果上下文

⚙️ 显示模式配置:
  mode("full")        # 完整路径模式 (默认)
  mode("filename")    # 仅文件名模式
  mode("content")     # 仅内容模式
  toggle()            # 循环切换显示模式
  status()            # 查看当前模式

📖 使用示例:
  # 基本搜索 (使用当前默认模式)
  s("原函数")         # 使用当前默认模式

  # 强制指定显示模式
  sc("原函数")        # 强制纯内容模式
  sf("原函数")        # 强制文件名模式 (推荐!)

  # 配置默认显示模式
  mode("filename")    # 设置默认为文件名模式
  s("积分")           # 现在默认显示: 文件名.md:行号
  toggle()            # 切换到下一个模式
  status()            # 查看当前模式

  # 正则和模糊搜索
  rf("def\\s+\\w+")   # 文件名模式正则搜索
  ff("积分", 0.8)     # 文件名模式模糊搜索

  # 结果操作
  j(1)               # 跳转到第1个结果
  show(2, 10)        # 显示第2个结果的10行上下文

⚙️ 搜索选项:
  context_lines=N    # 显示N行上下文
  extensions=['md']  # 只搜索指定扩展名
  case_sensitive=True # 大小写敏感

💡 推荐用法:
  mode("filename")    # 设置为文件名模式 (最佳平衡)
  sf("函数", extensions=['md'])  # 文件名搜索指定类型
"""
        print(help_text)
    
    def h(self):
        """帮助的简短别名"""
        self.help()

# 创建全局搜索实例
search_tool = DebugConsoleSearch()

# 导出常用函数到全局命名空间
def search(keyword: str, **kwargs):
    """全局搜索函数"""
    return search_tool.search(keyword, **kwargs)

def s(keyword: str, **kwargs):
    """搜索简短别名"""
    return search_tool.s(keyword, **kwargs)

def sc(keyword: str, **kwargs):
    """纯内容搜索 - 只显示内容，不显示路径"""
    return search_tool.sc(keyword, **kwargs)

def sf(keyword: str, **kwargs):
    """文件名搜索 - 显示文件名、行号和内容"""
    return search_tool.sf(keyword, **kwargs)

def jump(index: int):
    """全局跳转函数"""
    return search_tool.jump(index)

def j(index: int):
    """跳转简短别名"""
    return search_tool.j(index)

def show(index: int, context: int = 5):
    """全局显示函数"""
    return search_tool.show(index, context)

def regex_search(pattern: str, **kwargs):
    """全局正则搜索"""
    return search_tool.regex_search(pattern, **kwargs)

def r(pattern: str, **kwargs):
    """正则搜索简短别名"""
    return search_tool.r(pattern, **kwargs)

def rc(pattern: str, **kwargs):
    """纯内容正则搜索 - 只显示内容，不显示路径"""
    return search_tool.rc(pattern, **kwargs)

def rf(pattern: str, **kwargs):
    """文件名正则搜索 - 显示文件名、行号和内容"""
    return search_tool.rf(pattern, **kwargs)

def fuzzy_search(keyword: str, threshold: float = 0.7, **kwargs):
    """全局模糊搜索"""
    return search_tool.fuzzy_search(keyword, threshold, **kwargs)

def f(keyword: str, threshold: float = 0.7, **kwargs):
    """模糊搜索简短别名"""
    return search_tool.f(keyword, threshold, **kwargs)

def fc(keyword: str, threshold: float = 0.7, **kwargs):
    """纯内容模糊搜索 - 只显示内容，不显示路径"""
    return search_tool.fc(keyword, threshold, **kwargs)

def ff(keyword: str, threshold: float = 0.7, **kwargs):
    """文件名模糊搜索 - 显示文件名、行号和内容"""
    return search_tool.ff(keyword, threshold, **kwargs)

# 配置函数
def set_display_mode(mode: str = "full"):
    """设置搜索显示模式

    Args:
        mode: "full"=完整路径, "filename"=仅文件名, "content"=仅内容

    Examples:
        set_display_mode("full")      # 完整路径模式
        set_display_mode("filename")  # 仅文件名模式
        set_display_mode("content")   # 仅内容模式
    """
    return search_tool.set_display_mode(mode)

def toggle_display_mode():
    """切换搜索显示模式"""
    return search_tool.toggle_display_mode()

def get_display_mode():
    """获取当前搜索显示模式"""
    return search_tool.get_display_mode()

# 简短别名
def mode(mode_str: str = "full"):
    """设置显示模式的简短别名"""
    return set_display_mode(mode_str)

def toggle():
    """切换模式的简短别名"""
    return toggle_display_mode()

def status():
    """查看状态的简短别名"""
    return get_display_mode()

def help_search():
    """显示帮助"""
    search_tool.help()

def h():
    """帮助简短别名"""
    search_tool.h()

# 启动信息
if __name__ == "__main__":
    print("🔍 调试控制台搜索工具已加载")
    print("💡 输入 help_search() 或 h() 查看帮助")
    print("🚀 快速开始: sf('原函数') - 推荐文件名模式")
    print("⚙️ 显示模式: mode('full')=完整路径, mode('filename')=文件名, mode('content')=纯内容")
else:
    print("🔍 调试控制台搜索工具已导入")
    print("💡 使用 sf('关键词') 开始搜索 - 推荐文件名模式")
    print("⚙️ 显示模式: mode('filename')=文件名, toggle()=切换")
