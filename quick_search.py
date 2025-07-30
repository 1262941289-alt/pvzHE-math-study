#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速搜索启动器
提供便捷的搜索入口和工作区集成
"""

import sys
import os
import argparse
from pathlib import Path
from search_engine import InteractiveSearchEngine
from vscode_integration import VSCodeIntegration

def quick_search():
    """快速搜索模式"""
    print("🔍 快速搜索模式")
    print("=" * 50)
    
    # 获取搜索关键词
    if len(sys.argv) > 1:
        keyword = " ".join(sys.argv[1:])
    else:
        keyword = input("请输入搜索关键词: ").strip()
    
    if not keyword:
        print("❌ 搜索关键词不能为空")
        return
    
    # 创建交互式搜索引擎
    engine = InteractiveSearchEngine(".")
    
    # 执行搜索
    engine.interactive_search(
        keyword,
        context_lines=2,
        case_sensitive=False
    )

def setup_workspace():
    """设置工作区"""
    print("🔧 设置工作区集成")
    print("=" * 50)
    
    # 检查是否在Git仓库中
    if Path(".git").exists():
        print("✅ 检测到Git仓库")
    else:
        print("⚠️  未检测到Git仓库")
    
    # 设置VSCode集成
    integration = VSCodeIntegration(".")
    
    # 常用搜索关键词
    common_keywords = [
        "函数", "定义", "原函数", "积分", "导数",
        "TODO", "FIXME", "BUG", "NOTE", "HACK"
    ]
    
    print("设置常用搜索关键词:")
    for i, keyword in enumerate(common_keywords, 1):
        print(f"  {i}. {keyword}")
    
    # 询问用户是否要自定义关键词
    custom = input("\n是否要添加自定义关键词？(y/N): ").lower().strip()
    if custom == 'y':
        custom_keywords = input("请输入自定义关键词（用空格分隔）: ").strip().split()
        common_keywords.extend(custom_keywords)
    
    # 设置集成
    integration.setup_workspace(common_keywords)

def show_help():
    """显示帮助信息"""
    help_text = """
🔍 快速搜索工具使用指南

📋 基本用法:
  python quick_search.py [关键词]     # 快速搜索
  python quick_search.py --setup      # 设置工作区集成
  python quick_search.py --help       # 显示帮助

🚀 交互式搜索:
  python search_engine.py -k "关键词" --interactive

🌐 Web界面:
  python search_web.py

🔧 VSCode集成:
  python vscode_integration.py --setup

💡 搜索技巧:
  - 使用引号包围多词搜索: "原函数定义"
  - 使用正则表达式: python search_engine.py -r "def\s+\w+"
  - 多关键词搜索: python search_engine.py -m "函数" "定义" -o AND
  - 模糊搜索: python search_engine.py -f "积分" -t 0.7

📁 文件跳转:
  - 在交互模式中输入数字直接跳转到VSCode
  - 数字+n: 用记事本打开
  - 数字+f: 打开文件所在文件夹

🎯 VSCode集成功能:
  - Ctrl+Shift+P → "Tasks: Run Task" → 选择搜索任务
  - 使用代码片段: 输入 "search" 然后按Tab
  - 自定义搜索任务和快捷键

📊 输出格式:
  - 控制台: 默认彩色输出
  - JSON: --json 参数
  - HTML: --html filename.html 参数

⚙️ 高级选项:
  - -c N: 显示N行上下文
  - -e ext1 ext2: 只搜索指定扩展名文件
  - -x dir1 dir2: 排除指定目录
  - -i: 忽略大小写
  - -w: 全词匹配
"""
    print(help_text)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="快速搜索启动器",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('keyword', nargs='*', help='搜索关键词')
    parser.add_argument('--setup', action='store_true', help='设置工作区集成')
    parser.add_argument('--help-detail', action='store_true', help='显示详细帮助')
    
    # 如果没有参数，显示交互式菜单
    if len(sys.argv) == 1:
        print("🔍 快速搜索工具")
        print("=" * 30)
        print("1. 快速搜索")
        print("2. 设置工作区集成")
        print("3. 显示帮助")
        print("4. 退出")
        
        choice = input("\n请选择操作 (1-4): ").strip()
        
        if choice == '1':
            quick_search()
        elif choice == '2':
            setup_workspace()
        elif choice == '3':
            show_help()
        elif choice == '4':
            print("👋 再见！")
        else:
            print("❌ 无效选择")
        
        return
    
    args = parser.parse_args()
    
    if args.help_detail:
        show_help()
    elif args.setup:
        setup_workspace()
    elif args.keyword:
        keyword = " ".join(args.keyword)
        engine = InteractiveSearchEngine(".")
        engine.interactive_search(keyword, context_lines=2, case_sensitive=False)
    else:
        quick_search()

if __name__ == "__main__":
    main()
