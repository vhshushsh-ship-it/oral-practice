"""邮件发送服务 — 通过 QQ SMTP 发送验证码邮件"""

import smtplib
import ssl
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, MAIL_FROM


_LAST_SEND: dict[str, float] = {}  # 简单的内存冷却：{email: last_send_timestamp}


def check_cooldown(email: str, cooldown_seconds: int) -> int | None:
    """检查是否在冷却期内，返回剩余冷却秒数；不在冷却期返回 None"""
    now = time.time()
    last = _LAST_SEND.get(email)
    if last and (now - last) < cooldown_seconds:
        return int(cooldown_seconds - (now - last))
    return None


def record_send(email: str) -> None:
    """记录发送时间"""
    _LAST_SEND[email] = time.time()


def send_verification_code_email(email: str, code: str, purpose: str) -> None:
    """发送验证码邮件（同步，请在 run_in_executor 中调用）"""
    if not SMTP_USER or not SMTP_PASSWORD:
        raise RuntimeError("SMTP 邮件服务未配置（缺少 SMTP_USER 或 SMTP_PASSWORD）")

    purpose_label = "注册" if purpose == "register" else "登录"

    # ---- 构造 HTML 邮件 ----
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>SceneTalk 验证码</title>
</head>
<body style="margin:0;padding:0;background-color:#fdf8f0;font-family:Georgia,'Times New Roman',serif;">
  <table width="100%%" cellpadding="0" cellspacing="0" style="background-color:#fdf8f0;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="480" cellpadding="0" cellspacing="0" style="background-color:#fffbf5;border:1px solid #e0d5c0;border-radius:12px;box-shadow:0 2px 16px rgba(120,80,40,0.08);overflow:hidden;">
          <!-- Header -->
          <tr>
            <td style="padding:32px 40px 0 40px;text-align:center;">
              <h1 style="margin:0;font-family:Georgia,'Times New Roman',serif;font-size:28px;color:#5c3d2e;letter-spacing:0.02em;">
                SceneTalk
              </h1>
              <p style="margin:8px 0 0 0;font-size:14px;color:#a08060;">
                AI 英语口语练习平台
              </p>
            </td>
          </tr>
          <!-- Divider -->
          <tr>
            <td style="padding:20px 40px;">
              <hr style="border:none;border-top:1px solid #e0d5c0;margin:0;">
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding:8px 40px 32px 40px;">
              <p style="margin:0 0 8px 0;font-size:15px;color:#6b5a4a;">
                您正在{purpose_label} SceneTalk 账号
              </p>
              <p style="margin:0 0 24px 0;font-size:13px;color:#a08060;">
                请输入以下 6 位数字验证码完成{purpose_label}（有效期 5 分钟）：
              </p>
              <!-- Code box -->
              <table width="100%%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
                <tr>
                  <td style="background-color:#faf3e6;border:2px dashed #d4b896;border-radius:8px;padding:18px 20px;text-align:center;">
                    <span style="font-family:'Courier New',monospace;font-size:36px;font-weight:bold;letter-spacing:10px;color:#5c3d2e;">
                      {code}
                    </span>
                  </td>
                </tr>
              </table>
              <p style="margin:0 0 4px 0;font-size:12px;color:#c0a880;">
                此验证码 5 分钟内有效，请勿透露给他人
              </p>
              <p style="margin:0;font-size:12px;color:#c0a880;">
                如果不是您本人操作，请忽略此邮件
              </p>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="background-color:#faf5ec;padding:16px 40px;text-align:center;">
              <p style="margin:0;font-size:11px;color:#c0a880;">
                SceneTalk · 系统自动发送，请勿回复
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"SceneTalk {purpose_label}验证码：{code}"
    msg["From"] = MAIL_FROM or SMTP_USER
    msg["To"] = email
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    # ---- 连接 QQ SMTP 并发送 ----
    try:
        # 创建 SSL 上下文（QQ 邮箱要求加密连接）
        ssl_context = ssl.create_default_context()
        # 兼容较旧的 TLS 版本（QQ 邮箱可能需要）
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2

        if SMTP_PORT == 465:
            # SSL 直连
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=15, context=ssl_context)
        else:
            # STARTTLS
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15)
            server.starttls(context=ssl_context)

        # 开启调试日志以便排查问题
        server.set_debuglevel(False)

        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(MAIL_FROM or SMTP_USER, [email], msg.as_string())
        server.quit()
    except smtplib.SMTPAuthenticationError as e:
        raise RuntimeError(
            f"SMTP 认证失败（{e}），请检查：\n"
            "1. QQ 邮箱地址是否正确（当前 SMTP_USER={SMTP_USER}）\n"
            "2. 授权码是否正确\n"
            "获取方式：QQ邮箱 → 设置 → 账户 → 开启 POP3/SMTP 服务 → 获取授权码"
        )
    except (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected) as e:
        raise RuntimeError(
            f"无法连接到 SMTP 服务器 {SMTP_HOST}:{SMTP_PORT}（{type(e).__name__}: {e}）\n"
            "可能原因：\n"
            f"1. SMTP_USER 邮箱地址无效（当前值：{SMTP_USER}）\n"
            "2. 服务器网络不通，请检查防火墙/代理设置\n"
            "3. 授权码已过期，请在 QQ 邮箱重新获取"
        )
    except Exception as e:
        raise RuntimeError(f"邮件发送失败: {type(e).__name__}: {e}")
