#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
编辑器搜索演示脚本
展示如何在编辑器中使用我们的搜索引擎
"""

import time
import os
from pathlib import Path

def demo_vscode_integration():
    """演示VSCode集成"""
    print("🎯 VSCode编辑器搜索演示")
    print("=" * 50)
    
    print("📋 可用的搜索任务:")
    print("1. 编辑器搜索: 当前选中文本")
    print("2. 编辑器搜索: 交互式搜索")
    print("3. 搜索: 函数")
    print("4. 搜索: 定义")
    print("5. 搜索: TODO")
    print("6. 搜索: 自定义")
    
    print("\n🚀 使用步骤:")
    print("1. 在VSCode中按 Ctrl+Shift+P")
    print("2. 输入 'Tasks: Run Task'")
    print("3. 选择上述任务之一")
    print("4. 根据提示输入搜索内容")
    print("5. 在搜索结果中选择跳转")
    
    print("\n💡 快捷键提示:")
    print("- Ctrl+Shift+P: 打开命令面板")
    print("- Ctrl+`: 打开终端面板查看搜索结果")
    print("- Ctrl+Shift+`: 新建终端")

def demo_search_comparison():
    """演示搜索方式对比"""
    print("\n🔍 搜索方式对比演示")
    print("=" * 50)
    
    # 模拟不同搜索场景
    scenarios = [
        {
            "场景": "查找当前文件中的变量",
            "编辑器内置": "Ctrl+F → 输入变量名 → 即时高亮",
            "我们的引擎": "适合跨文件查找同名变量",
            "推荐": "编辑器内置"
        },
        {
            "场景": "查找函数定义和调用",
            "编辑器内置": "Ctrl+Shift+F → 输入函数名 → 预览结果",
            "我们的引擎": "显示更多上下文，支持模糊匹配",
            "推荐": "两者结合"
        },
        {
            "场景": "学习新概念",
            "编辑器内置": "基本搜索，结果有限",
            "我们的引擎": "模糊搜索相关概念，丰富上下文",
            "推荐": "我们的引擎"
        },
        {
            "场景": "代码重构",
            "编辑器内置": "强大的替换功能，实时预览",
            "我们的引擎": "查找阶段有优势，替换需要编辑器",
            "推荐": "编辑器内置"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📌 场景 {i}: {scenario['场景']}")
        print(f"   编辑器内置: {scenario['编辑器内置']}")
        print(f"   我们的引擎: {scenario['我们的引擎']}")
        print(f"   💡 推荐: {scenario['推荐']}")

def demo_workflow():
    """演示推荐工作流"""
    print("\n🔄 推荐工作流演示")
    print("=" * 50)
    
    workflows = [
        {
            "名称": "日常开发流程",
            "步骤": [
                "1. 用 Ctrl+P 快速打开文件",
                "2. 用 Ctrl+F 在文件内快速定位",
                "3. 用 Ctrl+Shift+F 查找跨文件引用",
                "4. 复杂搜索时使用我们的搜索引擎"
            ]
        },
        {
            "名称": "学习研究流程", 
            "步骤": [
                "1. 用我们的搜索引擎模糊搜索概念",
                "2. 在搜索结果中跳转到相关文件",
                "3. 用编辑器的符号搜索理解结构",
                "4. 用书签功能保存重要位置"
            ]
        },
        {
            "名称": "调试问题流程",
            "步骤": [
                "1. 用编辑器搜索错误信息",
                "2. 用我们的引擎搜索相关函数",
                "3. 跳转到问题代码位置",
                "4. 用编辑器的调试功能继续分析"
            ]
        }
    ]
    
    for workflow in workflows:
        print(f"\n🎯 {workflow['名称']}:")
        for step in workflow['步骤']:
            print(f"   {step}")

def demo_tips():
    """演示使用技巧"""
    print("\n💡 使用技巧演示")
    print("=" * 50)
    
    tips = [
        {
            "技巧": "选中文本快速搜索",
            "方法": "在VSCode中选中文本 → Ctrl+Shift+P → '编辑器搜索: 当前选中文本'",
            "优势": "无需手动输入，直接搜索选中内容"
        },
        {
            "技巧": "使用正则表达式",
            "方法": "python search_engine.py -r 'def\\s+\\w+' --interactive",
            "优势": "查找所有函数定义，支持复杂模式"
        },
        {
            "技巧": "模糊搜索相关概念",
            "方法": "python search_engine.py -f '积分' -t 0.7",
            "优势": "找到相似但不完全匹配的内容"
        },
        {
            "技巧": "保存常用搜索",
            "方法": "使用书签功能保存重要位置",
            "优势": "快速回到常用的代码位置"
        },
        {
            "技巧": "组合使用编辑器功能",
            "方法": "搜索 → 跳转 → 符号搜索 → 定义跳转",
            "优势": "充分利用编辑器的导航能力"
        }
    ]
    
    for i, tip in enumerate(tips, 1):
        print(f"\n💡 技巧 {i}: {tip['技巧']}")
        print(f"   方法: {tip['方法']}")
        print(f"   优势: {tip['优势']}")

def main():
    """主演示函数"""
    print("🎉 编辑器搜索完整演示")
    print("=" * 60)
    
    # 检查配置文件
    vscode_config = Path(".vscode/tasks.json")
    if vscode_config.exists():
        print("✅ VSCode配置已就绪")
    else:
        print("⚠️  请先运行: python editor_search_integration.py --setup")
        return
    
    # 演示各个部分
    demo_vscode_integration()
    demo_search_comparison()
    demo_workflow()
    demo_tips()
    
    print("\n" + "=" * 60)
    print("🎯 总结")
    print("=" * 60)
    print("✅ 编辑器内置搜索：快速、直观、适合日常使用")
    print("✅ 我们的搜索引擎：强大、灵活、适合复杂需求")
    print("✅ 最佳策略：根据场景选择合适的工具")
    print("✅ 集成使用：在VSCode中无缝切换两种搜索方式")
    
    print("\n🚀 立即体验:")
    print("1. 打开VSCode")
    print("2. 按 Ctrl+Shift+P")
    print("3. 输入 'Tasks: Run Task'")
    print("4. 选择 '编辑器搜索: 交互式搜索'")
    print("5. 输入 '原函数' 开始搜索")

if __name__ == "__main__":
    main()
