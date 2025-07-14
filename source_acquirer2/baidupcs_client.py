# source_acquirer2/baidupcs_client.py (v2 - 新增了切换目录功能)

import subprocess
import config
from datetime import datetime, timedelta
import re
import os


class BaiduPCSClient:
    """
    一个封装了 BaiduPCS-Go 命令行工具交互的客户端。
    """

    def __init__(self):
        self.executable_path = config.BAIDUPCS_CONFIG.get("executable_path")
        if not self.executable_path:
            raise ValueError("错误: 未在 config.py 中配置 BaiduPCS-Go 的可执行文件路径 (executable_path)。")

    def _execute_command(self, command: list) -> subprocess.CompletedProcess:
        """
        一个通用的内部命令执行函数，用于减少重复代码。
        """
        print(f"[*] [BaiduPCS] 准备执行命令: {' '.join(command)}")
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=300
            )
            print("[*] [BaiduPCS] 命令执行完毕，原始输出:")
            print("--- STDOUT ---\n" + result.stdout.strip())
            print("--- STDERR ---\n" + result.stderr.strip())
            print("----------------")
            return result
        except FileNotFoundError:
            raise RuntimeError(f"致命错误: 无法找到 BaiduPCS-Go 可执行文件于 {self.executable_path}")
        except subprocess.TimeoutExpired:
            raise RuntimeError("致命错误: 命令执行超时。")
        except Exception as e:
            raise RuntimeError(f"执行命令时发生未知异常: {e}")

    # --- 新增的切换目录函数 ---
    def change_remote_directory(self, remote_path: str) -> bool:
        """
        切换网盘的当前工作目录。

        :param remote_path: 目标目录，例如 "/"。
        :return: 成功返回 True，失败返回 False。
        """
        command = [self.executable_path, "cd", remote_path]
        result = self._execute_command(command)

        # 'cd'命令成功时，通常没有标准输出，且返回码为0
        if result.returncode == 0 and not result.stderr:
            print(f"✅ [BaiduPCS] 成功切换目录到: {remote_path}")
            return True
        else:
            print(f"❌ [BaiduPCS] 切换目录失败。")
            return False

    def clear_remote_directory(self, remote_path: str) -> bool:
        """
        清空指定的网盘远程目录下的所有文件。
        """
        if not remote_path.endswith('/'):
            remote_path += '/'

        command = [self.executable_path, "rm", f"{remote_path}*"]
        result = self._execute_command(command)

        if result.returncode == 0 and "操作成功" in result.stdout:
            print("✅ [BaiduPCS] 确认操作成功。")
            return True
        else:
            if "no such file or directory" in result.stderr.lower() or "文件或目录不存在" in result.stdout:
                print("✅ [BaiduPCS] 目录本身为空或不存在，视为清理成功。")
                return True

            print(f"❌ [BaiduPCS] 清理目录操作失败。返回码: {result.returncode}")
            return False

    def transfer_shared_link(self, share_link: str, password: str) -> bool:
        """
        转存一个带密码的百度网盘分享链接到当前工作目录。

        :param share_link: 完整的分享链接。
        :param password: 分享链接的提取码。
        :return: 如果成功转存则返回 True，否则返回 False。
        """
        # 兼容带 "pwd=" 的链接和不带的
        if "?pwd=" in share_link:
            command = [self.executable_path, "transfer", share_link]
        else:
            command = [self.executable_path, "transfer", share_link, password]

        result = self._execute_command(command)

        # 根据BaiduPCS-Go的输出特性，检查是否包含“转存成功”等关键字
        # 注意：这里的成功关键字需要根据实际运行输出来确定，"转存成功"是一个合理的初始猜测
        if result.returncode == 0 and ("链接转存到网盘成功" in result.stdout or "所有文件已存在" in result.stdout):
            print("✅ [BaiduPCS] 确认转存操作成功。")
            return True
        else:
            print(f"❌ [BaiduPCS] 转存操作失败。")
            return False

    def _parse_ls_output(self, ls_output: str) -> list[str]:
        """
        一个内部辅助函数，用于解析'ls'命令的输出，提取文件名。
        """
        filenames = []
        lines = ls_output.strip().split('\n')
        # 从 "----" 分割线后开始解析
        try:
            start_index = lines.index("----") + 1
        except ValueError:
            return []  # 如果没有找到分割线，返回空列表

        for line in lines[start_index:]:
            # 使用正则表达式匹配文件名，它能更好地处理文件名中的空格
            match = re.search(r'\s+\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+(.*)', line)
            if match:
                filenames.append(match.group(1).strip())
        return filenames

    def list_files_in_directory(self, remote_path: str) -> list[str] | None:
        """
        列出并解析指定网盘目录下的所有文件名。
        """
        # 先切换到该目录
        if not self.change_remote_directory(remote_path):
            return None  # 如果目录切换失败，则无法列出文件

        command = [self.executable_path, "ls"]
        result = self._execute_command(command)

        if result.returncode == 0:
            print(f"✅ [BaiduPCS] 成功列出目录 '{remote_path}' 的内容。")
            return self._parse_ls_output(result.stdout)
        else:
            print(f"❌ [BaiduPCS] 列出目录 '{remote_path}' 失败。")
            return None

    def get_recent_report_filenames(self, base_path: str, days: int = 10) -> list[str]:
        """
        智能地获取并筛选出最近指定天数内的研报文件名。
        """
        today = datetime.now()

        # 1. 尝试进入当月目录
        current_month_path = f"{base_path}/{today.year}/{today.month}月/"
        print(f"[*] [智能路径] 尝试进入当月目录: {current_month_path}")
        filenames = self.list_files_in_directory(current_month_path)

        # 2. 如果当月目录为空或不存在，则尝试上个月目录
        if not filenames:
            print(f"[*] [智能路径] 当月目录为空或不存在，回溯到上个月...")
            last_month_date = today - timedelta(days=today.day + 1)  # 确保跳到上个月
            last_month_path = f"{base_path}/{last_month_date.year}/{last_month_date.month}月/"
            print(f"[*] [智能路径] 尝试进入上个月目录: {last_month_path}")
            filenames = self.list_files_in_directory(last_month_path)

        if filenames is None:
            print("❌ [智能过滤] 最终未能获取到任何文件列表，操作中止。")
            return []

        # 3. 根据文件名中的日期进行过滤
        print(f"\n[*] [智能过滤] 开始从 {len(filenames)} 个文件中筛选最近 {days} 天的报告...")
        recent_files = []
        ten_days_ago = today - timedelta(days=days)

        for filename in filenames:
            try:
                # 从文件名中提取日期部分，例如 "2025-07-07"
                date_str = filename[:10]
                file_date = datetime.strptime(date_str, "%Y-%m-%d")

                if file_date >= ten_days_ago:
                    recent_files.append(filename)
                    print(f"    [匹配成功] {filename}")
            except (ValueError, IndexError):
                # 如果文件名不符合 "YYYY-MM-DD" 开头的格式，则忽略
                print(f"    [格式不匹配，已忽略] {filename}")
                continue

        print(f"✅ [智能过滤] 筛选完成，共找到 {len(recent_files)} 个符合条件的报告。")
        return recent_files

    def download_files(self, remote_filenames: list[str], save_dir: str) -> bool:
        """
        下载指定的一系列文件到本地目录。

        :param remote_filenames: 需要下载的网盘文件名列表。
        :param save_dir: 本地保存目录的路径。
        :return: 如果所有文件都下载成功或已存在，返回 True。
        """
        if not remote_filenames:
            print("[*] [下载] 没有需要下载的新文件。")
            return True

        # 确保本地保存目录存在
        os.makedirs(save_dir, exist_ok=True)

        # 构造下载命令: ./BaiduPCS-Go d 'file1.pdf' 'file2.pdf' ...
        command = [self.executable_path, "d", f"--saveto={save_dir}"] + remote_filenames

        result = self._execute_command(command)

        # BaiduPCS-Go下载成功时，通常会打印"下载成功"或"已存在, 跳过"
        # 简单的成功判断是检查返回码
        if result.returncode == 0:
            print("✅ [BaiduPCS] 确认下载命令执行成功。")
            return True
        else:
            print(f"❌ [BaiduPCS] 下载命令执行失败。")
            return False