# navigate_util.py
# 一个专门负责“导航”任务的、可复用的模块

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import config

# --- 导航目标配置 ---
REPORTS_ROOT_FOLDER_NAME = "2025年摩根大通研报"
TARGET_PATH_COMPONENTS = ["2025年摩根大通研报", "2025"]


def navigate_to_target_folder():
    """
    一个可复用的函数，负责完整的导航流程。
    成功后，它不会关闭浏览器，而是会返回driver对象，交由后续模块处理。
    """
    print("--- [导航模块] 开始执行 ---")
    driver = None
    try:
        # 1. 初始化并登录
        print("    -> 正在初始化并登录...")
        driver = webdriver.Chrome()
        driver.get("https://pan.baidu.com/")
        driver.add_cookie({"name": "BDUSS", "value": config.BAIDU_CONFIG.get("BDUSS")})
        driver.add_cookie({"name": "STOKEN", "value": config.BAIDU_CONFIG.get("STOKEN")})
        print("    -> Cookie注入成功。")

        # 2. 打开分享链接
        print("    -> 正在打开分享链接...")
        driver.get(config.BAIDU_SHARE_CONFIG.get("URL"))
        if config.BAIDU_SHARE_CONFIG.get("PASSWORD"):
            try:
                password_input = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.ID, "accessCode")))
                if not password_input.get_attribute('value'):
                    password_input.send_keys(config.BAIDU_SHARE_CONFIG.get("PASSWORD"))
                submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "submitBtn")))
                submit_button.click()
            except TimeoutException:
                pass  # 如果没有提取码框，就直接继续
        print("    -> 已进入分享链接。")

        # 3. 逐层导航
        print("    -> 正在开始逐层导航...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "file-name")))
        time.sleep(2)
        for folder_name in TARGET_PATH_COMPONENTS:
            print(f"        -> 正在进入: '{folder_name}'...")
            folder_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//a[contains(@class, 'filename') and @title='{folder_name}']"))
            )
            folder_link.click()
            time.sleep(3)

        print("--- ✅ [导航模块] 成功导航到目标文件夹！---")
        # 成功后，返回driver对象，让其他模块可以接管
        return driver

    except Exception as e:
        print(f"--- ❌ [导航模块] 执行失败: {e} ---")
        if driver:
            driver.quit()  # 如果中途失败，就关闭浏览器
        return None


# 这部分是用于独立测试这个导航模块的
if __name__ == '__main__':
    print("正在独立测试导航模块...")
    active_driver = navigate_to_target_folder()
    if active_driver:
        print("导航测试成功！浏览器将在10秒后关闭。")
        time.sleep(10)
        active_driver.quit()
    else:
        print("导航测试失败。")