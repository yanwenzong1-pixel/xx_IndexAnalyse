import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

def send_email_report(report, receiver_email="248550734@qq.com"):
    """发送邮件报告"""
    try:
        # 邮件配置
        smtp_server = "smtp.qq.com"
        smtp_port = 587
        sender_email = "your_email@qq.com"  # 需要替换为实际邮箱
        sender_password = "your_password"  # 需要替换为实际密码
        
        # 检查邮箱配置是否已修改
        if sender_email == "your_email@qq.com" or sender_password == "your_password":
            print("请先配置邮件发送参数")
            return False
        
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = f"微盘股指数监控报告 - {datetime.now().strftime('%Y-%m-%d')}"
        
        msg.attach(MIMEText(report, 'plain', 'utf-8'))
        
        # 发送邮件
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print("邮件发送成功")
        return True
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False
