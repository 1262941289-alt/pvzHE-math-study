#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
寸止 (Cunzhi) MCP服务器实现
用于AI与用户之间的强制交互控制
"""

import json
import sys
import asyncio
from typing import Dict, List, Any, Optional

class CunzhiMCPServer:
    """寸止MCP服务器类"""
    
    def __init__(self):
        self.name = "寸止"
        self.version = "1.0.0"
        self.description = "寸止强制交互网关 - 控制AI与用户的所有交互"
        
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理MCP请求"""
        method = request.get("method", "")
        params = request.get("params", {})
        
        if method == "initialize":
            return await self.initialize(params)
        elif method == "tools/list":
            return await self.list_tools()
        elif method == "tools/call":
            return await self.call_tool(params)
        else:
            return {
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    async def initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """初始化MCP服务器"""
        return {
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": self.name,
                    "version": self.version
                }
            }
        }
    
    async def list_tools(self) -> Dict[str, Any]:
        """列出可用工具"""
        return {
            "result": {
                "tools": [
                    {
                        "name": "寸止询问",
                        "description": "向用户提出问题并等待回答",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "question": {
                                    "type": "string",
                                    "description": "要询问用户的问题"
                                },
                                "options": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "预定义的选项列表"
                                },
                                "context": {
                                    "type": "string",
                                    "description": "问题的上下文信息"
                                }
                            },
                            "required": ["question"]
                        }
                    },
                    {
                        "name": "寸止确认",
                        "description": "请求用户确认某个操作",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "action": {
                                    "type": "string",
                                    "description": "要确认的操作"
                                },
                                "details": {
                                    "type": "string",
                                    "description": "操作的详细信息"
                                }
                            },
                            "required": ["action"]
                        }
                    }
                ]
            }
        }
    
    async def call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具"""
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        
        if tool_name == "寸止询问":
            return await self.ask_user(arguments)
        elif tool_name == "寸止确认":
            return await self.confirm_action(arguments)
        else:
            return {
                "error": {
                    "code": -32602,
                    "message": f"Unknown tool: {tool_name}"
                }
            }
    
    async def ask_user(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """向用户询问问题"""
        question = arguments.get("question", "")
        options = arguments.get("options", [])
        context = arguments.get("context", "")
        
        # 构建询问消息
        message = f"🤔 **寸止询问**\n\n"
        if context:
            message += f"**上下文**: {context}\n\n"
        message += f"**问题**: {question}\n\n"
        
        if options:
            message += "**请选择**:\n"
            for i, option in enumerate(options, 1):
                message += f"{chr(64+i)}. {option}\n"
        
        # 这里应该实际向用户显示问题并等待回答
        # 目前返回一个模拟响应
        return {
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": message
                    }
                ]
            }
        }
    
    async def confirm_action(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """请求用户确认操作"""
        action = arguments.get("action", "")
        details = arguments.get("details", "")
        
        message = f"⚠️ **寸止确认**\n\n"
        message += f"**操作**: {action}\n\n"
        if details:
            message += f"**详情**: {details}\n\n"
        message += "**请确认是否继续执行此操作？**\n\n"
        message += "A. 确认执行\nB. 取消操作"
        
        return {
            "result": {
                "content": [
                    {
                        "type": "text", 
                        "text": message
                    }
                ]
            }
        }

async def main():
    """主函数"""
    # 设置标准输入输出编码
    import codecs
    sys.stdin = codecs.getreader('utf-8')(sys.stdin.detach())
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

    server = CunzhiMCPServer()

    # 读取标准输入的JSON-RPC请求
    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                break

            try:
                request = json.loads(line.strip())
                response = await server.handle_request(request)
                print(json.dumps(response, ensure_ascii=False))
                sys.stdout.flush()
            except json.JSONDecodeError:
                error_response = {
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                print(json.dumps(error_response, ensure_ascii=False))
                sys.stdout.flush()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        error_response = {
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }
        print(json.dumps(error_response, ensure_ascii=False))
        sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main())
