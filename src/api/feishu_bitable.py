"""
飞书多维表格 API 封装
=====================
对接飞书开放平台多维表格接口，实现数据的增删改查。
文档参考: https://open.feishu.cn/document/server-docs/docs/bitable-v1/bitable-overview
"""

import requests
from datetime import datetime


class FeishuBitableClient:
    """飞书多维表格客户端"""

    def __init__(self, app_id, app_secret, app_token):
        self.app_id = app_id
        self.app_secret = app_secret
        self.app_token = app_token
        self.base_url = "https://open.feishu.cn/open-apis"
        self.access_token = None
        self.token_expire = 0

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
            self.token_expire = datetime.now().timestamp() + data["expire"] - 300
            return self.access_token
        else:
            raise Exception(f"获取token失败: {data}")

    def _get_headers(self):
        """获取请求头（自动刷新token）"""
        if not self.access_token or datetime.now().timestamp() > self.token_expire:
            self._get_tenant_access_token()
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def list_records(self, table_id, page_size=100, filter_condition=None):
        """
        查询多维表格记录
        文档: https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/list
        """
        url = f"{self.base_url}/bitable/v1/apps/{self.app_token}/tables/{table_id}/records"
        params = {"page_size": page_size}
        if filter_condition:
            params["filter"] = filter_condition

        all_records = []
        has_more = True
        page_token = None

        while has_more:
            if page_token:
                params["page_token"] = page_token
            resp = requests.get(url, headers=self._get_headers(), params=params)
            data = resp.json()
            if data.get("code") != 0:
                raise Exception(f"查询记录失败: {data}")

            all_records.extend(data["data"]["items"])
            has_more = data["data"]["has_more"]
            page_token = data["data"].get("page_token")

        return all_records

    def create_record(self, table_id, fields):
        """
        新增一条记录
        文档: https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/create
        """
        url = f"{self.base_url}/bitable/v1/apps/{self.app_token}/tables/{table_id}/records"
        payload = {"fields": fields}
        resp = requests.post(url, headers=self._get_headers(), json=payload)
        data = resp.json()
        if data.get("code") == 0:
            return data["data"]["record"]
        else:
            raise Exception(f"创建记录失败: {data}")

    def batch_create_records(self, table_id, records):
        """批量创建记录"""
        url = f"{self.base_url}/bitable/v1/apps/{self.app_token}/tables/{table_id}/records/batch_create"
        payload = {"records": [{"fields": r} for r in records]}
        resp = requests.post(url, headers=self._get_headers(), json=payload)
        data = resp.json()
        if data.get("code") == 0:
            return data["data"]["records"]
        else:
            raise Exception(f"批量创建失败: {data}")

    def update_record(self, table_id, record_id, fields):
        """更新记录"""
        url = f"{self.base_url}/bitable/v1/apps/{self.app_token}/tables/{table_id}/records/{record_id}"
        payload = {"fields": fields}
        resp = requests.put(url, headers=self._get_headers(), json=payload)
        data = resp.json()
        if data.get("code") == 0:
            return data["data"]["record"]
        else:
            raise Exception(f"更新记录失败: {data}")

    def delete_record(self, table_id, record_id):
        """删除记录"""
        url = f"{self.base_url}/bitable/v1/apps/{self.app_token}/tables/{table_id}/records/{record_id}"
        resp = requests.delete(url, headers=self._get_headers())
        data = resp.json()
        return data.get("code") == 0

    def create_field(self, table_id, field_name, field_type, property=None):
        """
        创建字段（列）
        文档: https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-field/create
        """
        url = f"{self.base_url}/bitable/v1/apps/{self.app_token}/tables/{table_id}/fields"
        payload = {
            "field_name": field_name,
            "type": field_type
        }
        if property:
            payload["property"] = property
        resp = requests.post(url, headers=self._get_headers(), json=payload)
        data = resp.json()
        if data.get("code") == 0:
            return data["data"]["field"]
        else:
            raise Exception(f"创建字段失败: {data}")
