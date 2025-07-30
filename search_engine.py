#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件内容搜索引擎
支持多种搜索模式：关键词搜索、正则表达式搜索、模糊搜索等
"""

import os
import re
import json
import argparse
import subprocess
import platform
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from difflib import SequenceMatcher
import chardet

@dataclass
class SearchResult:
    """搜索结果数据类"""
    file_path: str
    line_number: int
    line_content: str
    match_text: str
    context_before: List[str] = None
    context_after: List[str] = None
    absolute_path: str = None

    def __post_init__(self):
        """初始化后处理"""
        if self.absolute_path is None:
            self.absolute_path = os.path.abspath(self.file_path)

class FileSearchEngine:
    """文件内容搜索引擎"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.supported_extensions = {
            '.txt', '.md', '.py', '.js', '.html', '.css', '.json', 
            '.xml', '.yml', '.yaml', '.ini', '.cfg', '.conf',
            '.java', '.cpp', '.c', '.h', '.cs', '.php', '.rb',
            '.go', '.rs', '.swift', '.kt', '.scala', '.sh', '.bat'
        }
        
    def detect_encoding(self, file_path: Path) -> str:
        """检测文件编码"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # 读取前10KB来检测编码
                result = chardet.detect(raw_data)
                return result['encoding'] or 'utf-8'
        except:
            return 'utf-8'
    
    def read_file_safely(self, file_path: Path) -> List[str]:
        """安全读取文件内容"""
        encoding = self.detect_encoding(file_path)
        try:
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                return f.readlines()
        except Exception as e:
            print(f"⚠️  无法读取文件 {file_path}: {e}")
            return []
    
    def get_files_to_search(self, extensions: Optional[List[str]] = None, 
                           exclude_dirs: Optional[List[str]] = None) -> List[Path]:
        """获取需要搜索的文件列表"""
        if extensions is None:
            extensions = self.supported_extensions
        else:
            extensions = set(ext if ext.startswith('.') else f'.{ext}' for ext in extensions)
        
        if exclude_dirs is None:
            exclude_dirs = {'.git', '__pycache__', 'node_modules', '.vscode', '.idea'}
        else:
            exclude_dirs = set(exclude_dirs)
        
        files = []
        for file_path in self.root_path.rglob('*'):
            # 跳过目录和排除的目录
            if file_path.is_dir():
                continue
            
            # 检查是否在排除目录中
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue
            
            # 检查文件扩展名
            if file_path.suffix.lower() in extensions:
                files.append(file_path)
        
        return files
    
    def search_keyword(self, keyword: str, case_sensitive: bool = False, 
                      whole_word: bool = False, context_lines: int = 0,
                      extensions: Optional[List[str]] = None,
                      exclude_dirs: Optional[List[str]] = None) -> List[SearchResult]:
        """关键词搜索"""
        results = []
        files = self.get_files_to_search(extensions, exclude_dirs)
        
        # 构建搜索模式
        if whole_word:
            pattern = r'\b' + re.escape(keyword) + r'\b'
        else:
            pattern = re.escape(keyword)
        
        flags = 0 if case_sensitive else re.IGNORECASE
        regex = re.compile(pattern, flags)
        
        for file_path in files:
            lines = self.read_file_safely(file_path)
            if not lines:
                continue
                
            for i, line in enumerate(lines):
                matches = regex.finditer(line)
                for match in matches:
                    # 获取上下文
                    context_before = []
                    context_after = []
                    
                    if context_lines > 0:
                        start_idx = max(0, i - context_lines)
                        end_idx = min(len(lines), i + context_lines + 1)
                        
                        context_before = [lines[j].rstrip() for j in range(start_idx, i)]
                        context_after = [lines[j].rstrip() for j in range(i + 1, end_idx)]
                    
                    result = SearchResult(
                        file_path=str(file_path.relative_to(self.root_path)),
                        line_number=i + 1,
                        line_content=line.rstrip(),
                        match_text=match.group(),
                        context_before=context_before,
                        context_after=context_after
                    )
                    results.append(result)
        
        return results
    
    def search_regex(self, pattern: str, context_lines: int = 0,
                    extensions: Optional[List[str]] = None,
                    exclude_dirs: Optional[List[str]] = None) -> List[SearchResult]:
        """正则表达式搜索"""
        results = []
        files = self.get_files_to_search(extensions, exclude_dirs)
        
        try:
            regex = re.compile(pattern, re.MULTILINE)
        except re.error as e:
            print(f"❌ 正则表达式错误: {e}")
            return results
        
        for file_path in files:
            lines = self.read_file_safely(file_path)
            if not lines:
                continue
                
            for i, line in enumerate(lines):
                matches = regex.finditer(line)
                for match in matches:
                    # 获取上下文
                    context_before = []
                    context_after = []
                    
                    if context_lines > 0:
                        start_idx = max(0, i - context_lines)
                        end_idx = min(len(lines), i + context_lines + 1)
                        
                        context_before = [lines[j].rstrip() for j in range(start_idx, i)]
                        context_after = [lines[j].rstrip() for j in range(i + 1, end_idx)]
                    
                    result = SearchResult(
                        file_path=str(file_path.relative_to(self.root_path)),
                        line_number=i + 1,
                        line_content=line.rstrip(),
                        match_text=match.group(),
                        context_before=context_before,
                        context_after=context_after
                    )
                    results.append(result)
        
        return results
    
    def fuzzy_search(self, query: str, threshold: float = 0.6, 
                    context_lines: int = 0, extensions: Optional[List[str]] = None,
                    exclude_dirs: Optional[List[str]] = None) -> List[SearchResult]:
        """模糊搜索"""
        results = []
        files = self.get_files_to_search(extensions, exclude_dirs)
        
        for file_path in files:
            lines = self.read_file_safely(file_path)
            if not lines:
                continue
                
            for i, line in enumerate(lines):
                # 计算相似度
                similarity = SequenceMatcher(None, query.lower(), line.lower()).ratio()
                
                if similarity >= threshold:
                    # 获取上下文
                    context_before = []
                    context_after = []
                    
                    if context_lines > 0:
                        start_idx = max(0, i - context_lines)
                        end_idx = min(len(lines), i + context_lines + 1)
                        
                        context_before = [lines[j].rstrip() for j in range(start_idx, i)]
                        context_after = [lines[j].rstrip() for j in range(i + 1, end_idx)]
                    
                    result = SearchResult(
                        file_path=str(file_path.relative_to(self.root_path)),
                        line_number=i + 1,
                        line_content=line.rstrip(),
                        match_text=f"相似度: {similarity:.2f}",
                        context_before=context_before,
                        context_after=context_after
                    )
                    results.append(result)
        
        return results

    def search_multiple_keywords(self, keywords: List[str], operator: str = "AND",
                                case_sensitive: bool = False, context_lines: int = 0,
                                extensions: Optional[List[str]] = None,
                                exclude_dirs: Optional[List[str]] = None) -> List[SearchResult]:
        """多关键词搜索"""
        results = []
        files = self.get_files_to_search(extensions, exclude_dirs)

        flags = 0 if case_sensitive else re.IGNORECASE
        patterns = [re.compile(re.escape(kw), flags) for kw in keywords]

        for file_path in files:
            lines = self.read_file_safely(file_path)
            if not lines:
                continue

            for i, line in enumerate(lines):
                matches = [pattern.search(line) for pattern in patterns]

                if operator.upper() == "AND":
                    # 所有关键词都必须匹配
                    if all(match for match in matches):
                        matched_keywords = [match.group() for match in matches if match]
                elif operator.upper() == "OR":
                    # 任意关键词匹配即可
                    if any(match for match in matches):
                        matched_keywords = [match.group() for match in matches if match]
                else:
                    continue

                if 'matched_keywords' in locals():
                    # 获取上下文
                    context_before = []
                    context_after = []

                    if context_lines > 0:
                        start_idx = max(0, i - context_lines)
                        end_idx = min(len(lines), i + context_lines + 1)

                        context_before = [lines[j].rstrip() for j in range(start_idx, i)]
                        context_after = [lines[j].rstrip() for j in range(i + 1, end_idx)]

                    result = SearchResult(
                        file_path=str(file_path.relative_to(self.root_path)),
                        line_number=i + 1,
                        line_content=line.rstrip(),
                        match_text=", ".join(matched_keywords),
                        context_before=context_before,
                        context_after=context_after
                    )
                    results.append(result)
                    del matched_keywords

        return results


class FileJumper:
    """文件跳转工具"""

    def __init__(self):
        # 导入增强的行跳转工具
        try:
            from line_jumper import AdvancedLineJumper
            self.advanced_jumper = AdvancedLineJumper()
        except ImportError:
            self.advanced_jumper = None

    def open_in_vscode(self, file_path: str, line_number: int = None):
        """在VSCode中打开文件并跳转到指定行"""
        if self.advanced_jumper and line_number:
            success, message = self.advanced_jumper.jump_to_line(file_path, line_number, 'auto')
            return success

        # 回退到原始方法
        vscode_commands = ['code', 'cursor', 'codium']

        for cmd in vscode_commands:
            try:
                if line_number:
                    full_cmd = f'{cmd} -g "{file_path}:{line_number}"'
                else:
                    full_cmd = f'{cmd} "{file_path}"'

                subprocess.run(full_cmd, shell=True, check=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except subprocess.CalledProcessError:
                continue

        return False

    @staticmethod
    def open_in_notepad(file_path: str):
        """在记事本中打开文件"""
        try:
            if platform.system() == "Windows":
                subprocess.run(f'notepad "{file_path}"', shell=True, check=True)
            else:
                subprocess.run(f'nano "{file_path}"', shell=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def open_in_default_editor(file_path: str):
        """用默认编辑器打开文件"""
        try:
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(f'open "{file_path}"', shell=True, check=True)
            else:  # Linux
                subprocess.run(f'xdg-open "{file_path}"', shell=True, check=True)
            return True
        except Exception:
            return False

    @staticmethod
    def open_file_location(file_path: str):
        """打开文件所在文件夹"""
        try:
            folder_path = os.path.dirname(file_path)
            if platform.system() == "Windows":
                subprocess.run(f'explorer "{folder_path}"', shell=True, check=True)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(f'open "{folder_path}"', shell=True, check=True)
            else:  # Linux
                subprocess.run(f'xdg-open "{folder_path}"', shell=True, check=True)
            return True
        except Exception:
            return False


class SearchResultFormatter:
    """搜索结果格式化器"""

    @staticmethod
    def format_console_interactive(results: List[SearchResult], show_context: bool = True,
                                 max_results: Optional[int] = None) -> str:
        """交互式控制台输出格式"""
        if not results:
            return "🔍 未找到匹配结果"

        if max_results:
            results = results[:max_results]

        output = []
        output.append(f"🎯 找到 {len(results)} 个匹配结果:\n")

        for i, result in enumerate(results, 1):
            output.append(f"[{i:2d}] 📁 {result.file_path}:{result.line_number}")
            output.append(f"     {result.line_content}")

            if show_context and (result.context_before or result.context_after):
                if result.context_before:
                    for ctx_line in result.context_before:
                        output.append(f"     │ {ctx_line}")

                output.append(f"  ➤  │ {result.line_content}")

                if result.context_after:
                    for ctx_line in result.context_after:
                        output.append(f"     │ {ctx_line}")

            output.append("")

        output.append("💡 操作提示:")
        output.append("   输入数字 + 回车: 在VSCode中打开对应文件")
        output.append("   输入数字 + 'n': 在记事本中打开")
        output.append("   输入数字 + 'f': 打开文件所在文件夹")
        output.append("   输入 'q': 退出")

        return "\n".join(output)

    @staticmethod
    def format_console(results: List[SearchResult], show_context: bool = True,
                      max_results: Optional[int] = None) -> str:
        """格式化为控制台输出"""
        if not results:
            return "🔍 未找到匹配结果"

        if max_results:
            results = results[:max_results]

        output = []
        output.append(f"🎯 找到 {len(results)} 个匹配结果:\n")

        current_file = None
        for result in results:
            # 文件分组显示
            if result.file_path != current_file:
                current_file = result.file_path
                output.append(f"📁 {current_file}")
                output.append("─" * 50)

            # 显示匹配行
            output.append(f"  📍 第 {result.line_number} 行: {result.match_text}")

            # 显示上下文
            if show_context and (result.context_before or result.context_after):
                if result.context_before:
                    for ctx_line in result.context_before:
                        output.append(f"     │ {ctx_line}")

                output.append(f"  ➤  │ {result.line_content}")

                if result.context_after:
                    for ctx_line in result.context_after:
                        output.append(f"     │ {ctx_line}")
            else:
                output.append(f"     {result.line_content}")

            output.append("")

        return "\n".join(output)

    @staticmethod
    def format_json(results: List[SearchResult]) -> str:
        """格式化为JSON输出"""
        json_results = []
        for result in results:
            json_result = {
                "file_path": result.file_path,
                "line_number": result.line_number,
                "line_content": result.line_content,
                "match_text": result.match_text
            }

            if result.context_before:
                json_result["context_before"] = result.context_before
            if result.context_after:
                json_result["context_after"] = result.context_after

            json_results.append(json_result)

        return json.dumps(json_results, ensure_ascii=False, indent=2)

    @staticmethod
    def format_html(results: List[SearchResult]) -> str:
        """格式化为HTML输出"""
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>搜索结果</title>
    <style>
        body { font-family: 'Consolas', monospace; margin: 20px; background-color: #f8f9fa; }
        .header { background-color: #007bff; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .result { margin-bottom: 15px; border: 1px solid #dee2e6; padding: 15px; background-color: white; border-radius: 5px; }
        .file-path { font-weight: bold; color: #0066cc; font-size: 16px; margin-bottom: 5px; }
        .line-number { color: #6c757d; font-size: 14px; }
        .match-text { background-color: #fff3cd; padding: 2px 4px; border-radius: 3px; }
        .line-content { background-color: #f8f9fa; padding: 10px; margin: 10px 0; border-left: 3px solid #007bff; font-family: monospace; }
        .context { color: #6c757d; font-style: italic; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 搜索结果</h1>
        <p>找到 """ + str(len(results)) + """ 个匹配结果</p>
    </div>
"""

        for result in results:
            html += f"""
    <div class="result">
        <div class="file-path">📁 {result.file_path}</div>
        <div class="line-number">📍 第 {result.line_number} 行</div>
        <div class="line-content">{result.line_content}</div>
        <div>匹配内容: <span class="match-text">{result.match_text}</span></div>
    </div>
"""

        html += """
</body>
</html>
"""
        return html


class InteractiveSearchEngine:
    """交互式搜索引擎"""

    def __init__(self, root_path: str = "."):
        self.engine = FileSearchEngine(root_path)
        self.jumper = FileJumper()

    def interactive_search(self, keyword: str, **kwargs):
        """交互式搜索"""
        print(f"🔍 搜索关键词: {keyword}")
        print("⏳ 搜索中...")

        results = self.engine.search_keyword(keyword, **kwargs)

        if not results:
            print("🔍 未找到匹配结果")
            return

        while True:
            # 显示结果
            output = SearchResultFormatter.format_console_interactive(results, max_results=20)
            print("\n" + output)

            # 获取用户输入
            try:
                user_input = input("\n请选择操作: ").strip().lower()

                if user_input == 'q':
                    print("👋 再见！")
                    break

                # 解析用户输入
                if user_input.isdigit():
                    # 纯数字，用VSCode打开
                    index = int(user_input) - 1
                    if 0 <= index < len(results):
                        result = results[index]
                        print(f"📂 在VSCode中打开: {result.file_path}:{result.line_number}")
                        if self.jumper.open_in_vscode(result.absolute_path, result.line_number):
                            print("✅ 文件已在VSCode中打开")
                        else:
                            print("❌ 无法打开VSCode，尝试默认编辑器...")
                            self.jumper.open_in_default_editor(result.absolute_path)
                    else:
                        print("❌ 无效的序号")

                elif user_input.endswith('n'):
                    # 数字+n，用记事本打开
                    try:
                        index = int(user_input[:-1]) - 1
                        if 0 <= index < len(results):
                            result = results[index]
                            print(f"📝 在记事本中打开: {result.file_path}")
                            if self.jumper.open_in_notepad(result.absolute_path):
                                print("✅ 文件已在记事本中打开")
                            else:
                                print("❌ 无法打开记事本")
                        else:
                            print("❌ 无效的序号")
                    except ValueError:
                        print("❌ 输入格式错误")

                elif user_input.endswith('f'):
                    # 数字+f，打开文件夹
                    try:
                        index = int(user_input[:-1]) - 1
                        if 0 <= index < len(results):
                            result = results[index]
                            print(f"📁 打开文件夹: {os.path.dirname(result.absolute_path)}")
                            if self.jumper.open_file_location(result.absolute_path):
                                print("✅ 文件夹已打开")
                            else:
                                print("❌ 无法打开文件夹")
                        else:
                            print("❌ 无效的序号")
                    except ValueError:
                        print("❌ 输入格式错误")

                else:
                    print("❌ 无效的输入，请重试")
                    print("💡 提示: 输入数字打开文件，数字+n用记事本打开，数字+f打开文件夹，q退出")

            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
            except EOFError:
                print("\n👋 再见！")
                break


def main():
    """命令行主函数"""
    parser = argparse.ArgumentParser(description="文件内容搜索引擎",
                                   formatter_class=argparse.RawDescriptionHelpFormatter,
                                   epilog="""
使用示例:
  python search_engine.py -k "函数" -p "数学"                    # 在数学目录下搜索"函数"
  python search_engine.py -r "def\s+\w+" -e py                  # 用正则表达式搜索Python函数定义
  python search_engine.py -m "原函数" "积分" -o AND             # 搜索同时包含"原函数"和"积分"的行
  python search_engine.py -f "不定积分" -t 0.7                  # 模糊搜索相似度0.7以上的内容
  python search_engine.py -k "定义" -c 2 --json > result.json  # 搜索并输出JSON格式
""")

    # 搜索模式选择
    search_group = parser.add_mutually_exclusive_group(required=True)
    search_group.add_argument('-k', '--keyword', help='关键词搜索')
    search_group.add_argument('-r', '--regex', help='正则表达式搜索')
    search_group.add_argument('-m', '--multiple', nargs='+', help='多关键词搜索')
    search_group.add_argument('-f', '--fuzzy', help='模糊搜索')

    # 搜索选项
    parser.add_argument('-p', '--path', default='.', help='搜索路径 (默认: 当前目录)')
    parser.add_argument('-e', '--extensions', nargs='+', help='文件扩展名过滤 (如: py js md)')
    parser.add_argument('-x', '--exclude', nargs='+', help='排除目录 (如: .git __pycache__)')
    parser.add_argument('-c', '--context', type=int, default=0, help='显示上下文行数 (默认: 0)')
    parser.add_argument('-i', '--ignore-case', action='store_true', help='忽略大小写')
    parser.add_argument('-w', '--whole-word', action='store_true', help='全词匹配')
    parser.add_argument('-o', '--operator', choices=['AND', 'OR'], default='AND',
                       help='多关键词搜索操作符 (默认: AND)')
    parser.add_argument('-t', '--threshold', type=float, default=0.6,
                       help='模糊搜索相似度阈值 (默认: 0.6)')

    # 输出选项
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    parser.add_argument('--html', help='输出HTML文件')
    parser.add_argument('--max-results', type=int, help='最大结果数量')
    parser.add_argument('--no-context', action='store_true', help='不显示上下文')
    parser.add_argument('--interactive', '-I', action='store_true', help='交互式模式，支持文件跳转')

    args = parser.parse_args()

    # 交互式模式
    if args.interactive:
        interactive_engine = InteractiveSearchEngine(args.path)
        if args.keyword:
            interactive_engine.interactive_search(
                args.keyword,
                case_sensitive=not args.ignore_case,
                whole_word=args.whole_word,
                context_lines=args.context,
                extensions=args.extensions,
                exclude_dirs=args.exclude
            )
        else:
            print("❌ 交互式模式需要指定关键词")
        return

    # 创建搜索引擎
    engine = FileSearchEngine(args.path)

    # 执行搜索
    results = []
    try:
        if args.keyword:
            results = engine.search_keyword(
                args.keyword,
                case_sensitive=not args.ignore_case,
                whole_word=args.whole_word,
                context_lines=args.context,
                extensions=args.extensions,
                exclude_dirs=args.exclude
            )
        elif args.regex:
            results = engine.search_regex(
                args.regex,
                context_lines=args.context,
                extensions=args.extensions,
                exclude_dirs=args.exclude
            )
        elif args.multiple:
            results = engine.search_multiple_keywords(
                args.multiple,
                operator=args.operator,
                case_sensitive=not args.ignore_case,
                context_lines=args.context,
                extensions=args.extensions,
                exclude_dirs=args.exclude
            )
        elif args.fuzzy:
            results = engine.fuzzy_search(
                args.fuzzy,
                threshold=args.threshold,
                context_lines=args.context,
                extensions=args.extensions,
                exclude_dirs=args.exclude
            )
    except KeyboardInterrupt:
        print("\n⚠️  搜索被用户中断")
        return
    except Exception as e:
        print(f"❌ 搜索过程中发生错误: {e}")
        return

    # 输出结果
    if args.json:
        print(SearchResultFormatter.format_json(results))
    elif args.html:
        html_content = SearchResultFormatter.format_html(results)
        with open(args.html, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ HTML结果已保存到: {args.html}")
    else:
        show_context = not args.no_context and args.context > 0
        output = SearchResultFormatter.format_console(results, show_context, args.max_results)
        print(output)


if __name__ == "__main__":
    main()
