"""
飞书 aily 智能体 API 封装
=========================
对接飞书aily智能体，实现AI对话、知识问答和智能推荐。
文档参考: https://aily.feishu.cn/doc/zau10hcu/r50v5c7d
         https://open.larkoffice.com/document/aily-v1/aily_session-aily_message/create
"""

import requests
import json


class FeishuAilyClient:
    """飞书aily智能体客户端"""

    def __init__(self, app_id, app_secret, aily_app_id):
        self.app_id = app_id
        self.app_secret = app_secret
        self.aily_app_id = aily_app_id
        self.base_url = "https://open.feishu.cn/open-apis"
        self.access_token = None

    def _get_tenant_access_token(self):
        """获取租户访问令牌"""
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        resp = requests.post(url, json=payload)
        data = resp.json()
        if data.get("code") == 0:
            self.access_token = data["tenant_access_token"]
            return self.access_token
        else:
            raise Exception(f"获取token失败: {data}")

    def _get_headers(self):
        if not self.access_token:
            self._get_tenant_access_token()
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def create_session(self, user_id=None):
        """
        创建aily会话
        文档: https://open.larkoffice.com/document/aily-v1/aily_session/create
        """
        url = f"{self.base_url}/aily/v1/sessions"
        payload = {
            "aily_app_id": self.aily_app_id,
        }
        if user_id:
            payload["user_id"] = user_id

        resp = requests.post(url, headers=self._get_headers(), json=payload)
        data = resp.json()
        if data.get("code") == 0:
            return data["data"]["aily_session_id"]
        else:
            raise Exception(f"创建会话失败: {data}")

    def send_message(self, session_id, content, content_type="text"):
        """
        发送消息给aily智能体
        文档: https://open.larkoffice.com/document/aily-v1/aily_session-aily_message/create
        """
        url = f"{self.base_url}/aily/v1/sessions/{session_id}/messages"
        payload = {
            "content": content,
            "content_type": content_type
        }
        resp = requests.post(url, headers=self._get_headers(), json=payload)
        data = resp.json()
        if data.get("code") == 0:
            return data["data"]
        else:
            raise Exception(f"发送消息失败: {data}")

    def list_messages(self, session_id):
        """获取会话消息列表"""
        url = f"{self.base_url}/aily/v1/sessions/{session_id}/messages"
        resp = requests.get(url, headers=self._get_headers())
        data = resp.json()
        if data.get("code") == 0:
            return data["data"]["items"]
        else:
            raise Exception(f"获取消息失败: {data}")

    def chat(self, message, session_id=None, user_id=None):
        """
        便捷对话方法：创建会话（如需要）+ 发送消息 + 返回回复
        """
        if not session_id:
            session_id = self.create_session(user_id)

        self.send_message(session_id, message)
        messages = self.list_messages(session_id)

        # 获取最后一条aily回复
        for msg in reversed(messages):
            if msg.get("sender_type") == "aily":
                return {
                    "session_id": session_id,
                    "reply": msg.get("content", ""),
                    "raw": msg
                }

        return {"session_id": session_id, "reply": "", "raw": messages}
