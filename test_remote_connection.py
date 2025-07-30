#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证远程仓库连接
"""

import subprocess
import sys
from pathlib import Path

def test_remote_setup():
    """测试远程仓库设置"""
    print("🔍 测试远程仓库连接...")
    
    tests = []
    
    # 检查是否在Git仓库中
    try:
        subprocess.run(['git', 'rev-parse', '--git-dir'], 
                      capture_output=True, text=True, check=True)
        tests.append(("Git仓库检测", True, "当前目录是Git仓库"))
    except subprocess.CalledProcessError:
        tests.append(("Git仓库检测", False, "当前目录不是Git仓库"))
        return tests
    
    # 检查远程仓库配置
    try:
        result = subprocess.run(['git', 'remote', '-v'], 
                              capture_output=True, text=True, check=True)
        if result.stdout.strip():
            lines = result.stdout.strip().split('\n')
            origin_lines = [line for line in lines if line.startswith('origin')]
            if origin_lines:
                tests.append(("远程仓库配置", True, f"已配置 {len(origin_lines)} 个远程连接"))
                
                # 检查URL格式
                for line in origin_lines:
                    if 'github.com' in line and '.git' in line:
                        tests.append(("GitHub URL格式", True, "URL格式正确"))
                        break
                else:
                    tests.append(("GitHub URL格式", False, "URL格式可能有误"))
            else:
                tests.append(("远程仓库配置", False, "未找到origin远程仓库"))
        else:
            tests.append(("远程仓库配置", False, "未配置任何远程仓库"))
    except subprocess.CalledProcessError:
        tests.append(("远程仓库配置", False, "无法检查远程仓库配置"))
    
    # 测试远程仓库连接
    try:
        result = subprocess.run(['git', 'ls-remote', 'origin'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            tests.append(("远程仓库连接", True, "可以连接到远程仓库"))
        else:
            error_msg = result.stderr.strip() if result.stderr else "连接失败"
            tests.append(("远程仓库连接", False, f"连接失败: {error_msg}"))
    except subprocess.TimeoutExpired:
        tests.append(("远程仓库连接", False, "连接超时"))
    except subprocess.CalledProcessError as e:
        tests.append(("远程仓库连接", False, f"连接错误: {e}"))
    except FileNotFoundError:
        tests.append(("远程仓库连接", False, "Git命令不可用"))
    
    # 检查分支设置
    try:
        result = subprocess.run(['git', 'branch', '--show-current'], 
                              capture_output=True, text=True, check=True)
        current_branch = result.stdout.strip()
        if current_branch:
            tests.append(("当前分支", True, f"分支: {current_branch}"))
        else:
            tests.append(("当前分支", False, "无当前分支"))
    except subprocess.CalledProcessError:
        tests.append(("当前分支", False, "无法获取分支信息"))
    
    return tests

def get_remote_info():
    """获取远程仓库信息"""
    try:
        result = subprocess.run(['git', 'remote', '-v'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "无法获取远程仓库信息"

def print_setup_commands():
    """打印设置命令"""
    print("\n" + "="*60)
    print("📋 远程仓库设置命令参考")
    print("="*60)
    
    commands = [
        "# 1. 添加远程仓库（请替换为您的实际URL）",
        "git remote add origin https://github.com/您的用户名/您的仓库名.git",
        "",
        "# 2. 设置主分支",
        "git branch -M main",
        "",
        "# 3. 验证远程仓库",
        "git remote -v",
        "",
        "# 4. 测试连接",
        "git ls-remote origin",
        "",
        "# 如果需要删除错误的远程仓库配置：",
        "git remote remove origin",
        "",
        "# 然后重新添加正确的远程仓库"
    ]
    
    for cmd in commands:
        print(cmd)

def main():
    """主函数"""
    print("🧪 远程仓库连接测试")
    print(f"📍 当前目录: {Path.cwd()}")
    
    # 运行测试
    tests = test_remote_setup()
    
    print(f"\n{'='*60}")
    print("📊 测试结果")
    print('='*60)
    
    passed = 0
    total = len(tests)
    
    for test_desc, result, details in tests:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} {test_desc}: {details}")
        if result:
            passed += 1
    
    print(f"\n📈 总体结果: {passed}/{total} 项测试通过")
    
    # 显示当前远程仓库配置
    print(f"\n📡 当前远程仓库配置:")
    remote_info = get_remote_info()
    if remote_info:
        print(remote_info)
    else:
        print("未配置远程仓库")
    
    # 根据测试结果给出建议
    if passed == total:
        print("\n🎉 远程仓库连接设置完成！")
        print("✅ 可以进行下一步：提交和推送文件")
    else:
        print("\n⚠️  远程仓库设置需要完善")
        print_setup_commands()

if __name__ == "__main__":
    main()
