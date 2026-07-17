/**
 * 东方雨虹门店巡检应用 - 妙搭后端服务
 * 
 * 功能：
 * 1. 获取门店列表（从飞书多维表格）
 * 2. 提交巡检记录（写入飞书多维表格）
 * 3. 查看巡检历史（读取飞书多维表格）
 * 4. 获取巡检模板（检查项标准）
 */

const express = require('express');
const axios = require('axios');
const path = require('path');

const app = express();
app.use(express.json({ limit: '10mb' }));
app.use(express.static(path.join(__dirname, 'public')));

// ===== 配置（从环境变量读取，妙搭部署时设置）=====
const CONFIG = {
  FEISHU_APP_ID: process.env.FEISHU_APP_ID || 'cli_aadc44eb88f89cc4',
  FEISHU_APP_SECRET: process.env.FEISHU_APP_SECRET || 'rknUZjLCegvpqAyzgL531f1CO712ejxw',
  BITABLE_APP_TOKEN: process.env.BITABLE_APP_TOKEN || 'R7v9bKHNdaBsDFsDdvzcXICOnWh',
  TABLE_STORE: process.env.TABLE_STORE || 'tblz4EvPXhpCVy6l',
  TABLE_INSPECTION: process.env.TABLE_INSPECTION || 'tbl6WQHXuVF6Qgk9',
  TABLE_REGION_STATS: process.env.TABLE_REGION_STATS || 'tblyoXE0QKYtfEAR',
  PORT: process.env.PORT || 3000
};

const FEISHU_BASE = 'https://open.feishu.cn/open-apis';
let accessToken = null;
let tokenExpire = 0;

// ===== 飞书API工具函数 =====

async function getToken() {
  if (accessToken && Date.now() < tokenExpire) return accessToken;
  
  const resp = await axios.post(`${FEISHU_BASE}/auth/v3/tenant_access_token/internal`, {
    app_id: CONFIG.FEISHU_APP_ID,
    app_secret: CONFIG.FEISHU_APP_SECRET
  });
  
  if (resp.data.code !== 0) throw new Error(`获取token失败: ${JSON.stringify(resp.data)}`);
  accessToken = resp.data.tenant_access_token;
  tokenExpire = Date.now() + (resp.data.expire - 300) * 1000;
  return accessToken;
}

async function bitableRequest(method, urlPath, data) {
  const token = await getToken();
  const resp = await axios({
    method,
    url: `${FEISHU_BASE}/bitable/v1/apps/${CONFIG.BITABLE_APP_TOKEN}${urlPath}`,
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    data
  });
  return resp.data;
}

// 提取Bitable字段值的通用函数
function val(fields, key, defaultVal = '') {
  const v = fields[key];
  if (v === undefined || v === null) return defaultVal;
  if (Array.isArray(v) && v.length > 0) {
    if (typeof v[0] === 'object' && v[0] !== null) {
      return v[0].text || v[0].name || defaultVal;
    }
    return v[0];
  }
  return v;
}

function toNum(fields, key, defaultVal = 0) {
  let v = fields[key];
  if (v === undefined || v === null) return defaultVal;
  if (Array.isArray(v) && v.length > 0) {
    v = typeof v[0] === 'object' ? (v[0].text || v[0]) : v[0];
  }
  if (typeof v === 'number') return v;
  const n = parseFloat(v);
  return isNaN(n) ? defaultVal : n;
}

// ===== 巡检检查项标准 =====
const INSPECTION_ITEMS = [
  { id: 'display', name: '产品陈列标准', maxScore: 20, checkPoints: [
    '防水材料按品类分区陈列', '畅销品放置在黄金视线区域', '陈列面整洁无积灰', '价签与产品对应准确'
  ]},
  { id: 'cleanliness', name: '门店卫生状况', maxScore: 15, checkPoints: [
    '地面清洁无污渍', '展架无灰尘', '样品无破损', '照明设备正常运作'
  ]},
  { id: 'pricing', name: '价签与促销物料', maxScore: 15, checkPoints: [
    '价签信息完整（品名、规格、价格）', '促销海报按公司规范张贴', '活动信息及时更新', '价签无缺失'
  ]},
  { id: 'inventory', name: '库存与样品展示', maxScore: 20, checkPoints: [
    '样品库存充足', '滞销品及时下架', '新品上架及时', '库存与系统数据一致'
  ]},
  { id: 'service', name: '服务规范', maxScore: 15, checkPoints: [
    '店员着统一工装', '接待话术规范', '客户咨询响应及时', '施工预约流程清晰'
  ]},
  { id: 'safety', name: '安全合规', maxScore: 15, checkPoints: [
    '消防通道畅通', '危险品按规定存放', '电气设备安全', '应急标识完好'
  ]}
];

// ===== 区域月度统计：提交后自动更新区域月度统计表 =====

async function updateRegionStats(region) {
  try {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const monthKey = `${year}-${month}`;

    // 1. 查询巡检记录表中该区域的所有记录
    const resp = await bitableRequest('get', `/tables/${CONFIG.TABLE_INSPECTION}/records?page_size=500`);
    if (resp.code !== 0) {
      console.error('区域统计-查询巡检记录失败:', resp.msg);
      return;
    }

    const allRegionRecords = (resp.data.items || []).filter(r => val(r.fields, '区域') === region);

    // 2. 筛选当月记录
    const monthStart = new Date(year, now.getMonth(), 1).getTime();
    const monthEnd = new Date(year, now.getMonth() + 1, 1).getTime();
    const monthRecords = allRegionRecords.filter(r => {
      const t = toNum(r.fields, '巡检时间');
      return t >= monthStart && t < monthEnd;
    });

    const monthTotal = monthRecords.length;
    const monthPassed = monthRecords.filter(r => toNum(r.fields, '总分') >= 80).length;
    const monthFailed = monthTotal - monthPassed;
    const monthPassRate = monthTotal > 0 ? monthPassed / monthTotal : 0;
    const monthAvgScore = monthTotal > 0
      ? monthRecords.reduce((sum, r) => sum + toNum(r.fields, '总分'), 0) / monthTotal
      : 0;

    // 3. 筛选当年记录，计算年度巡检总条数
    const yearStart = new Date(year, 0, 1).getTime();
    const yearRecords = allRegionRecords.filter(r => toNum(r.fields, '巡检时间') >= yearStart);
    const yearTotal = yearRecords.length;

    // 4. 查找区域月度统计表中该区域+该月的记录行
    const statsResp = await bitableRequest('get', `/tables/${CONFIG.TABLE_REGION_STATS}/records?page_size=500`);
    if (statsResp.code !== 0) {
      console.error('区域统计-查询统计表失败:', statsResp.msg);
      return;
    }

    let statRecord = (statsResp.data.items || []).find(r =>
      val(r.fields, '区域') === region && val(r.fields, '统计月份') === monthKey
    );

    // 5. 如果当月行不存在，则新建
    if (!statRecord) {
      const createResp = await bitableRequest('post', `/tables/${CONFIG.TABLE_REGION_STATS}/records`, {
        fields: { '区域': region, '统计月份': monthKey }
      });
      if (createResp.code === 0) {
        statRecord = createResp.data.record;
        console.log(`区域统计-新建「${region} ${monthKey}」记录行`);
      } else {
        console.error('区域统计-新建记录行失败:', createResp.msg);
        return;
      }
    }

    // 6. 更新该行
    const updateResp = await bitableRequest('patch', `/tables/${CONFIG.TABLE_REGION_STATS}/records/${statRecord.record_id}`, {
      fields: {
        '月度巡检条数': monthTotal,
        '月度合格条数': monthPassed,
        '月度不合格条数': monthFailed,
        '月度通过率': monthPassRate,
        '月度平均分': Math.round(monthAvgScore * 100) / 100,
        '年度巡检总条数': yearTotal,
        '更新时间': Date.now()
      }
    });

    if (updateResp.code === 0) {
      console.log(`区域统计-已更新「${region} ${monthKey}」: 月度条数=${monthTotal} 合格=${monthPassed} 通过率=${(monthPassRate * 100).toFixed(1)}% 平均分=${monthAvgScore.toFixed(1)} 年度总条数=${yearTotal}`);
    } else {
      console.error('区域统计-更新失败:', updateResp.msg);
    }
  } catch (e) {
    console.error('区域统计-异常:', e.message);
  }
}

// ===== API路由 =====

// 健康检查
app.get('/api/health', (req, res) => {
  res.json({ ok: true, service: 'yuhong-inspection', version: '1.0.0', time: new Date().toISOString() });
});

// 获取巡检模板
app.get('/api/template', (req, res) => {
  res.json({
    templateName: '东方雨虹门店巡检表',
    version: '2.0',
    totalMaxScore: 100,
    items: INSPECTION_ITEMS
  });
});

// 获取门店列表
app.get('/api/stores', async (req, res) => {
  try {
    const resp = await bitableRequest('get', `/tables/${CONFIG.TABLE_STORE}/records?page_size=500`);
    if (resp.code !== 0) {
      return res.status(500).json({ ok: false, error: resp.msg });
    }
    const stores = (resp.data.items || []).map(r => {
      const f = r.fields;
      return {
        storeId: val(f, '门店编号'),
        storeName: val(f, '门店名称'),
        region: val(f, '区域'),
        storeType: val(f, '门店类型'),
        address: val(f, '地址'),
        status: val(f, '经营状态')
      };
    });
    res.json({ ok: true, data: stores });
  } catch (e) {
    console.error('获取门店列表失败:', e.message);
    res.status(500).json({ ok: false, error: e.message });
  }
});

// 提交巡检记录
app.post('/api/submit', async (req, res) => {
  try {
    const { storeId, storeName, region, inspector, scores, notes, photos } = req.body;
    
    const totalScore = Object.values(scores).reduce((a, b) => a + b, 0);
    const passed = totalScore >= 80;
    const level = totalScore >= 90 ? '优秀' : totalScore >= 80 ? '合格' : '不合格';
    
    // 构建Bitable记录字段
    const fields = {
      '门店编号': storeId,
      '门店名称': storeName || storeId,
      '区域': region || '',
      '巡检人': inspector || '未知',
      '巡检时间': Date.now(),  // 毫秒时间戳
      '陈列标准得分': Number(scores.display || 0),
      '卫生状况得分': Number(scores.cleanliness || 0),
      '价签物料得分': Number(scores.pricing || 0),
      '库存样品得分': Number(scores.inventory || 0),
      '服务规范得分': Number(scores.service || 0),
      '安全合规得分': Number(scores.safety || 0),
      '备注': notes || ''
    };
    
    const resp = await bitableRequest('post', `/tables/${CONFIG.TABLE_INSPECTION}/records`, { fields });
    
    if (resp.code !== 0) {
      return res.status(500).json({ ok: false, error: resp.msg });
    }
    
    // 异步更新区域统计表（不阻塞响应）
    if (region) {
      updateRegionStats(region).catch(e => console.error('区域统计更新异常:', e.message));
    }
    
    res.json({
      ok: true,
      data: {
        recordId: resp.data.record.record_id,
        totalScore,
        level,
        passed,
        submittedAt: new Date().toISOString()
      }
    });
  } catch (e) {
    console.error('提交巡检失败:', e.message);
    res.status(500).json({ ok: false, error: e.message });
  }
});

// 获取巡检历史
app.get('/api/history', async (req, res) => {
  try {
    const { storeId, limit } = req.query;
    let urlPath = `/tables/${CONFIG.TABLE_INSPECTION}/records?page_size=${limit || 50}`;
    
    const resp = await bitableRequest('get', urlPath);
    if (resp.code !== 0) {
      return res.status(500).json({ ok: false, error: resp.msg });
    }
    
    let records = (resp.data.items || []).map(r => {
      const f = r.fields;
      return {
        recordId: r.record_id,
        storeId: val(f, '门店编号'),
        storeName: val(f, '门店名称'),
        region: val(f, '区域'),
        inspector: val(f, '巡检人'),
        inspectTime: val(f, '巡检时间'),
        scores: {
          display: toNum(f, '陈列标准得分'),
          cleanliness: toNum(f, '卫生状况得分'),
          pricing: toNum(f, '价签物料得分'),
          inventory: toNum(f, '库存样品得分'),
          service: toNum(f, '服务规范得分'),
          safety: toNum(f, '安全合规得分')
        },
        totalScore: toNum(f, '总分'),
        result: val(f, '巡检结果'),
        passed: val(f, '是否通过'),
        notes: val(f, '备注')
      };
    });
    
    // 按门店过滤（客户端过滤）
    if (storeId) {
      records = records.filter(r => r.storeId === storeId);
    }
    
    // 按时间倒序
    records.sort((a, b) => {
      const ta = typeof a.inspectTime === 'number' ? a.inspectTime : new Date(a.inspectTime).getTime();
      const tb = typeof b.inspectTime === 'number' ? b.inspectTime : new Date(b.inspectTime).getTime();
      return tb - ta;
    });
    
    res.json({ ok: true, data: records });
  } catch (e) {
    console.error('获取巡检历史失败:', e.message);
    res.status(500).json({ ok: false, error: e.message });
  }
});

// 获取巡检统计
app.get('/api/stats', async (req, res) => {
  try {
    const { storeId } = req.query;
    let urlPath = `/tables/${CONFIG.TABLE_INSPECTION}/records?page_size=500`;
    
    const resp = await bitableRequest('get', urlPath);
    if (resp.code !== 0) {
      return res.status(500).json({ ok: false, error: resp.msg });
    }
    
    let records = (resp.data.items || []);
    if (storeId) {
      records = records.filter(r => val(r.fields, '门店编号') === storeId);
    }
    
    const total = records.length;
    const passed = records.filter(r => {
      const p = val(r.fields, '是否通过');
      return p && p.includes('通过') && !p.includes('不') && !p.includes('未');
    }).length;
    
    const avgScore = total > 0 
      ? records.reduce((sum, r) => sum + toNum(r.fields, '总分'), 0) / total 
      : 0;
    
    // 各维度平均分
    const dimAvg = {};
    const dimMap = {
      '陈列标准': '陈列标准得分', '卫生状况': '卫生状况得分',
      '价签物料': '价签物料得分', '库存样品': '库存样品得分',
      '服务规范': '服务规范得分', '安全合规': '安全合规得分'
    };
    Object.entries(dimMap).forEach(([key, field]) => {
      dimAvg[key] = total > 0 
        ? Math.round(records.reduce((s, r) => s + toNum(r.fields, field), 0) / total * 10) / 10 
        : 0;
    });
    
    res.json({
      ok: true,
      data: {
        total,
        passed,
        failed: total - passed,
        passRate: total > 0 ? Math.round(passed / total * 100) : 0,
        avgScore: Math.round(avgScore * 10) / 10,
        dimensionAvg: dimAvg
      }
    });
  } catch (e) {
    console.error('获取统计失败:', e.message);
    res.status(500).json({ ok: false, error: e.message });
  }
});

// 兜底路由
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(CONFIG.PORT, () => {
  console.log(`[雨虹巡检应用] 服务已启动: http://localhost:${CONFIG.PORT}`);
});
