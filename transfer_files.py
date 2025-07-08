# main.py (Final Version - 基于黄金版导航并增加耐心等待)

import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import config

# --- 核心配置 ---
REPORTS_ROOT_FOLDER_NAME = "2025年摩根大通研报"
TARGET_MONTH_FOLDER_NAME = "6月"
MY_PAN_SAVE_DIR = "AI-temp-pdf"

# --- 从config读取 ---
SHARE_URL = config.BAIDU_SHARE_CONFIG.get("URL")
SHARE_PASSWORD = config.BAIDU_SHARE_CONFIG.get("PASSWORD")
BDUSS = config.BAIDU_CONFIG.get("BDUSS")
STOKEN = config.BAIDU_CONFIG.get("STOKEN")


def run_final_transfer():
    driver = None
    try:
        # --- 1. 初始化并登录 ---
        print("[1/4] 正在初始化浏览器...")
        driver = webdriver.Chrome()
        driver.get("https://pan.baidu.com/")
        driver.add_cookie({"name": "BDUSS", "value": BDUSS})
        driver.add_cookie({"name": "STOKEN", "value": STOKEN})
        print("✅ Cookie注入成功！")

        # --- 2. 打开分享链接并处理提取码 ---
        print(f"\n[2/4] 正在打开分享链接...")
        driver.get(SHARE_URL)
        if SHARE_PASSWORD:
            try:
                password_input = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "accessCode")))
                if not password_input.get_attribute('value'):
                    password_input.send_keys(SHARE_PASSWORD)
                submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "submitBtn")))
                submit_button.click()
                print("✅ 提取码提交成功！")
            except TimeoutException:
                print("✅ 未发现提取码输入框，直接进入。")

        # --- 3. 逐层导航 ---
        print("\n[3/4] 正在开始逐层导航...")

        # 等待根目录列表加载
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "file-name")))

        path_components = [REPORTS_ROOT_FOLDER_NAME, str(datetime.now().year)]
        for folder_name in path_components:
            print(f"    -> 正在进入: '{folder_name}'...")
            folder_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//a[@title='{folder_name}']")))
            folder_link.click()
            # 增加更长的强制等待，确保JS有时间重绘页面
            print("        -> 等待页面刷新...")
            time.sleep(5)

        print("✅ 已成功导航到年份文件夹。")

        # --- 4. 勾选并执行转存 ---
        print(f"\n[4/4] 正在勾选并转存 '{TARGET_MONTH_FOLDER_NAME}' 文件夹...")

        # 定位并勾选目标文件夹
        target_item_container = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.XPATH, f"//div[contains(@class, 'file-item') and .//a[@title='{TARGET_MONTH_FOLDER_NAME}']]")))
        checkbox = target_item_container.find_element(By.CLASS_NAME, "checkbox")
        checkbox.click()
        print(f"    -> ✅ 已成功勾选文件夹: '{TARGET_MONTH_FOLDER_NAME}'")
        time.sleep(1)

        # 点击“保存到网盘”按钮
        print("    -> 正在点击“保存到网盘”...")
        save_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(@class, 'save-button')]//span[contains(text(), '保存')]")))
        save_button.click()

        # 在弹窗中选择路径并确认
        print("    -> 正在处理路径选择弹窗...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "tree-view")))
        target_save_folder = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, f"//span[@class='tree-node-title-text' and text()='{MY_PAN_SAVE_DIR}']")))
        target_save_folder.click()

        confirm_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'dialog-button-ok')]//span[text()='确定']")))
        confirm_button.click()
        print("    -> ✅ 转存命令已发送！")

        # 等待转存成功
        time.sleep(5)

        print("\n🎉🎉🎉 任务圆满完成！🎉🎉🎉")
        print("程序将在10秒后自动关闭。")
        time.sleep(10)

    except Exception as e:
        print(f"\n❌ 发生未知错误: {e}")
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    run_final_transfer()