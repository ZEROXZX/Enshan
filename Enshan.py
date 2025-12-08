import requests
import json
import os
import sys
import re
import time

# 禁用 urllib3 警告
requests.packages.urllib3.disable_warnings()

# 获取环境变量
cookie = os.environ.get("cookie_enshan")

def send_message(content):
    """
    WxPusher 推送函数
    """
    api_url = 'https://sctapi.ftqq.com/SCT152534TSZyMr41S3EiZ2a3ipdzFiAGI.send'
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        "title": "恩山论坛签到",
        "content": content
    }
    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(data))
        return response.json()
    except Exception as e:
        print(f"推送失败: {e}")
        return {"code": 0, "msg": str(e)}

def get_formhash(session):
    """
    从页面获取 formhash (防跨站攻击 token)，这是新脚本的关键步骤
    """
    try:
        url = "https://www.right.com.cn/forum/forum.php"
        response = session.get(url, timeout=15)
        response.raise_for_status()
        html = response.text
        
        # 使用正则提取 formhash
        m = re.search(r'name=["\']formhash["\']\s+value=["\']([0-9a-fA-F]+)["\']', html)
        if not m:
            m = re.search(r"formhash\s*[:=]\s*['\"]([0-9a-fA-F]+)['\"]", html)
        if not m:
            m = re.search(r'name=["\']formhash["\']\s+value=["\']([^"\']+)["\']', html)
            
        if m:
            return m.group(1)
        else:
            return None
    except Exception as e:
        print(f"获取formhash异常: {e}")
        return None

def get_user_info(session):
    """
    获取积分和恩山币信息
    """
    msg = ""
    try:
        url = "https://www.right.com.cn/FORUM/home.php?mod=spacecp&ac=credit&showcredit=1"
        response = session.get(url, timeout=15)
        html = response.text
        
        # 使用正则提取积分信息
        coin_match = re.findall("恩山币: </em>(.*?)&nbsp;", html)
        point_match = re.findall("<em>积分: </em>(.*?)<span", html)
        
        if coin_match:
            msg += f" | 恩山币: {coin_match[0]}"
        if point_match:
            msg += f" | 积分: {point_match[0]}"
            
    except Exception as e:
        msg += f" | 获取积分失败: {str(e)}"
    return msg

def run(current_cookie):
    msg = ""
    session = requests.Session()
    
    # 使用新脚本的 Headers，模拟更真实
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": "https://www.right.com.cn/forum/",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": current_cookie,
    })

    try:
        # 1. 获取 formhash
        formhash = get_formhash(session)
        if not formhash:
            return "失败：Cookie可能失效，无法获取formhash"

        # 2. 执行签到 (POST请求)
        sign_url = "https://www.right.com.cn/forum/plugin.php?id=erling_qd:action&action=sign"
        payload = {"formhash": formhash}
        
        response = session.post(sign_url, data=payload, timeout=15)
        
        # 解析返回的 JSON
        try:
            data = response.json()
            if data.get("success"):
                days = data.get("continuous_days", "?")
                raw_msg = data.get("message", "签到成功")
                msg += f"签到结果: {raw_msg} (已连签{days}天)"
            else:
                # 即使 success 为 false，可能是今日已签到
                raw_msg = data.get("message", "签到失败")
                msg += f"签到反馈: {raw_msg}"
        except json.JSONDecodeError:
             msg += f"签到异常: 返回非JSON数据 (Code: {response.status_code})"

        # 3. 获取用户信息
        msg += get_user_info(session)

    except Exception as e:
        msg = f'脚本执行出错: {str(e)}'
        
    return msg

def main():
    global cookie
    msg_all = ""
    
    if not cookie:
        print("未找到 cookie_enshan 环境变量")
        return

    # 处理多账号
    if "\\n" in cookie:
        clist = cookie.split("\\n")
    else:
        clist = cookie.split("\n")
        
    i = 0
    while i < len(clist):
        account_msg = f"账号 {i+1}: "
        current_cookie = clist[i].strip()
        if current_cookie:
            log_str = run(current_cookie)
            account_msg += log_str
            print(account_msg)
            msg_all += account_msg + "\n"
        i += 1
        
        # 账号间稍微暂停，避免请求过快
        if i < len(clist):
            time.sleep(2)

    # 推送消息
    push_log = send_message(msg_all[:-1])
    print(f"推送结果: {push_log}")

if __name__ == "__main__":
    print("----------恩山论坛签到开始----------")
    main()
    print("----------恩山论坛签到结束----------")
