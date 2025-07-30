#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证Git仓库和记忆功能设置
"""

import os
import subprocess
import sys
from pathlib import Path

def test_git_repository():
    """测试Git仓库是否正确初始化"""
    print("🔍 测试Git仓库设置...")
    
    tests = []
    
    # 检查是否在Git仓库中
    try:
        result = subprocess.run(['git', 'rev-parse', '--git-dir'], 
                              capture_output=True, text=True, check=True)
        tests.append(("Git仓库存在", True, f"Git目录: {result.stdout.strip()}"))
    except subprocess.CalledProcessError:
        tests.append(("Git仓库存在", False, "未找到Git仓库"))
        return tests
    
    # 检查Git配置
    try:
        user_name = subprocess.run(['git', 'config', 'user.name'], 
                                 capture_output=True, text=True, check=True)
        user_email = subprocess.run(['git', 'config', 'user.email'], 
                                  capture_output=True, text=True, check=True)
        tests.append(("Git用户配置", True, 
                     f"用户: {user_name.stdout.strip()}, 邮箱: {user_email.stdout.strip()}"))
    except subprocess.CalledProcessError:
        tests.append(("Git用户配置", False, "Git用户信息未配置"))
    
    # 检查.gitignore文件
    gitignore_path = Path('.gitignore')
    if gitignore_path.exists():
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if '数学/' in content and '*.pdf' in content:
                tests.append((".gitignore配置", True, "包含必要的忽略规则"))
            else:
                tests.append((".gitignore配置", False, "缺少关键忽略规则"))
    else:
        tests.append((".gitignore文件", False, ".gitignore文件不存在"))
    
    # 检查重要目录是否被跟踪
    important_paths = ['数学/', '数学/mcp/']
    for path in important_paths:
        if Path(path).exists():
            try:
                result = subprocess.run(['git', 'ls-files', path], 
                                      capture_output=True, text=True, check=True)
                if result.stdout.strip():
                    tests.append((f"{path}目录跟踪", True, "目录已被Git跟踪"))
                else:
                    tests.append((f"{path}目录跟踪", False, "目录未被Git跟踪"))
            except subprocess.CalledProcessError:
                tests.append((f"{path}目录跟踪", False, "无法检查跟踪状态"))
    
    return tests

def test_memory_functionality():
    """测试记忆功能的可用性"""
    print("🧠 测试记忆功能设置...")
    
    tests = []
    
    # 检查是否在Git根目录
    current_dir = Path.cwd()
    git_dir = current_dir / '.git'
    
    if git_dir.exists():
        tests.append(("Git根目录检测", True, f"当前目录是Git根目录: {current_dir}"))
        
        # 检查MCP协议文件
        mcp_dir = current_dir / '数学' / 'mcp'
        if mcp_dir.exists():
            aura_files = list(mcp_dir.glob('AURA*.md'))
            if aura_files:
                tests.append(("AURA协议文件", True, f"找到 {len(aura_files)} 个协议文件"))
            else:
                tests.append(("AURA协议文件", False, "未找到AURA协议文件"))
        else:
            tests.append(("MCP目录", False, "MCP目录不存在"))
    else:
        tests.append(("Git根目录检测", False, "当前目录不是Git根目录"))
    
    return tests

def test_project_structure():
    """测试项目结构"""
    print("📁 测试项目结构...")
    
    tests = []
    
    # 检查关键目录和文件
    important_items = [
        ('数学/', '数学学习目录'),
        ('数学/mcp/', 'MCP协议目录'),
        ('数学/第22讲-线性方程组.md', '数学内容文件'),
        ('.gitignore', 'Git忽略文件'),
    ]
    
    for item_path, description in important_items:
        path = Path(item_path)
        if path.exists():
            if path.is_dir():
                file_count = len(list(path.rglob('*')))
                tests.append((description, True, f"目录存在，包含 {file_count} 个项目"))
            else:
                size = path.stat().st_size
                tests.append((description, True, f"文件存在，大小 {size} 字节"))
        else:
            tests.append((description, False, "不存在"))
    
    return tests

def print_test_results(test_name, tests):
    """打印测试结果"""
    print(f"\n{'='*60}")
    print(f"📊 {test_name}")
    print('='*60)
    
    passed = 0
    total = len(tests)
    
    for test_desc, result, details in tests:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} {test_desc}: {details}")
        if result:
            passed += 1
    
    print(f"\n📈 结果: {passed}/{total} 项测试通过")
    return passed == total

def main():
    """主测试函数"""
    print("🧪 开始Git仓库和记忆功能设置测试...")
    print(f"📍 当前工作目录: {Path.cwd()}")
    
    all_passed = True
    
    # 运行各项测试
    git_tests = test_git_repository()
    git_passed = print_test_results("Git仓库测试", git_tests)
    
    memory_tests = test_memory_functionality()
    memory_passed = print_test_results("记忆功能测试", memory_tests)
    
    structure_tests = test_project_structure()
    structure_passed = print_test_results("项目结构测试", structure_tests)
    
    all_passed = git_passed and memory_passed and structure_passed
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 所有测试通过！Git仓库和记忆功能已正确设置！")
        print("\n📝 下一步操作建议:")
        print("1. 现在可以使用 `记忆` MCP工具进行知识管理")
        print("2. 使用 `寸止` MCP工具进行交互控制")
        print("3. 开始使用优化后的AURA协议")
    else:
        print("⚠️  部分测试未通过，请检查设置")
        print("\n🔧 修复建议:")
        if not git_passed:
            print("- 运行 git init 初始化仓库")
            print("- 配置 git config user.name 和 user.email")
        if not memory_passed:
            print("- 确保在Git根目录中运行")
            print("- 检查MCP协议文件是否存在")
        if not structure_passed:
            print("- 检查重要目录和文件是否存在")

if __name__ == "__main__":
    main()
