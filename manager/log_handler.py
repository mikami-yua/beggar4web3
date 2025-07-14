# manager/log_handler.py

import os


def read_processed_files(log_path: str) -> set:
    """
    读取已处理文件的日志，并返回一个包含所有文件名的集合。
    使用集合(set)可以极大地提高后续的查找效率。

    :param log_path: 日志文件的完整路径。
    :return: 一个包含所有已处理文件名的集合。
    """
    # 检查日志文件所在的目录是否存在，如果不存在则创建
    log_dir = os.path.dirname(log_path)
    if not os.path.exists(log_dir):
        print(f"[*] [日志] 日志目录不存在，正在创建: {log_dir}")
        os.makedirs(log_dir, exist_ok=True)

    # 检查日志文件是否存在，如果不存在则创建一个空的
    if not os.path.exists(log_path):
        print(f"[*] [日志] 日志文件不存在，已创建空文件: {log_path}")
        return set()  # 返回一个空集合

    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            # 读取所有行，并移除每行末尾的换行符
            processed_files = {line.strip() for line in f if line.strip()}
        print(f"[*] [日志] 成功加载 {len(processed_files)} 条已处理记录。")
        return processed_files
    except Exception as e:
        print(f"❌ [日志] 读取日志文件时发生错误: {e}")
        return set()


def log_processed_file(log_path: str, filename: str):
    """
    将一个新处理完成的文件名追加到日志文件的末尾。

    :param log_path: 日志文件的完整路径。
    :param filename: 需要记录的文件名。
    """
    try:
        # 使用 'a' 模式 (append) 来追加内容，而不是覆盖
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(filename + '\n')
        print(f"[*] [日志] 已成功记录新文件: {filename}")
    except Exception as e:
        print(f"❌ [日志] 写入日志文件时发生错误: {e}")