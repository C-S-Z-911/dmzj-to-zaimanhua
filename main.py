import json
import logging
import sys
import time

from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage.errors import PageDisconnectedError

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dmzj_to_zaimanhua.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 读取配置文件
try:
    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
        browser_path = config["browser_path"]
        load = config["load"]
        zaimanhua_url = config["zaimanhua_url"]
except FileNotFoundError as e:
    logger.error(f"config.json文件未找到: {e}")
except Exception as e:
    logger.error(f"config.json文件读取错误: {e}")

# 配置options
try:
    options = ChromiumOptions()
    options.set_browser_path(browser_path)
    page = ChromiumPage(addr_or_opts=options)
except FileNotFoundError as e:
    logger.error(f"未找到浏览器: {e}")
    sys.exit()
except Exception as e:
    logger.error(f"浏览器配置错误: {e}")
    sys.exit()

not_found = []
has_been_removed = []


# 订阅漫画
def subscription(subscription_name, search_name):
    # 查找漫画
    try:
        page.listen.start(f"{zaimanhua_url}/dynamic/{search_name}")
        page.get(f'{zaimanhua_url}/dynamic/{search_name}')
        page.ele(f'xpath://div[@class="tab-con autoHeight"]//a[@title="{subscription_name}"]/../../a',
                 timeout=1).click()
    except PageDisconnectedError as e:
        logger.error(f"浏览器已关闭: {e}")
        sys.exit()
    except Exception as e:
        logger.warning(f"未搜索到漫画-关键词: {search_name}")
        len_name = len(search_name)
        if len_name > 2:
            subscription(subscription_name, search_name[0:int(len_name / 2)])
        else:
            not_found.append(subscription_name)
            logger.error(f"未找到漫画: {subscription_name}\n Exception: {e}")
            logger.info("不存在或已被删除: " + str(has_been_removed))
            logger.info("未找到: " + str(not_found))
        return

    # 订阅漫画
    try:
        page.wait.load_start()
        # 延时 等待页面加载
        time.sleep(load)
        if page.ele(f'xpath://a[@id="subscribe_id_mh"]').text == "取消订阅":
            logger.warning(f"已经订阅: {subscription_name}")
        else:
            page.ele(f'xpath://a[text()="订阅收藏"]').click()
            try:
                if page.ele(f'xpath://div[@class="manhuaerrcon"]/p', timeout=0).text == "漫画不存在或已被删除":
                    has_been_removed.append(subscription_name)
                    logger.error(f"漫画不存在或已被删除: {subscription_name}")
                    logger.info("不存在或已被删除: " + str(has_been_removed))
                    logger.info("未找到: " + str(not_found))
                else:
                    logger.info(f"订阅成功:{subscription_name}")
            except Exception:
                logger.info(f"订阅成功:{subscription_name}")
    except PageDisconnectedError as e:
        logger.error(f"浏览器已关闭: {e}")
        sys.exit()
    except Exception as e:
        not_found.append("subscription_name")
        logger.info("不存在或已被删除: " + str(has_been_removed))
        logger.info("未找到: " + str(not_found))
        logger.error(f"订阅失败: {subscription_name}\n Exception: {e}")


def main():
    try:
        with open('all_subscriptions/all_subscriptions.json', 'r', encoding='utf-8') as file:
            all_subscriptions = json.load(file)

            # 循环订阅漫画
            for subscriptions in all_subscriptions:
                subscription(subscriptions["name"], subscriptions["name"])
        logger.info("不存在或已被删除: " + str(has_been_removed))
        logger.info("未找到: " + str(not_found))
    except FileNotFoundError as e:
        logger.error(f"all_subscriptions.json文件未找到: {e}")
    except Exception as e:
        logger.error(f"all_subscriptions.json文件读取错误: {e}")


if __name__ == "__main__":
    main()
