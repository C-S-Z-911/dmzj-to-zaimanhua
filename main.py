import json
import logging
import sys
import time

from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage.errors import PageDisconnectedError

# 配置日志
# 创建logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 创建文件处理器，使用UTF-8编码
file_handler = logging.FileHandler('dmzj_to_zaimanhua.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)

# 创建控制台处理器
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# 创建日志格式
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 添加处理器到logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 移除默认的根logger处理器（如果有）
logging.getLogger().handlers = []

# 设置根logger级别
logging.getLogger().setLevel(logging.INFO)

# 读取配置文件
try:
    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
        browser_path = config["browser_path"]
        wait_load = config["wait_load"]
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
been_removed = []


def get_finding_failed():
    logger.info("不存在或已被删除: " + str(been_removed))
    logger.info("未找到: " + str(not_found) + "\n")


def validate_manga():
    try:
        time.sleep(wait_load)
        if page.ele(f'xpath://div[@class="manhuaerrcon"]/p', timeout=0).text == "漫画不存在或已被删除":
            return False
    except Exception:
        return True


# ID查找
def id_lookup(id, name):
    try:
        page.listen.start(f"{zaimanhua_url}/details/{id}")
        page.get(f'{zaimanhua_url}/details/{id}')

        if validate_manga():
            if (actual_name := page.ele('xpath://div[@class="comic_deCon"]/h1/a', timeout=1).text) == name:
                logger.info(f"ID查找成功: {name} \tID: {id}")
                return True
            else:
                logger.warning(f"与实际名称不符: {name} \t实际名称: {actual_name}\tID: {id}")
        logger.warning(f"ID查找失败: {name} \tID: {id}")
        return False
    except PageDisconnectedError as e:
        logger.error(f"浏览器已关闭: {e}")
        sys.exit()
    except Exception as e:
        logger.warning(f"ID查找未找到漫画: {name} \tID: {id} \nException: {e}")
        return False


# 通过名称查找
def name_lookup(subscription_name, search_name):
    try:
        page.listen.start(f"{zaimanhua_url}/dynamic/{search_name}")
        page.get(f'{zaimanhua_url}/dynamic/{search_name}')
        page.ele(f'xpath://div[@class="tab-con autoHeight"]//a[@title="{subscription_name}"]/../../a',
                 timeout=1).click()
        if validate_manga():
            logger.info(f"名称查找成功: {subscription_name} \t关键词: {search_name}")
            return True
        else:
            been_removed.append(subscription_name)
            logger.error(f"漫画不存在或已被删除: {subscription_name}")
            get_finding_failed()
            return False

    except PageDisconnectedError as e:
        logger.error(f"浏览器已关闭: {e}")
        sys.exit()
    except Exception as e:
        logger.warning(f"未找到切换为关键词: {subscription_name} \t关键词: {search_name}")
        len_name = len(search_name)
        if len_name > 2:
            return name_lookup(subscription_name, search_name[0:int(len_name / 2)])
        else:
            not_found.append(subscription_name)
            logger.error(f"名称查找未找到漫画: {subscription_name}")
            get_finding_failed()
            return False


# 订阅漫画
def subscription(name):
    # 订阅漫画
    try:
        if page.ele(f'xpath://a[@id="subscribe_id_mh"]').text == "取消订阅":
            logger.info(f"已经订阅: {name}\n")
        else:
            page.ele(f'xpath://a[text()="订阅收藏"]').click()
            logger.info(f"订阅成功:{name}\n")
    except PageDisconnectedError as e:
        logger.error(f"浏览器已关闭: {e}")
        sys.exit()
    except Exception as e:
        not_found.append("subscription_name")
        logger.error(f"订阅失败: {name}\n Exception: {e}\n")


def main():
    try:
        with open('all_subscriptions.json', 'r', encoding='utf-8') as file:
            all_subscriptions = json.load(file)
            # 循环订阅漫画
            for subscriptions in all_subscriptions:
                if id_lookup(subscriptions["id"], subscriptions["name"]) or name_lookup(subscriptions["name"],
                                                                                        subscriptions["name"]):
                    subscription(subscriptions["name"])
        get_finding_failed()
    except FileNotFoundError as e:
        logger.error(f"all_subscriptions.json文件未找到: {e}")
    except Exception as e:
        logger.error(f"all_subscriptions.json文件读取错误: {e}")


if __name__ == "__main__":
    main()
