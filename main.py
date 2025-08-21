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
import json
import sys


# 配置读取和浏览器初始化分离，提高可读性
def load_config():
    """加载配置文件并返回配置字典"""
    try:
        with open('config.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error("config.json文件未找到，请确保配置文件存在")
        sys.exit(1)
    except json.JSONDecodeError:
        logger.error("config.json格式错误，请检查JSON格式")
        sys.exit(1)
    except Exception as e:
        logger.error(f"读取配置文件时发生未知错误: {e}")
        sys.exit(1)


def setup_browser(browser_path):
    """设置浏览器选项并返回页面对象"""
    try:
        options = ChromiumOptions()
        options.set_browser_path(browser_path)
        return ChromiumPage(addr_or_opts=options)
    except FileNotFoundError:
        logger.error(f"未找到浏览器路径: {browser_path}，请检查路径是否正确")
        sys.exit(1)
    except Exception as e:
        logger.error(f"浏览器初始化失败: {e}")
        sys.exit(1)

# 主流程
try:
    # 加载配置
    config = load_config()
    browser_path = config["browser_path"]
    wait_load = config["wait_load"]
    zaimanhua_url = config["zaimanhua_url"]

    # 初始化浏览器
    page = setup_browser(browser_path)

except KeyError as e:
    logger.error(f"配置文件中缺少必要字段: {e}")
    sys.exit(1)
except SystemExit:
    # 已经处理过的错误，直接退出
    pass
except Exception as e:
    logger.error(f"程序初始化失败: {e}")
    sys.exit(1)

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
