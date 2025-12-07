import requests
import json
import os
import sys
import re
import urllib3

# 禁用 SSL 警告，防止 verify=False 时报错
urllib3.disable_warnings()

sys.path.append('.')

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

def run(current_cookie):
    """
    执行签到/查询逻辑
    """
    msg = ""
    # 模拟浏览器 User-Agent，使用新脚本中的配置
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.125 Safari/537.36",
        "Cookie": current_cookie,
    }
    
    # 恩山积分页面
    url = "https://www.right.com.cn/FORUM/home.php?mod=spacecp&ac=credit&showcredit=1"

    try:
        # verify=False 避免 SSL 证书报错，timeout 防止卡死
        response = requests.get(url, headers=headers, verify=False, timeout=120)
        response.encoding = 'utf-8' # 确保编码正确
        
        # 使用正则提取积分信息 (核心修改部分)
        if "恩山币" in response.text:
            try:
                # 尝试提取恩山币
                coin_match = re.findall(r"恩山币: </em>(.*?)&nbsp;", response.text)
                coin = coin_match[0] if coin_match else "未知"
                
                # 尝试提取积分
                point_match = re.findall(r"<em>积分: </em>(.*?)<span", response.text)
                point = point_match[0] if point_match else "未知"
                
                msg += f"【签到成功】\n恩山币: {coin}\n积分: {point}"
            except Exception as e:
                msg += f"【签到异常】页面访问成功但解析数值失败: {str(e)}"
        elif "登录" in response.text and "注册" in response.text:
             msg += "【签到失败】Cookie已失效，请重新获取"
        else:
             msg += "【签到失败】未能匹配到相关信息，可能是网站改版"
             
    except requests.exceptions.RequestException as e:
        msg = f"【网络错误】连接网站失败: {str(e)}"
    except Exception as e:
        msg = f"【脚本错误】发生未知错误: {str(e)}"
        
    return msg + '\n'

def main():
    """
    主程序
    """
    global cookie
    msg = "【恩山论坛签到任务】\n"
    
    if not cookie:
        print("未检测到 cookie_enshan 环境变量")
        return

    # 处理多账号，支持换行符或\n字符串分割
    if "\\n" in cookie:
        clist = cookie.split("\\n")
    else:
        clist = cookie.split("\n")
        
    i = 0
    while i < len(clist):
        account_cookie = clist[i].strip()
        if account_cookie: # 跳过空行
            msg += f"--- 第 {i+1} 个账号 ---\n"
            msg += run(account_cookie)
        i += 1
        
    print(msg)
    
    # 推送消息
    log = send_message(msg)
    print("推送结果:", log)

if __name__ == "__main__":
    print("----------恩山论坛开始尝试签到----------")
    if cookie:
        main()
    else:
        print("请在环境变量中设置 cookie_enshan")
    print("----------恩山论坛签到执行完毕----------")
