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
    


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    context = browser.new_context()
    page = context.new_page()
    page.on("dialog", handle_dialog)

    page.goto("https://www.xiaohongshu.com/user/profile/5a62fe0e4eacab39de541f86")
    # page.screenshot(path="example.png")

    err = load_cookies_from_file(context, 'cookies.json')
    if err == True:
        print("load and set cookies success.")
        page.reload()
    else:
        # login
        page.get_by_role("button", name="登录").click()
        page.wait_for_load_state()

        ## to find the login qrcode image and wait manualy scan
        # 定位图片元素（根据提供的HTML）
        # img_element = page.get_by_role("img", name="登录").click()
        img_element = page.locator('img.qrcode-img')
        
        # 获取Base64数据
        src = img_element.get_attribute('src')
        
        # 提取Base64编码部分（去掉data:image/png;base64,前缀）
        base64_data = src.split(',')[1]
        
        # 解码Base64数据
        image_data = base64.b64decode(base64_data)
        
        # 保存图片到文件
        output_path = 'downloaded_qrcode.png'
        with open(output_path, 'wb') as f:
            f.write(image_data)
        
        print(f"图片已成功保存到: {os.path.abspath(output_path)}")


        time.sleep(30)

        cookies = context.cookies()
        print(cookies)

        # save cookies
        filename = 'cookies.json'
        with open(filename, 'w') as f:
            json.dump(cookies, f, indent=2)
        
        print(f"Cookies已保存到 {filename}")
        

    # fetch all user's notes
    note_items = page.locator('section.note-item').all()
    print("get note_items count:", len(note_items))

    note_urls = []
    for note_one in note_items:
        # find links
        # first_href = note_one.locator('a[href="/explore/"]').get_attribute('href')
        # print("第一个链接的href:", first_href)
        
        # second_href = note_one.locator('a.cover.mask.ld').get_attribute('href')
        # print("第二个链接的href:", second_href)

        note_id = ""
        query_params = ""
        
        note_links = note_one.locator('a').all()
        for link_one in note_links:

            href = link_one.get_attribute('href')
            link_class = link_one.get_attribute('class')
            print("get href:", href)
            print("get class:", link_class)

            if href == None:
                continue

            if href.startswith('/explore/'):
                # parse note id
                note_id = os.path.basename(href)

            if href.startswith('/user/profile/') and link_class == 'cover mask ld':
                # parse note id
                query_params = href.split('?', 1)[1]

        if note_id != "" and query_params != "":
            note_urls.append(f"https://www.xiaohongshu.com/explore/{note_id}?{query_params}")

    print("note_urls:", note_urls)

    time.sleep(1000)
    browser.close()