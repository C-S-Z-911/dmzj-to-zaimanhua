import json
import logging
import sys
import time
from typing import List, Dict, Any

from DrissionPage import ChromiumPage, ChromiumOptions

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dmzj_to_zaimanhua.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 全局变量
not_found: List[str] = []
has_been_removed: List[str] = []


def setup_browser() -> ChromiumPage:
    """设置并返回浏览器实例"""
    try:
        with open('config.json', 'r', encoding='utf-8') as file:
            config = json.load(file)
            browser_path = config.get("browser_path", "")

        options = ChromiumOptions()
        if browser_path:
            options.set_browser_path(browser_path)
        else:
            logger.warning("未在配置文件中找到浏览器路径，使用默认浏览器")

        page = ChromiumPage(addr_or_opts=options)
        logger.info("浏览器初始化成功")
        return page

    except FileNotFoundError as e:
        logger.error(f"配置文件或浏览器未找到: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"浏览器初始化失败: {e}")
        sys.exit(1)


def subscription(page: ChromiumPage, subscription_name: str, search_name: str) -> None:
    """订阅漫画函数"""
    try:
        # 设置监听并搜索
        page.listen.start(f"https://manhua.zaimanhua.com/dynamic/{search_name}")
        page.get(f'https://manhua.zaimanhua.com/dynamic/{search_name}')

        # 尝试点击搜索结果
        try:
            page.ele(f'xpath://div[@class="tab-con autoHeight"]//a[@title="{subscription_name}"]/../../a',
                     timeout=2).click()
        except Exception:
            logger.warning(f"未搜索到漫画-关键词: {search_name}")
            # 如果搜索失败，尝试使用更短的关键词
            if len(search_name) > 2:
                subscription(page, subscription_name, search_name[0:len(search_name) // 2])
            else:
                not_found.append(subscription_name)
                logger.error(f"未找到漫画: {subscription_name}")
            return

        # 等待页面加载
        page.wait.load_start()
        time.sleep(2)  # 等待页面完全加载

        # 检查订阅状态
        subscribe_btn = page.ele('xpath://a[@id="subscribe_id_mh"]', timeout=3)
        if subscribe_btn.text == "取消订阅":
            logger.info(f"已经订阅: {subscription_name}")
            return

        # 尝试订阅
        page.ele('xpath://a[text()="订阅收藏"]').click()
        time.sleep(1)  # 等待订阅操作完成

        # 检查是否订阅成功
        try:
            error_msg = page.ele('xpath://div[@class="manhuaerrcon"]/p', timeout=1)
            if error_msg.text == "漫画不存在或已被删除":
                has_been_removed.append(subscription_name)
                logger.error(f"漫画不存在或已被删除: {subscription_name}")
            else:
                logger.info(f"订阅成功: {subscription_name}")
        except Exception:
            # 如果没有错误消息，则认为订阅成功
            logger.info(f"订阅成功: {subscription_name}")

    except Exception as e:
        logger.error(f"处理漫画 '{subscription_name}' 时发生错误: {e}")
        not_found.append(subscription_name)


def load_subscriptions(file_path: str) -> List[Dict[str, Any]]:
    """加载订阅列表"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"订阅文件未找到: {file_path}")
        return []
    except json.JSONDecodeError:
        logger.error(f"订阅文件格式错误: {file_path}")
        return []


def main():
    """主函数"""
    # 初始化浏览器
    page = setup_browser()

    # 加载订阅列表
    all_subscriptions = load_subscriptions('output/all_subscriptions.json')
    if not all_subscriptions:
        logger.error("没有可用的订阅数据，程序退出")
        return

    logger.info(f"开始处理 {len(all_subscriptions)} 个订阅")

    # 循环订阅漫画
    for i, subscription_data in enumerate(all_subscriptions, 1):
        name = subscription_data.get("name", "")
        if not name:
            logger.warning(f"跳过第 {i} 个无名称的订阅")
            continue

        logger.info(f"处理第 {i}/{len(all_subscriptions)} 个订阅: {name}")
        subscription(page, name, name)

        # 添加短暂延迟，避免请求过于频繁
        if i < len(all_subscriptions):
            time.sleep(1)

    # 输出最终结果
    if has_been_removed:
        logger.info(f"不存在或已被删除的漫画: {has_been_removed}")

    if not_found:
        logger.info(f"未找到的漫画: {not_found}")

    success_count = len(all_subscriptions) - len(has_been_removed) - len(not_found)
    logger.info(f"处理完成! 成功: {success_count}, 失败: {len(has_been_removed) + len(not_found)}")

    # 关闭浏览器
    try:
        page.quit()
        logger.info("浏览器已关闭")
    except Exception as e:
        logger.warning(f"关闭浏览器时发生错误: {e}")


if __name__ == "__main__":
    main()