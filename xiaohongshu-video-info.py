from playwright.sync_api import sync_playwright
import time
import base64
import os
import json


def handle_dialog(dialog):
    print(dialog.message)
    dialog.dismiss()


def load_cookies_from_file(context, filename="cookies.json"):
    """
    从JSON文件加载cookies并设置到浏览器context
    
    :param context: Playwright的BrowserContext对象
    :param filename: 存储cookies的JSON文件路径
    """
    try:
        with open(filename, 'r') as f:
            cookies = json.load(f)
        
        # 清除现有cookies(可选)
        # context.clear_cookies()
        
        # 添加cookies到context
        context.add_cookies(cookies)
        print(f"成功从 {filename} 加载 {len(cookies)} 个cookies")
        return True
    except FileNotFoundError:
        print(f"错误: cookies文件 {filename} 不存在")
        return False
    except json.JSONDecodeError:
        print(f"错误: cookies文件 {filename} 格式不正确")
        return False
    except Exception as e:
        print(f"加载cookies时发生错误: {str(e)}")
        return False
    


# 拦截并阻止非必要资源
def intercept_route(route):
    # 阻止图片、CSS、字体等资源
    if route.request.resource_type in {"image", "stylesheet", "font", "video"}:
        route.abort()
    else:
        route.continue_()


with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=[
        "--disable-gpu",         # 禁用 GPU 加速（某些环境下可能提升稳定性）
        "--no-sandbox",          # 禁用沙盒（适用于 Docker/CI 环境）
        "--disable-dev-shm-usage",  # 避免共享内存不足问题
        "--disable-setuid-sandbox",
        "--disable-blink-features=AutomationControlled",  # 禁用自动化特征检测
        "--window-size=1920,1080"  # 设置窗口尺寸
    ])

    context = browser.new_context()
    page = context.new_page()

    # 设置视口尺寸（防止响应式布局问题）
    page.set_viewport_size({"width": 1920, "height": 1080})

    # 注入脚本：隐藏自动化特征
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
    """)

    # 自定义 User-Agent
    page.set_extra_http_headers({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    })


    # 在页面中启用拦截
    # page.route("**/*", intercept_route)

    page.goto("https://www.xiaohongshu.com/explore/68086502000000001c00ce09?xsec_token=ABpiQ88-GRmKwrFUXJgiWM9bjcqNmEbSrJ_8E9Jj8Bcvk=&xsec_source=pc_feed")

    # page.wait_for_selector(".username")

    # fetch video title
    title_element = page.locator('#detail-title')
    title = title_element.inner_text()
    print("title:", title)

    desc_element = page.locator('#detail-desc')
    desc = desc_element.inner_text()
    print("desc:", desc)

    username_element = page.locator('.username').all()
    if len(username_element) > 0:
        username = username_element[0].text_content()
        print("username:", username)


    # time.sleep(1000)
    browser.close()