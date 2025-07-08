# test_list_files.py (v15 - 终极完美版，精确解析最终数据结构)

import config
from baidupcs_py.baidupcs import BaiduPCS
from baidupcs_py.baidupcs.pcs import BaiduPCSError

# --- 测试配置 ---
SHARE_URL = config.BAIDU_SHARE_CONFIG.get("URL")
SHARE_PASSWORD = config.BAIDU_SHARE_CONFIG.get("PASSWORD")
BDUSS_COOKIE = config.BAIDU_CONFIG.get("BDUSS")
STOKEN_COOKIE = config.BAIDU_CONFIG.get("STOKEN")


def run_list_shared_files_test():
    """
    此版本根据真实的返回数据，精确解析文件列表。
    """
    print("=============================================")
    print("     百度网盘共享文件夹文件列表功能测试     ")
    print("=============================================")

    # ... (配置检查和客户端初始化部分保持不变) ...
    try:
        print("[1/3] 正在使用Cookies创建API客户端...")
        client = BaiduPCS(cookies={'BDUSS': BDUSS_COOKIE, 'STOKEN': STOKEN_COOKIE})
        print("✅ 客户端创建成功！")

        print(f"\n[2/3] 正在验证共享链接访问权限...")
        client.access_shared(SHARE_URL, SHARE_PASSWORD, "", "")
        print("✅ 共享链接访问权限验证成功！")

        print(f"\n[3/3] 正在请求文件列表元数据...")
        response_dict = client.shared_paths(SHARE_URL)

        # --- !! 核心改动在这里：直接处理 file_list !! ---
        if isinstance(response_dict, dict) and 'file_list' in response_dict:
            # `file_list` 的值直接就是我们想要的列表
            actual_files = response_dict['file_list']

            if isinstance(actual_files, list):
                print("\n✅ 文件列表解析成功！共享文件夹内容如下：")
                print("------------------------------------")
                if not actual_files:
                    print("    -> (这个共享文件夹是空的)")
                else:
                    # 这里的每一个 item 就是一个包含文件详细信息的字典
                    for item in actual_files:
                        is_dir = item.get('isdir', 0) == 1
                        filename = item.get('server_filename', '未知文件')
                        item_type = "[文件夹]" if is_dir else "[文件]"
                        print(f"    {item_type} {filename}")
                print("------------------------------------")
                print("\n🎉 恭喜！我们已彻底攻克了文件列表获取的难题！")
            else:
                print(f"❌ 解析失败：'file_list' 的值不是一个列表，而是 {type(actual_files)}。")
        else:
            print("❌ 解析失败：API返回的数据结构中未找到 'file_list' 键。")

    except Exception as e:
        print(f"\n❌ 发生未知错误: {e}")

    print("\n=============================================")
    print("                  测试结束                 ")
    print("=============================================")


if __name__ == "__main__":
    run_list_shared_files_test()