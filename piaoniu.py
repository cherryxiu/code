import requests
from requests.exceptions import RequestException
from email.message import EmailMessage
import chardet
import smtplib
import time
import xml.etree.ElementTree as ET
from datetime import datetime

def get_canon_page():
    url = "https://www.piaoniu.com/api/v1/ticketCategories.json?b2c=true&eventId=14946565"

    # 设置请求头，模拟浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    try:
        # 发送GET请求
        response = requests.get(url, headers=headers, timeout=10)

        # 检查请求是否成功
        response.raise_for_status()

        # 检测编码并解码内容
        encoding = chardet.detect(response.content)['encoding']
        if encoding:
            response.encoding = encoding
        else:
            response.encoding = 'utf-8'  # 默认使用utf-8

        # 获取网页内容
        content = response.text

        print("请求成功！" + response.encoding)

        # print(f"状态码: {response.status_code}")
        # print(f"编码: {response.encoding}")
        # print(f"内容长度: {len(content)} 字符")
        # print("\n" + "=" * 50 + "\n")

        # 打印前500个字符作为预览
        #print("页面内容预览:")
        # print(content[:500] + "..." if len(content) > 500 else content)
        # 解析XML
        root = ET.fromstring(content)
        print(root)

        # 提取所有item
        return root

    except RequestException as e:
        print(f"请求失败: {e}")
        return None


def save_content(content, filename="canon_page.html"):
    print(f"\n内容已保存到: {content}")
    """保存内容到文件"""
    if content:
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\n内容已保存到: {filename}")
        except Exception as e:
            print(f"保存文件失败: {e}")


def send_email_simple(subject, content, to_email):
    """
    发送简单文本邮件
    """
    print(f"准备发送邮件")
    # 邮箱配置 17820739046 NNsvTGFejhTNmBTr  Liuxiu6718311
    smtp_server = "smtp.163.com"  # 以163邮箱为例
    smtp_port = 25
    from_email = "13476977730@163.com"
    password = "Liuxiu6718311"  # 或授权码

    try:
        # 创建邮件对象
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        msg.set_content(content)

        # 连接服务器并发送
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # 启用加密
            server.login(from_email, password)
            server.send_message(msg)

        print("邮件发送成功！")
        return True

    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False


def simple_monitor(to_email):
    """简单定时监控"""
    print("🚀 开始监控票牛软件票价...")
    print("按 Ctrl+C 停止监控\n")

    check_count = 0

    while True:
        try:
            check_count += 1
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(current_time + " 第" + str(check_count) + "次请求")

            # 获取页面内容
            page_content = get_canon_page()

            # 保存到文件
            # if page_content:
            #     save_content(page_content)

            for item in page_content.findall('item'):
                origin_price = item.find('originPrice').text
                low_price = item.find('lowPrice').text
                if origin_price == '220.00' and low_price is not None and float(low_price) <= 270:
                    send_email_simple(
                        "周五票牛监控提醒123",
                        f"票牛220票价降低！{low_price}元",
                        to_email)
                    print(f"220票面的低价是: {low_price}元")



            # 等待5分钟（300秒）
            print("等待300s后再次检查...\n")
            time.sleep(300)

        except KeyboardInterrupt:
            print("\n\n⏹️ 监控已停止")
            break
        except Exception as e:
            print(f"60s❌ 发生错误: {e}")
            time.sleep(60)  # 出错也等待5分钟

if __name__ == "__main__":
    # 多个邮箱， 逗号分割
    simple_monitor("13476977730@163.com")
