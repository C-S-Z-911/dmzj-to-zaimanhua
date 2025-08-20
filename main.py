import json
import logging
import sys
import time

from DrissionPage import ChromiumPage, ChromiumOptions

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

# 配置options
try:
    options = ChromiumOptions()
    options.set_browser_path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
    page = ChromiumPage(addr_or_opts=options)
except FileNotFoundError as e:
    logger.error(f"未找到浏览器: {e}")
    sys.exit()
except Exception as e:
    logger.error(f"错误: {e}")
    sys.exit()

not_found = []
has_been_removed = []


# 订阅漫画
def subscription(subscription_name, search_name):
    # 查找漫画
    try:
        page.listen.start(f"https://manhua.zaimanhua.com/dynamic/{search_name}")
        page.get(f'https://manhua.zaimanhua.com/dynamic/{search_name}')
        page.ele(f'xpath://div[@class="tab-con autoHeight"]//a[@title="{subscription_name}"]/../../a',
                 timeout=1).click()
    except Exception as e:
        logger.warning(f"未搜索到漫画-关键词: {search_name}")
        len_name = len(search_name)
        if len_name > 2:
            subscription(subscription_name, search_name[0:int(len_name / 2)])
        else:
            not_found.append(subscription_name)
            logger.info("不存在或已被删除: " + str(has_been_removed))
            logger.info("未找到: " + str(not_found))
            logger.error(f"未找到漫画: {subscription_name}\n Exception: {e}")
        return

    # 订阅漫画
    try:
        page.wait.load_start()
        # 延时2秒 等待页面加载
        time.sleep(2)
        if page.ele(f'xpath://a[@id="subscribe_id_mh"]').text == "取消订阅":
            logger.warning(f"已经订阅: {subscription_name}")
        else:
            page.ele(f'xpath://a[text()="订阅收藏"]').click()
            try:
                if page.ele(f'xpath://div[@class="manhuaerrcon"]/p', timeout=0).text == "漫画不存在或已被删除":
                    has_been_removed.append(subscription_name)
                    print("不存在或已被删除: " + str(has_been_removed))
                    print("未找到: " + str(not_found))
                    logger.error(f"漫画不存在或已被删除: {subscription_name}")
                else:
                    logger.info(f"订阅成功:{subscription_name}")
            except Exception as e:
                logger.info(f"订阅成功:{subscription_name}")
    except Exception as e:
        not_found.append("subscription_name")
        logger.info("不存在或已被删除: " + str(has_been_removed))
        logger.info("未找到: " + str(not_found))
        logger.error(f"订阅失败: {subscription_name}\n Exception: {e}")


def main():
    # subscription("我的妻子有点可怕", "我的妻子有点可怕")

    with open('output/all_subscriptions.json', 'r', encoding='utf-8') as file:
        all_subscriptions = json.load(file)

        # 循环订阅漫画
        for subscriptions in all_subscriptions:
            subscription(subscriptions["name"], subscriptions["name"])
    logger.info("不存在或已被删除: " + str(has_been_removed))
    logger.info("未找到: " + str(not_found))


if __name__ == "__main__":
    main()