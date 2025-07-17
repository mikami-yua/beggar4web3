# test_transfer_and_process.py (最终版 - 增加“创建目录”步骤)

import config
from baidupcs_py.baidupcs import BaiduPCS
from baidupcs_py.baidupcs.pcs import BaiduPCSError

# --- 配置 ---
TARGET_ROOT_FOLDER_NAME = "2025年摩根大通研报"
MY_PAN_SAVE_DIR = "/auto_saved_reports" # 我们要把文件存到自己网盘的这个目录下

# --- 从config读取 ---
SHARE_URL = config.BAIDU_SHARE_CONFIG.get("URL")
SHARE_PASSWORD = config.BAIDU_SHARE_CONFIG.get("PASSWORD")
BDUSS_COOKIE = config.BAIDU_CONFIG.get("BDUSS")
STOKEN_COOKIE = config.BAIDU_CONFIG.get("STOKEN")

def run_final_workflow_test():
    print("=============================================")
    print("     百度网盘转存并处理功能 (最终方案测试)    ")
    print("=============================================")
    try:
        # --- 1. 初始化客户端 ---
        print("[1/6] 正在初始化客户端...")
        client = BaiduPCS(cookies={'BDUSS': BDUSS_COOKIE, 'STOKEN': STOKEN_COOKIE})
        print("✅ 客户端初始化成功！")

        # --- 2. 验证并获取共享链接的元数据 ---
        print("\n[2/6] 正在访问共享链接...")
        client.access_shared(SHARE_URL, SHARE_PASSWORD, "", "")
        response_dict = client.shared_paths(SHARE_URL)
        print("✅ 共享链接访问成功！")

        # --- 3. 找到目标文件夹的 `fs_id` ---
        print(f"\n[3/6] 正在根目录寻找目标文件夹: '{TARGET_ROOT_FOLDER_NAME}'...")
        target_folder_info = None
        for item in response_dict.get('file_list', []):
            if item.get('server_filename') == TARGET_ROOT_FOLDER_NAME and item.get('isdir') == 1:
                target_folder_info = item
                break
        if not target_folder_info:
            print(f"❌ 失败：在共享链接根目录未找到文件夹 '{TARGET_ROOT_FOLDER_NAME}'。")
            return
        fs_id = target_folder_info.get('fs_id')
        print(f"✅ 找到目标文件夹！其 fs_id 为: {fs_id}")

        # --- 4. !! 新增步骤 !! 在自己的网盘中创建目标目录 ---
        print(f"\n[4/6] 正在你的网盘中创建保存目录: '{MY_PAN_SAVE_DIR}'...")
        try:
            client.makedir(MY_PAN_SAVE_DIR)
            print(f"✅ 目录 '{MY_PAN_SAVE_DIR}' 创建成功或已存在。")
        except BaiduPCSError as e:
            # 如果目录已存在，可能会报错，但我们可以忽略它并继续
            if "dir is exist" in str(e).lower():
                print(f"✅ 目录 '{MY_PAN_SAVE_DIR}' 已存在，无需重复创建。")
            else:
                # 如果是其他错误，则抛出
                raise e

        # --- 5. 执行转存操作 ---
        print(f"\n[5/6] 正在将文件夹转存到你的网盘目录: '{MY_PAN_SAVE_DIR}'...")
        uk = response_dict.get('uk')
        shareid = response_dict.get('shareid')
        bdstoken = response_dict.get('bdstoken')
        client.transfer_shared_paths(MY_PAN_SAVE_DIR, [fs_id], uk, shareid, bdstoken, SHARE_URL)
        print(f"✅ 转存命令执行成功！")

        # --- 6. 验证转存结果 ---
        my_pan_target_path = f"{MY_PAN_SAVE_DIR}/{TARGET_ROOT_FOLDER_NAME}"
        print(f"\n[6/6] 正在你自己的网盘中验证已转存的文件夹: '{my_pan_target_path}'...")
        my_files = client.list(my_pan_target_path)

        print("\n✅ 操作成功！已转存文件夹内容如下：")
        print("------------------------------------")
        for file_info in my_files:
            item_type = "[文件夹]" if file_info.is_dir else "[文件]"
            print(f"    {item_type} {file_info.filename}")
        print("------------------------------------")
        print("\n🎉 恭喜！我们已经实现了从“侦查”->“缴获”->“盘点”的全链路！")

    except Exception as e:
        print(f"\n❌ 发生未知错误: {e}")

    print("\n=============================================")
    print("                  测试结束                 ")
    print("=============================================")

if __name__ == "__main__":
    run_final_workflow_test()