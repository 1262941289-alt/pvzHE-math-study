#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub仓库验证脚本
验证GitHub仓库设置的完整性和功能性
"""

import subprocess
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path
import time

def run_command(cmd, timeout=30):
    """安全执行命令"""
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            shell=True if isinstance(cmd, str) else False
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "命令执行超时"
    except Exception as e:
        return False, "", str(e)

def test_git_installation():
    """测试Git是否正确安装"""
    print("🔧 测试Git安装...")
    
    tests = []
    
    # 检查Git版本
    success, output, error = run_command(['git', '--version'])
    if success:
        tests.append(("Git安装", True, f"版本: {output}"))
    else:
        tests.append(("Git安装", False, "Git未安装或不在PATH中"))
        return tests
    
    # 检查Git配置
    success, name, _ = run_command(['git', 'config', 'user.name'])
    success2, email, _ = run_command(['git', 'config', 'user.email'])
    
    if success and name:
        tests.append(("Git用户名", True, f"用户名: {name}"))
    else:
        tests.append(("Git用户名", False, "未配置用户名"))
    
    if success2 and email:
        tests.append(("Git邮箱", True, f"邮箱: {email}"))
    else:
        tests.append(("Git邮箱", False, "未配置邮箱"))
    
    return tests

def test_local_repository():
    """测试本地仓库状态"""
    print("📁 测试本地仓库...")
    
    tests = []
    
    # 检查是否在Git仓库中
    success, output, error = run_command(['git', 'rev-parse', '--git-dir'])
    if success:
        tests.append(("本地Git仓库", True, "仓库已初始化"))
    else:
        tests.append(("本地Git仓库", False, "当前目录不是Git仓库"))
        return tests
    
    # 检查当前分支
    success, branch, _ = run_command(['git', 'branch', '--show-current'])
    if success and branch:
        tests.append(("当前分支", True, f"分支: {branch}"))
    else:
        tests.append(("当前分支", False, "无当前分支或无提交"))
    
    # 检查工作区状态
    success, status, _ = run_command(['git', 'status', '--porcelain'])
    if success:
        if status:
            lines = status.split('\n')
            untracked = len([l for l in lines if l.startswith('??')])
            staged = len([l for l in lines if l.startswith('A')])
            modified = len([l for l in lines if l.startswith('M')])
            tests.append(("工作区状态", True, f"未跟踪:{untracked}, 暂存:{staged}, 修改:{modified}"))
        else:
            tests.append(("工作区状态", True, "工作区干净"))
    else:
        tests.append(("工作区状态", False, "无法检查工作区状态"))
    
    # 检查提交历史
    success, commits, _ = run_command(['git', 'log', '--oneline', '-5'])
    if success and commits:
        commit_count = len(commits.split('\n'))
        tests.append(("提交历史", True, f"有 {commit_count} 个提交"))
    else:
        tests.append(("提交历史", False, "无提交历史"))
    
    return tests

def test_remote_repository():
    """测试远程仓库连接"""
    print("🌐 测试远程仓库...")
    
    tests = []
    
    # 检查远程仓库配置
    success, remotes, _ = run_command(['git', 'remote', '-v'])
    if success and remotes:
        remote_lines = remotes.split('\n')
        origin_lines = [line for line in remote_lines if line.startswith('origin')]
        
        if origin_lines:
            tests.append(("远程仓库配置", True, f"已配置 {len(origin_lines)} 个远程连接"))
            
            # 检查GitHub URL
            github_found = any('github.com' in line for line in origin_lines)
            if github_found:
                tests.append(("GitHub仓库", True, "已连接到GitHub"))
            else:
                tests.append(("GitHub仓库", False, "未连接到GitHub"))
        else:
            tests.append(("远程仓库配置", False, "未配置origin远程仓库"))
    else:
        tests.append(("远程仓库配置", False, "无远程仓库配置"))
        return tests
    
    # 测试远程仓库连接
    print("   正在测试远程连接...")
    success, output, error = run_command(['git', 'ls-remote', 'origin'], timeout=60)
    if success:
        tests.append(("远程仓库连接", True, "可以连接到远程仓库"))
    else:
        if "authentication" in error.lower() or "permission" in error.lower():
            tests.append(("远程仓库连接", False, "认证失败，需要配置访问权限"))
        elif "not found" in error.lower():
            tests.append(("远程仓库连接", False, "远程仓库不存在"))
        else:
            tests.append(("远程仓库连接", False, f"连接失败: {error[:100]}"))
    
    return tests

def test_github_connectivity():
    """测试GitHub网络连接"""
    print("🔗 测试GitHub连接性...")
    
    tests = []
    
    # 测试GitHub API
    try:
        with urllib.request.urlopen('https://api.github.com', timeout=10) as response:
            if response.status == 200:
                tests.append(("GitHub API", True, "可以访问GitHub API"))
            else:
                tests.append(("GitHub API", False, f"HTTP状态码: {response.status}"))
    except urllib.error.URLError as e:
        tests.append(("GitHub API", False, f"网络连接失败: {e}"))
    except Exception as e:
        tests.append(("GitHub API", False, f"连接错误: {e}"))
    
    # 测试GitHub网站
    try:
        with urllib.request.urlopen('https://github.com', timeout=10) as response:
            if response.status == 200:
                tests.append(("GitHub网站", True, "可以访问GitHub网站"))
            else:
                tests.append(("GitHub网站", False, f"HTTP状态码: {response.status}"))
    except Exception as e:
        tests.append(("GitHub网站", False, f"访问失败: {e}"))
    
    return tests

def test_important_files():
    """测试重要文件存在性"""
    print("📄 测试重要文件...")
    
    tests = []
    
    # 检查重要文件
    important_files = [
        ('.gitignore', 'Git忽略文件'),
        ('数学/', '数学学习目录'),
        ('数学/mcp/', 'MCP协议目录'),
        ('数学/第22讲-线性方程组.md', '线性方程组笔记'),
        ('github_setup_guide.md', 'GitHub设置指南')
    ]
    
    for file_path, description in important_files:
        path = Path(file_path)
        if path.exists():
            if path.is_dir():
                file_count = len(list(path.rglob('*')))
                tests.append((description, True, f"目录存在，包含 {file_count} 个项目"))
            else:
                size = path.stat().st_size
                tests.append((description, True, f"文件存在，大小 {size} 字节"))
        else:
            tests.append((description, False, "文件不存在"))
    
    return tests

def test_memory_functionality():
    """测试记忆功能前置条件"""
    print("🧠 测试记忆功能...")
    
    tests = []
    
    # 检查Git根目录
    current_dir = Path.cwd()
    git_dir = current_dir / '.git'
    
    if git_dir.exists():
        tests.append(("Git根目录", True, f"当前目录是Git根目录"))
        tests.append(("记忆功能前置", True, "记忆MCP工具可以使用"))
    else:
        tests.append(("Git根目录", False, "当前目录不是Git根目录"))
        tests.append(("记忆功能前置", False, "记忆MCP工具无法使用"))
    
    # 检查MCP协议文件
    mcp_files = [
        '数学/mcp/AURA 协议.md',
        '数学/mcp/AURA-X-MCP(context7-mcp+寸止) 协议.md'
    ]
    
    mcp_count = 0
    for mcp_file in mcp_files:
        if Path(mcp_file).exists():
            mcp_count += 1
    
    if mcp_count > 0:
        tests.append(("MCP协议文件", True, f"找到 {mcp_count} 个协议文件"))
    else:
        tests.append(("MCP协议文件", False, "未找到MCP协议文件"))
    
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

def generate_fix_commands():
    """生成修复命令"""
    commands = [
        "# GitHub仓库问题修复命令",
        "",
        "# 如果Git未安装，请下载安装：",
        "# https://git-scm.com/download/win",
        "",
        "# 如果用户信息未配置：",
        "git config --global user.name \"您的姓名\"",
        "git config --global user.email \"您的邮箱\"",
        "",
        "# 如果未初始化仓库：",
        "git init",
        "",
        "# 如果未添加远程仓库：",
        "git remote add origin https://github.com/您的用户名/您的仓库名.git",
        "",
        "# 如果需要设置中文显示：",
        "git config --global core.quotepath false",
        "",
        "# 如果需要添加文件：",
        "git add .gitignore 数学/ *.py *.md",
        "",
        "# 如果需要创建提交：",
        "git commit -m \"Initial commit: 数学学习资料\"",
        "",
        "# 如果需要推送到GitHub：",
        "git push -u origin main"
    ]
    
    return "\n".join(commands)

def main():
    """主函数"""
    print("🧪 GitHub仓库完整性验证")
    print(f"📍 当前目录: {Path.cwd()}")
    print(f"⏰ 测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_passed = True
    
    # 运行所有测试
    git_passed = print_test_results("Git安装测试", test_git_installation())
    local_passed = print_test_results("本地仓库测试", test_local_repository())
    remote_passed = print_test_results("远程仓库测试", test_remote_repository())
    github_passed = print_test_results("GitHub连接测试", test_github_connectivity())
    files_passed = print_test_results("重要文件测试", test_important_files())
    memory_passed = print_test_results("记忆功能测试", test_memory_functionality())
    
    all_passed = all([git_passed, local_passed, remote_passed, github_passed, files_passed, memory_passed])
    
    # 总结
    print("\n" + "="*60)
    print("🎯 总体评估")
    print("="*60)
    
    if all_passed:
        print("🎉 所有测试通过！GitHub仓库设置完美！")
        print("\n✅ 您现在可以：")
        print("- 使用记忆MCP工具进行知识管理")
        print("- 使用寸止MCP工具进行交互控制")
        print("- 正常进行Git版本控制")
        print("- 与GitHub仓库同步")
    else:
        print("⚠️  部分测试未通过，需要修复")
        
        # 保存修复命令
        fix_commands = generate_fix_commands()
        with open('github_fix_commands.txt', 'w', encoding='utf-8') as f:
            f.write(fix_commands)
        
        print(f"\n📄 修复命令已保存到: github_fix_commands.txt")
        print("请根据失败的测试项目执行相应的修复命令")
    
    print(f"\n📊 测试完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
