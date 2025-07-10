# notifier/email_sender.py (最终简洁版)

import smtplib
import time
from email.mime.text import MIMEText
from email.header import Header

import config
from .formatters import format_analysis_for_email

# 重试配置
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 10

def send_analysis_report(analysis_json: dict, source_filename: str):
    """发送一份格式化后的新闻分析报告。"""
    subject, body = format_analysis_for_email(analysis_json, source_filename)
    _send_email(subject, body)

def _send_email(subject: str, body: str):
    """通用的内部邮件发送函数，使用直接的SSL连接并包含重试逻辑。"""
    if not hasattr(config, 'EMAIL_CONFIG') or not config.EMAIL_CONFIG.get("use_email"):
        print("[*] 邮件发送功能在config.py中被禁用。")
        return False

    conf = config.EMAIL_CONFIG
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['From'] = Header(f"新闻分析Agent <{conf['sender_email']}>", 'utf-8')
    msg['To'] = Header(f"管理员 <{conf['receiver_email']}>", 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"[*] [邮件发送] 正在进行第 {attempt}/{MAX_RETRIES} 次尝试...")
        try:
            # 使用最简单、最直接的 SMTP_SSL 连接方式
            with smtplib.SMTP_SSL(conf['smtp_server'], conf['port'], timeout=20) as server:
                server.login(conf['sender_email'], conf['password'])
                server.sendmail(conf['sender_email'], [conf['receiver_email']], msg.as_string())
            print(f"✅ [邮件发送] 成功！邮件已发送到 {conf['receiver_email']}。")
            return True
        except Exception as e:
            print(f"⚠️ [邮件发送] 第 {attempt} 次尝试失败，错误: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                print("❌ [邮件发送] 已达到最大重试次数，发送失败。")
    return False