from __future__ import annotations

import peewee

from constants import RoleTemplateType
from util import i18nUtil
from .base import DbModelBase, EnumField, JsonField


class GtRoleTemplate(DbModelBase):
    name: str = peewee.CharField(unique=True)
    model: str | None = peewee.CharField(null=True)
    soul: str = peewee.TextField(default="")
    type: RoleTemplateType = EnumField(RoleTemplateType, default=RoleTemplateType.SYSTEM)
    i18n: dict = JsonField(default=dict)  # 多语言数据，含 display_name

    @property
    def display_name(self) -> str:
        """返回角色模板显示名（从 i18n.display_name 解析，缺省回退到 name）。"""
        return i18nUtil.extract_i18n_str(
            self.i18n.get("display_name") if self.i18n else None,
            default=self.name,
        ) or self.name

    def to_json(self) -> dict:
        """转换为 JSON 可序列化的字典，并补充 display_name。"""
        result = super().to_json()
        result["type"] = self.type.name
        result["display_name"] = self.display_name
        return result

    class Meta:
        table_name = "role_templates"


__all__ = ["GtRoleTemplate"]
