#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试MCP寸止工具连接
"""

import json
import sys
import subprocess
import os

def test_python_environment():
    """测试Python环境"""
    print("🔍 测试Python环境...")
    try:
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True)
        print(f"✅ Python版本: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"❌ Python环境错误: {e}")
        return False

def test_mcp_server():
    """测试MCP服务器"""
    print("\n🔍 测试寸止MCP服务器...")
    
    # 检查寸止.py文件是否存在
    if not os.path.exists("寸止.py"):
        print("❌ 寸止.py文件不存在")
        return False
    
    print("✅ 寸止.py文件存在")
    
    # 测试MCP协议初始化
    test_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    try:
        # 启动寸止服务器进程
        process = subprocess.Popen(
            [sys.executable, "寸止.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        
        # 发送初始化请求
        request_json = json.dumps(test_request, ensure_ascii=False) + "\n"
        stdout, stderr = process.communicate(input=request_json, timeout=5)
        
        if stdout:
            try:
                response = json.loads(stdout.strip())
                if "result" in response:
                    print("✅ MCP服务器响应正常")
                    print(f"   服务器信息: {response['result'].get('serverInfo', {})}")
                    return True
                else:
                    print(f"❌ MCP服务器响应异常: {response}")
                    return False
            except json.JSONDecodeError as e:
                print(f"❌ 响应JSON解析错误: {e}")
                print(f"   原始响应: {stdout}")
                return False
        else:
            print(f"❌ 无响应输出，错误信息: {stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ MCP服务器响应超时")
        process.kill()
        return False
    except Exception as e:
        print(f"❌ MCP服务器测试错误: {e}")
        return False

def test_cursor_config():
    """检查Cursor配置文件"""
    print("\n🔍 检查Cursor配置...")
    
    config_files = [
        "cursor-mcp-settings.json",
        "mcp-config.json"
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"✅ {config_file} 存在")
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    print(f"   配置有效，包含 {len(config)} 个配置项")
            except Exception as e:
                print(f"❌ {config_file} 格式错误: {e}")
        else:
            print(f"❌ {config_file} 不存在")

def main():
    """主测试函数"""
    print("🚀 开始MCP寸止工具连接测试\n")
    
    # 测试Python环境
    python_ok = test_python_environment()
    
    # 测试MCP服务器
    mcp_ok = test_mcp_server()
    
    # 检查配置文件
    test_cursor_config()
    
    print("\n📋 测试结果总结:")
    print(f"   Python环境: {'✅ 正常' if python_ok else '❌ 异常'}")
    print(f"   MCP服务器: {'✅ 正常' if mcp_ok else '❌ 异常'}")
    
    if python_ok and mcp_ok:
        print("\n🎉 MCP寸止工具基础功能正常！")
        print("📝 下一步：在Cursor中配置MCP设置")
        print("📖 请参考 'Cursor-MCP配置指导.md' 文件")
    else:
        print("\n⚠️  存在问题，请检查上述错误信息")
    
    return python_ok and mcp_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
