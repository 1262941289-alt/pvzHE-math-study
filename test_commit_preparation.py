#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证文件提交准备
"""

import subprocess
import sys
from pathlib import Path

def test_git_status():
    """测试Git状态"""
    print("🔍 检查Git仓库状态...")
    
    tests = []
    
    # 检查是否在Git仓库中
    try:
        subprocess.run(['git', 'rev-parse', '--git-dir'], 
                      capture_output=True, text=True, check=True)
        tests.append(("Git仓库检测", True, "当前目录是Git仓库"))
    except subprocess.CalledProcessError:
        tests.append(("Git仓库检测", False, "当前目录不是Git仓库"))
        return tests
    
    # 检查Git状态
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        status_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        if status_lines:
            untracked = [line for line in status_lines if line.startswith('??')]
            staged = [line for line in status_lines if line.startswith('A')]
            modified = [line for line in status_lines if line.startswith('M')]
            
            tests.append(("未跟踪文件", len(untracked) > 0, f"发现 {len(untracked)} 个未跟踪文件"))
            tests.append(("暂存区文件", len(staged) > 0, f"暂存区有 {len(staged)} 个文件"))
            tests.append(("修改的文件", len(modified) == 0, f"有 {len(modified)} 个修改的文件"))
        else:
            tests.append(("工作区状态", True, "工作区干净"))
    except subprocess.CalledProcessError:
        tests.append(("Git状态检查", False, "无法检查Git状态"))
    
    return tests

def test_important_files():
    """测试重要文件是否存在"""
    print("📁 检查重要文件...")
    
    tests = []
    
    # 检查重要文件和目录
    important_items = [
        ('.gitignore', '文件', 'Git忽略文件'),
        ('数学/', '目录', '数学学习目录'),
        ('数学/mcp/', '目录', 'MCP协议目录'),
        ('数学/第22讲-线性方程组.md', '文件', '线性方程组笔记'),
        ('数学/mcp/AURA 协议.md', '文件', 'AURA基础协议'),
        ('数学/mcp/AURA-X-MCP(context7-mcp+寸止) 协议.md', '文件', 'AURA-X协议'),
        ('test_github_memory_setup.py', '文件', 'GitHub测试脚本'),
        ('github_setup_guide.md', '文件', 'GitHub设置指南')
    ]
    
    for item_path, item_type, description in important_items:
        path = Path(item_path)
        if path.exists():
            if item_type == '目录' and path.is_dir():
                file_count = len(list(path.rglob('*')))
                tests.append((description, True, f"目录存在，包含 {file_count} 个项目"))
            elif item_type == '文件' and path.is_file():
                size = path.stat().st_size
                tests.append((description, True, f"文件存在，大小 {size} 字节"))
            else:
                tests.append((description, False, f"类型不匹配（期望{item_type}）"))
        else:
            tests.append((description, False, "不存在"))
    
    return tests

def test_commit_readiness():
    """测试提交准备情况"""
    print("📦 检查提交准备情况...")
    
    tests = []
    
    # 检查是否有提交历史
    try:
        result = subprocess.run(['git', 'log', '--oneline', '-1'], 
                              capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            tests.append(("提交历史", True, f"最新提交: {result.stdout.strip()[:50]}"))
        else:
            tests.append(("提交历史", False, "无提交历史"))
    except subprocess.CalledProcessError:
        tests.append(("提交历史", False, "无提交历史"))
    
    # 检查暂存区
    try:
        result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                              capture_output=True, text=True, check=True)
        staged_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        if staged_files:
            tests.append(("暂存区文件", True, f"暂存区有 {len(staged_files)} 个文件"))
            
            # 检查重要文件是否在暂存区
            important_patterns = ['.gitignore', '数学/', '*.py', '*.md']
            found_patterns = []
            
            for pattern in important_patterns:
                if pattern == '数学/':
                    if any('数学/' in f for f in staged_files):
                        found_patterns.append(pattern)
                elif pattern.startswith('*.'):
                    ext = pattern[1:]
                    if any(f.endswith(ext) for f in staged_files):
                        found_patterns.append(pattern)
                else:
                    if pattern in staged_files:
                        found_patterns.append(pattern)
            
            tests.append(("重要文件暂存", len(found_patterns) >= 3, 
                         f"已暂存重要文件类型: {', '.join(found_patterns)}"))
        else:
            tests.append(("暂存区文件", False, "暂存区为空"))
    except subprocess.CalledProcessError:
        tests.append(("暂存区检查", False, "无法检查暂存区"))
    
    return tests

def show_git_commands():
    """显示Git命令参考"""
    print("\n" + "="*60)
    print("📋 文件提交命令参考")
    print("="*60)
    
    commands = [
        "# 1. 检查当前状态",
        "git status",
        "",
        "# 2. 添加重要文件到暂存区",
        "git add .gitignore",
        "git add 数学/",
        "git add *.py",
        "git add *.md",
        "git add *.json",
        "",
        "# 或者一次性添加所有重要文件",
        "git add .gitignore 数学/ *.py *.md *.json *.vim *.code-snippets",
        "",
        "# 3. 检查暂存区状态",
        "git status",
        "",
        "# 4. 创建提交",
        "git commit -m \"Initial commit: 数学学习资料和MCP协议文档\"",
        "",
        "# 5. 查看提交历史",
        "git log --oneline",
        "",
        "# 如果需要撤销暂存",
        "git reset HEAD <文件名>",
        "",
        "# 如果需要修改最后一次提交信息",
        "git commit --amend -m \"新的提交信息\""
    ]
    
    for cmd in commands:
        print(cmd)

def main():
    """主函数"""
    print("🧪 文件提交准备测试")
    print(f"📍 当前目录: {Path.cwd()}")
    
    all_tests = []
    
    # 运行各项测试
    git_tests = test_git_status()
    all_tests.extend(git_tests)
    
    file_tests = test_important_files()
    all_tests.extend(file_tests)
    
    commit_tests = test_commit_readiness()
    all_tests.extend(commit_tests)
    
    # 打印测试结果
    print(f"\n{'='*60}")
    print("📊 测试结果汇总")
    print('='*60)
    
    passed = 0
    total = len(all_tests)
    
    for test_desc, result, details in all_tests:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} {test_desc}: {details}")
        if result:
            passed += 1
    
    print(f"\n📈 总体结果: {passed}/{total} 项测试通过")
    
    # 根据结果给出建议
    if passed >= total * 0.8:  # 80%以上通过
        print("\n🎉 文件提交准备基本完成！")
        if passed == total:
            print("✅ 可以进行下一步：推送到GitHub")
        else:
            print("⚠️  有少量问题，但可以继续")
    else:
        print("\n⚠️  文件提交准备需要完善")
        show_git_commands()

if __name__ == "__main__":
    main()
