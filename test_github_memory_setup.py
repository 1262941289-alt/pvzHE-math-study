#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证GitHub仓库和记忆功能设置
"""

import os
import subprocess
import sys
import json
from pathlib import Path
import urllib.request
import urllib.error

def test_local_git_setup():
    """测试本地Git设置"""
    print("🔍 测试本地Git设置...")
    
    tests = []
    
    # 检查Git仓库
    try:
        result = subprocess.run(['git', 'rev-parse', '--git-dir'], 
                              capture_output=True, text=True, check=True)
        tests.append(("本地Git仓库", True, "Git仓库已初始化"))
    except (subprocess.CalledProcessError, FileNotFoundError):
        tests.append(("本地Git仓库", False, "Git仓库未初始化或Git未安装"))
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
    
    # 检查远程仓库
    try:
        result = subprocess.run(['git', 'remote', '-v'], 
                              capture_output=True, text=True, check=True)
        if 'origin' in result.stdout and 'github.com' in result.stdout:
            tests.append(("GitHub远程仓库", True, "已连接到GitHub"))
        else:
            tests.append(("GitHub远程仓库", False, "未连接到GitHub"))
    except subprocess.CalledProcessError:
        tests.append(("GitHub远程仓库", False, "无远程仓库配置"))
    
    # 检查分支
    try:
        result = subprocess.run(['git', 'branch', '--show-current'], 
                              capture_output=True, text=True, check=True)
        current_branch = result.stdout.strip()
        tests.append(("当前分支", True, f"分支: {current_branch}"))
    except subprocess.CalledProcessError:
        tests.append(("当前分支", False, "无法获取分支信息"))
    
    return tests

def test_github_connectivity():
    """测试GitHub连接性"""
    print("🌐 测试GitHub连接性...")
    
    tests = []
    
    # 测试GitHub API连接
    try:
        with urllib.request.urlopen('https://api.github.com', timeout=10) as response:
            if response.status == 200:
                tests.append(("GitHub API连接", True, "可以访问GitHub API"))
            else:
                tests.append(("GitHub API连接", False, f"HTTP状态码: {response.status}"))
    except urllib.error.URLError as e:
        tests.append(("GitHub API连接", False, f"连接失败: {e}"))
    except Exception as e:
        tests.append(("GitHub API连接", False, f"未知错误: {e}"))
    
    # 检查是否可以推送到远程仓库
    try:
        result = subprocess.run(['git', 'ls-remote', 'origin'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            tests.append(("远程仓库访问", True, "可以访问远程仓库"))
        else:
            tests.append(("远程仓库访问", False, "无法访问远程仓库"))
    except subprocess.TimeoutExpired:
        tests.append(("远程仓库访问", False, "连接超时"))
    except subprocess.CalledProcessError:
        tests.append(("远程仓库访问", False, "远程仓库不存在或无权限"))
    except FileNotFoundError:
        tests.append(("远程仓库访问", False, "Git命令不可用"))
    
    return tests

def test_memory_prerequisites():
    """测试记忆功能前置条件"""
    print("🧠 测试记忆功能前置条件...")
    
    tests = []
    
    # 检查是否在Git根目录
    current_dir = Path.cwd()
    git_dir = current_dir / '.git'
    
    if git_dir.exists():
        tests.append(("Git根目录", True, f"当前目录是Git根目录: {current_dir}"))
    else:
        tests.append(("Git根目录", False, "当前目录不是Git根目录"))
    
    # 检查重要文件结构
    important_paths = [
        ('数学/', '数学学习目录'),
        ('数学/mcp/', 'MCP协议目录'),
        ('数学/mcp/AURA 协议.md', 'AURA基础协议'),
        ('数学/mcp/AURA-X-MCP(context7-mcp+寸止) 协议.md', 'AURA-X协议'),
        ('.gitignore', 'Git忽略文件')
    ]
    
    for path_str, description in important_paths:
        path = Path(path_str)
        if path.exists():
            tests.append((description, True, "存在"))
        else:
            tests.append((description, False, "不存在"))
    
    # 检查提交状态
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        if result.stdout.strip():
            tests.append(("工作区状态", False, "有未提交的更改"))
        else:
            tests.append(("工作区状态", True, "工作区干净"))
    except subprocess.CalledProcessError:
        tests.append(("工作区状态", False, "无法检查状态"))
    
    return tests

def test_push_capability():
    """测试推送能力"""
    print("📤 测试推送能力...")
    
    tests = []
    
    # 检查是否有提交历史
    try:
        result = subprocess.run(['git', 'log', '--oneline', '-1'], 
                              capture_output=True, text=True, check=True)
        if result.stdout.strip():
            tests.append(("提交历史", True, f"最新提交: {result.stdout.strip()[:50]}"))
        else:
            tests.append(("提交历史", False, "无提交历史"))
    except subprocess.CalledProcessError:
        tests.append(("提交历史", False, "无法获取提交历史"))
    
    # 检查远程分支状态
    try:
        result = subprocess.run(['git', 'branch', '-r'], 
                              capture_output=True, text=True, check=True)
        if 'origin/' in result.stdout:
            tests.append(("远程分支", True, "存在远程分支"))
        else:
            tests.append(("远程分支", False, "无远程分支"))
    except subprocess.CalledProcessError:
        tests.append(("远程分支", False, "无法检查远程分支"))
    
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

def generate_setup_commands():
    """生成设置命令"""
    commands = [
        "# GitHub仓库设置命令",
        "",
        "# 1. 初始化本地仓库（如果还没有）",
        "git init",
        "",
        "# 2. 配置用户信息（请替换为您的信息）",
        "git config user.name \"Your Name\"",
        "git config user.email \"your.email@example.com\"",
        "",
        "# 3. 添加远程仓库（请替换为您的GitHub仓库URL）",
        "git remote add origin https://github.com/yourusername/pvzHE-math-study.git",
        "",
        "# 4. 设置主分支",
        "git branch -M main",
        "",
        "# 5. 添加文件",
        "git add .gitignore",
        "git add 数学/",
        "git add *.py",
        "git add *.md",
        "",
        "# 6. 创建提交",
        "git commit -m \"Initial commit: 数学学习资料和MCP协议\"",
        "",
        "# 7. 推送到GitHub",
        "git push -u origin main",
        "",
        "# 8. 验证设置",
        "python test_github_memory_setup.py"
    ]
    
    return "\n".join(commands)

def main():
    """主测试函数"""
    print("🧪 开始GitHub仓库和记忆功能设置测试...")
    print(f"📍 当前工作目录: {Path.cwd()}")
    
    all_passed = True
    
    # 运行各项测试
    local_tests = test_local_git_setup()
    local_passed = print_test_results("本地Git设置测试", local_tests)
    
    github_tests = test_github_connectivity()
    github_passed = print_test_results("GitHub连接性测试", github_tests)
    
    memory_tests = test_memory_prerequisites()
    memory_passed = print_test_results("记忆功能前置条件测试", memory_tests)
    
    push_tests = test_push_capability()
    push_passed = print_test_results("推送能力测试", push_tests)
    
    all_passed = local_passed and github_passed and memory_passed and push_passed
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 所有测试通过！GitHub仓库和记忆功能已正确设置！")
        print("\n📝 记忆功能现在可以使用:")
        print("- `记忆` MCP工具可以存储项目规则和偏好")
        print("- `寸止` MCP工具可以控制交互流程")
        print("- GitHub仓库提供了持久化的版本控制")
    else:
        print("⚠️  部分测试未通过，请按照以下步骤设置")
        
        # 生成设置命令文件
        setup_commands = generate_setup_commands()
        with open('github_setup_commands.txt', 'w', encoding='utf-8') as f:
            f.write(setup_commands)
        
        print(f"\n📄 设置命令已保存到: github_setup_commands.txt")
        print("请按照文件中的命令逐步执行设置")

if __name__ == "__main__":
    main()
