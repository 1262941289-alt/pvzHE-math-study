#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web界面搜索引擎
提供简单的Web界面来使用搜索功能
"""

from flask import Flask, render_template_string, request, jsonify
from search_engine import FileSearchEngine, SearchResultFormatter, FileJumper
import os
import subprocess
import platform

app = Flask(__name__)

# HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>文件内容搜索引擎</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Microsoft YaHei', Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 10px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header { 
            background: linear-gradient(45deg, #667eea, #764ba2); 
            color: white; 
            padding: 30px; 
            text-align: center; 
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.1em; opacity: 0.9; }
        .search-form { 
            padding: 30px; 
            background: #f8f9fa; 
        }
        .form-group { 
            margin-bottom: 20px; 
        }
        .form-group label { 
            display: block; 
            margin-bottom: 5px; 
            font-weight: bold; 
            color: #333; 
        }
        .form-control { 
            width: 100%; 
            padding: 12px; 
            border: 2px solid #ddd; 
            border-radius: 5px; 
            font-size: 16px; 
            transition: border-color 0.3s;
        }
        .form-control:focus { 
            outline: none; 
            border-color: #667eea; 
        }
        .form-row { 
            display: flex; 
            gap: 20px; 
        }
        .form-row .form-group { 
            flex: 1; 
        }
        .btn { 
            background: linear-gradient(45deg, #667eea, #764ba2); 
            color: white; 
            padding: 12px 30px; 
            border: none; 
            border-radius: 5px; 
            font-size: 16px; 
            cursor: pointer; 
            transition: transform 0.2s;
        }
        .btn:hover { 
            transform: translateY(-2px); 
        }
        .results { 
            padding: 30px; 
            max-height: 600px; 
            overflow-y: auto; 
        }
        .result-item { 
            background: #f8f9fa; 
            border: 1px solid #dee2e6; 
            border-radius: 5px; 
            padding: 15px; 
            margin-bottom: 15px; 
        }
        .file-path { 
            font-weight: bold; 
            color: #0066cc; 
            margin-bottom: 5px; 
        }
        .line-info { 
            color: #6c757d; 
            font-size: 14px; 
            margin-bottom: 10px; 
        }
        .line-content { 
            background: white; 
            padding: 10px; 
            border-left: 3px solid #667eea; 
            font-family: 'Consolas', monospace; 
            white-space: pre-wrap; 
        }
        .match-highlight {
            background-color: #fff3cd;
            padding: 2px 4px;
            border-radius: 3px;
        }
        .action-buttons {
            margin-top: 10px;
            display: flex;
            gap: 10px;
        }
        .action-btn {
            padding: 5px 10px;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
            transition: background-color 0.2s;
        }
        .btn-vscode {
            background-color: #007acc;
            color: white;
        }
        .btn-vscode:hover {
            background-color: #005a9e;
        }
        .btn-folder {
            background-color: #28a745;
            color: white;
        }
        .btn-folder:hover {
            background-color: #1e7e34;
        }
        .btn-notepad {
            background-color: #6c757d;
            color: white;
        }
        .btn-notepad:hover {
            background-color: #545b62;
        }
        .loading { 
            text-align: center; 
            padding: 50px; 
            color: #6c757d; 
        }
        .no-results { 
            text-align: center; 
            padding: 50px; 
            color: #6c757d; 
        }
        .search-options { 
            background: #e9ecef; 
            padding: 20px; 
            border-radius: 5px; 
            margin-bottom: 20px; 
        }
        .checkbox-group { 
            display: flex; 
            gap: 20px; 
            flex-wrap: wrap; 
        }
        .checkbox-item { 
            display: flex; 
            align-items: center; 
            gap: 5px; 
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 文件内容搜索引擎</h1>
            <p>快速搜索文件内容，支持关键词、正则表达式和模糊搜索</p>
        </div>
        
        <div class="search-form">
            <form id="searchForm">
                <div class="form-group">
                    <label for="query">搜索内容</label>
                    <input type="text" id="query" name="query" class="form-control" 
                           placeholder="输入关键词、正则表达式或模糊搜索内容" required>
                </div>
                
                <div class="search-options">
                    <div class="form-group">
                        <label>搜索模式</label>
                        <div class="checkbox-group">
                            <div class="checkbox-item">
                                <input type="radio" id="keyword" name="search_type" value="keyword" checked>
                                <label for="keyword">关键词搜索</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="radio" id="regex" name="search_type" value="regex">
                                <label for="regex">正则表达式</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="radio" id="fuzzy" name="search_type" value="fuzzy">
                                <label for="fuzzy">模糊搜索</label>
                            </div>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="extensions">文件扩展名 (用空格分隔)</label>
                            <input type="text" id="extensions" name="extensions" class="form-control" 
                                   placeholder="例如: py js md txt">
                        </div>
                        <div class="form-group">
                            <label for="context">上下文行数</label>
                            <input type="number" id="context" name="context" class="form-control" 
                                   value="2" min="0" max="10">
                        </div>
                    </div>
                    
                    <div class="checkbox-group">
                        <div class="checkbox-item">
                            <input type="checkbox" id="ignore_case" name="ignore_case">
                            <label for="ignore_case">忽略大小写</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="whole_word" name="whole_word">
                            <label for="whole_word">全词匹配</label>
                        </div>
                    </div>
                </div>
                
                <button type="submit" class="btn">🔍 开始搜索</button>
            </form>
        </div>
        
        <div id="results" class="results" style="display: none;"></div>
    </div>

    <script>
        document.getElementById('searchForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const resultsDiv = document.getElementById('results');
            
            // 显示加载状态
            resultsDiv.style.display = 'block';
            resultsDiv.innerHTML = '<div class="loading">🔄 搜索中，请稍候...</div>';
            
            try {
                const response = await fetch('/search', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.error) {
                    resultsDiv.innerHTML = `<div class="no-results">❌ 错误: ${data.error}</div>`;
                    return;
                }
                
                if (data.results.length === 0) {
                    resultsDiv.innerHTML = '<div class="no-results">🔍 未找到匹配结果</div>';
                    return;
                }
                
                // 显示结果
                let html = `<h3>🎯 找到 ${data.results.length} 个匹配结果</h3>`;
                
                data.results.forEach((result, index) => {
                    html += `
                        <div class="result-item">
                            <div class="file-path">📁 ${result.file_path}</div>
                            <div class="line-info">📍 第 ${result.line_number} 行</div>
                            <div class="line-content">${result.line_content}</div>
                            <div style="margin-top: 10px;">
                                <span class="match-highlight">匹配: ${result.match_text}</span>
                            </div>
                            <div class="action-buttons">
                                <button class="action-btn btn-vscode" onclick="openInVSCode('${result.file_path}', ${result.line_number})">
                                    📝 VSCode打开
                                </button>
                                <button class="action-btn btn-folder" onclick="openFolder('${result.file_path}')">
                                    📁 打开文件夹
                                </button>
                                <button class="action-btn btn-notepad" onclick="openInNotepad('${result.file_path}')">
                                    📄 记事本打开
                                </button>
                            </div>
                        </div>
                    `;
                });
                
                resultsDiv.innerHTML = html;
                
            } catch (error) {
                resultsDiv.innerHTML = `<div class="no-results">❌ 搜索失败: ${error.message}</div>`;
            }
        });

        // 文件跳转函数
        async function openInVSCode(filePath, lineNumber) {
            try {
                const response = await fetch('/open-file', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        action: 'vscode',
                        file_path: filePath,
                        line_number: lineNumber
                    })
                });

                const result = await response.json();
                if (result.success) {
                    showNotification('✅ 文件已在VSCode中打开', 'success');
                } else {
                    showNotification('❌ 无法打开VSCode: ' + result.error, 'error');
                }
            } catch (error) {
                showNotification('❌ 操作失败: ' + error.message, 'error');
            }
        }

        async function openFolder(filePath) {
            try {
                const response = await fetch('/open-file', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        action: 'folder',
                        file_path: filePath
                    })
                });

                const result = await response.json();
                if (result.success) {
                    showNotification('✅ 文件夹已打开', 'success');
                } else {
                    showNotification('❌ 无法打开文件夹: ' + result.error, 'error');
                }
            } catch (error) {
                showNotification('❌ 操作失败: ' + error.message, 'error');
            }
        }

        async function openInNotepad(filePath) {
            try {
                const response = await fetch('/open-file', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        action: 'notepad',
                        file_path: filePath
                    })
                });

                const result = await response.json();
                if (result.success) {
                    showNotification('✅ 文件已在记事本中打开', 'success');
                } else {
                    showNotification('❌ 无法打开记事本: ' + result.error, 'error');
                }
            } catch (error) {
                showNotification('❌ 操作失败: ' + error.message, 'error');
            }
        }

        function showNotification(message, type) {
            // 创建通知元素
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 10px 20px;
                border-radius: 5px;
                color: white;
                font-weight: bold;
                z-index: 1000;
                animation: slideIn 0.3s ease-out;
                background-color: ${type === 'success' ? '#28a745' : '#dc3545'};
            `;
            notification.textContent = message;

            document.body.appendChild(notification);

            // 3秒后自动移除
            setTimeout(() => {
                notification.remove();
            }, 3000);
        }

        // 添加CSS动画
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
        document.head.appendChild(style);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """主页"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/search', methods=['POST'])
def search():
    """搜索API"""
    try:
        query = request.form.get('query', '').strip()
        search_type = request.form.get('search_type', 'keyword')
        extensions = request.form.get('extensions', '').strip()
        context = int(request.form.get('context', 0))
        ignore_case = 'ignore_case' in request.form
        whole_word = 'whole_word' in request.form
        
        if not query:
            return jsonify({'error': '请输入搜索内容'})
        
        # 处理文件扩展名
        ext_list = extensions.split() if extensions else None
        
        # 创建搜索引擎
        engine = FileSearchEngine('.')
        
        # 执行搜索
        results = []
        if search_type == 'keyword':
            results = engine.search_keyword(
                query,
                case_sensitive=not ignore_case,
                whole_word=whole_word,
                context_lines=context,
                extensions=ext_list
            )
        elif search_type == 'regex':
            results = engine.search_regex(
                query,
                context_lines=context,
                extensions=ext_list
            )
        elif search_type == 'fuzzy':
            results = engine.fuzzy_search(
                query,
                threshold=0.6,
                context_lines=context,
                extensions=ext_list
            )
        
        # 限制结果数量
        if len(results) > 100:
            results = results[:100]
        
        # 转换为JSON格式
        json_results = []
        for result in results:
            json_results.append({
                'file_path': result.file_path,
                'line_number': result.line_number,
                'line_content': result.line_content,
                'match_text': result.match_text
            })
        
        return jsonify({'results': json_results})
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/open-file', methods=['POST'])
def open_file():
    """文件操作API"""
    try:
        data = request.get_json()
        action = data.get('action')
        file_path = data.get('file_path')
        line_number = data.get('line_number')

        if not file_path:
            return jsonify({'success': False, 'error': '文件路径不能为空'})

        # 转换为绝对路径
        abs_path = os.path.abspath(file_path)

        if not os.path.exists(abs_path):
            return jsonify({'success': False, 'error': '文件不存在'})

        jumper = FileJumper()
        success = False

        if action == 'vscode':
            success = jumper.open_in_vscode(abs_path, line_number)
        elif action == 'folder':
            success = jumper.open_file_location(abs_path)
        elif action == 'notepad':
            success = jumper.open_in_notepad(abs_path)
        else:
            return jsonify({'success': False, 'error': '不支持的操作类型'})

        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': '操作失败'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("🚀 启动Web搜索引擎...")
    print("📍 访问地址: http://localhost:5000")
    print("🔒 仅本机访问模式")
    print("⚠️  按 Ctrl+C 停止服务")
    # 使用 host='127.0.0.1' 确保只能本机访问
    app.run(debug=True, host='127.0.0.1', port=5000)
