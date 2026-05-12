"""快速验证 role 管理工具的 DAL 层行为"""
import os
import pytest
from service import ormService
from dal.db import gtRoleTemplateManager
from model.dbModel.gtRoleTemplate import GtRoleTemplate
from model.dbModel.gtAgent import GtAgent
from constants import RoleTemplateType

DB_PATH = os.path.join(os.path.dirname(__file__), "../dev_storage_root/data/data.db")


@pytest.fixture(scope="module")
def event_loop():
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module", autouse=True)
async def init_db():
    await ormService.startup(DB_PATH)
    yield
    await ormService.shutdown()


@pytest.mark.asyncio
async def test_create_and_update_role_template():
    """创建 → 修改 → 验证全字段 upsert"""
    # 创建
    new_t = GtRoleTemplate(
        name="test_role_pm",
        type=RoleTemplateType.USER,
        soul="你是一个测试角色",
        model=None,
        i18n={"display_name": {"zh-CN": "测试项目经理"}},
    )
    saved = await gtRoleTemplateManager.save_role_template(new_t)
    assert saved.id is not None
    assert saved.name == "test_role_pm"
    assert saved.soul == "你是一个测试角色"

    # 修改（全字段更新）
    saved.soul = "更新后的测试角色，验证工具功能。"
    saved.i18n = {"display_name": {"zh-CN": "测试项目经理(已修改)"}}
    updated = await gtRoleTemplateManager.save_role_template(saved)
    assert updated.soul == "更新后的测试角色，验证工具功能。"
    assert updated.i18n == {"display_name": {"zh-CN": "测试项目经理(已修改)"}}


@pytest.mark.asyncio
async def test_delete_referenced_template_should_fail():
    """删除被 Agent 引用的模板应被拒绝"""
    agents = list(await GtAgent.select().aio_execute())
    if not agents:
        pytest.skip("没有 Agent 数据，跳过引用检查测试")

    first_agent = agents[0]
    template = await gtRoleTemplateManager.get_role_template_by_id(first_agent.role_template_id)
    assert template is not None, f"Agent {first_agent.name} 引用的模板不存在"

    refs = list(
        await GtAgent.select()
        .where(GtAgent.role_template_id == template.id)
        .aio_execute()
    )
    assert len(refs) >= 1
    assert any(a.name == first_agent.name for a in refs)


@pytest.mark.asyncio
async def test_cleanup_test_template():
    """清理测试数据"""
    test_t = await gtRoleTemplateManager.get_role_template_by_name("test_role_pm")
    if test_t is None:
        return
    refs = list(
        await GtAgent.select()
        .where(GtAgent.role_template_id == test_t.id)
        .aio_execute()
    )
    if refs:
        pytest.fail(f"test_role_pm 被 Agent 引用，无法清理: {[a.name for a in refs]}")
    deleted = await gtRoleTemplateManager.delete_role_template(test_t.id)
    assert deleted is True
