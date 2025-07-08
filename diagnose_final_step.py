# diagnose_final_step.py (终极诊断脚本 - 只为收集导航成功后的证据)

import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import config

# --- 我们要诊断的目标 ---
REPORTS_ROOT_FOLDER_NAME = "2025年摩根大通研报"
YEAR_FOLDER_NAME = "2025"
TARGET_MONTH_FOLDER_NAME = "6月"

# --- 从config读取配置 ---
SHARE_URL = config.BAIDU_SHARE_CONFIG.get("URL")
SHARE_PASSWORD = config.BAIDU_SHARE_CONFIG.get("PASSWORD")
BDUSS = config.BAIDU_CONFIG.get("BDUSS")
STOKEN = config.BAIDU_CONFIG.get("STOKEN")


def run_final_diagnostics():
    """
    这个脚本的唯一目的，是严格按照已成功的版本导航到“6月”文件夹，
    然后立即记录下它看到的一切，并截图保存。
    """
    print("=============================================")
    print("      导航后状态诊断程序 (黑匣子模式)      ")
    print("=============================================")
    driver = None
    try:
        # --- 1. 使用我们已验证成功的代码，进行登录和导航 ---
        print("[1/2] 正在初始化并导航到最终诊断点...")
        driver = webdriver.Chrome()
        driver.get("https://pan.baidu.com/")
        driver.add_cookie({"name": "BDUSS", "value": BDUSS})
        driver.add_cookie({"name": "STOKEN", "value": STOKEN})
        driver.get(SHARE_URL)
        if SHARE_PASSWORD:
            try:
                password_input = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.ID, "accessCode")))
                if not password_input.get_attribute('value'):
                    password_input.send_keys(SHARE_PASSWORD)
                submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "submitBtn")))
                submit_button.click()
            except TimeoutException:
                pass

                # 导航
        print("    -> 正在进入第一层...")
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[@title='{REPORTS_ROOT_FOLDER_NAME}']"))).click()
        time.sleep(3)
        print("    -> 正在进入第二层...")
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[@title='{YEAR_FOLDER_NAME}']"))).click()
        time.sleep(3)
        print("    -> 正在进入第三层...")
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[@title='{TARGET_MONTH_FOLDER_NAME}']"))).click()
        print("✅ 已成功点击进入 '6月' 文件夹。")

        # --- 2. 核心诊断区域 ---
        print("\n[2/2] 已到达最终诊断点，现在开始强制等待并收集信息...")

        # 用一个更长的、强制性的等待，确保所有可能的JS都已执行完毕
        print("    -> 正在强制等待8秒，让页面完全渲染...")
        time.sleep(8)

        # 保存证据：无论如何，都进行截图和保存页面源码
        screenshot_path = "final_diagnostic_screenshot.png"
        page_source_path = "final_diagnostic_page.html"

        print("\n    -> [保存证据] 正在进行截图...")
        driver.save_screenshot(screenshot_path)
        print(f"    -> ✅ 截图已保存到: {screenshot_path}")

        print("\n    -> [保存证据] 正在保存页面源码...")
        with open(page_source_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"    -> ✅ 页面源码已保存到: {page_source_path}")

        print("\n诊断程序已执行完毕，请分析收集到的证据。")
        time.sleep(10)

    except Exception as e:
        print(f"\n❌ 在诊断过程中发生未知错误: {e}")
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    run_final_diagnostics()