#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""subs-check 邮件报告生成器：解析 check.log 与 result/all.yaml，产出 mail_report.md"""
import re
import subprocess
import datetime
import os


def count_names(text):
    return len(re.findall(r'(?<![a-z])name:', text))


def stat(label, log):
    m = re.findall(label + r'[：:]\s*(\d+)', log)
    return m[-1] if m else '-'


log = re.sub(r'\x1b\[[0-9;]*m', '', open('check.log', encoding='utf-8', errors='ignore').read())
total = stat(r'获取节点数量', log)
dedup = stat(r'去重后节点数量', log)
alive = stat(r'存活节点数量', log)
usable = stat(r'可用节点数量', log)

# 当前 / 上一轮节点数对比
cur = count_names(open('result/all.yaml', encoding='utf-8').read()) if os.path.exists('result/all.yaml') else 0
prev_raw = subprocess.run(['git', 'show', 'HEAD:result/all.yaml'], capture_output=True, text=True)
prev = count_names(prev_raw.stdout) if prev_raw.returncode == 0 else 0
delta = cur - prev
if prev:
    delta_txt = '（较上轮 +{}）'.format(delta) if delta >= 0 else '（较上轮 -{}）'.format(-delta)
else:
    delta_txt = '（本轮报告起始）'

# 地区分布与速度统计（从节点名解析，如 "US_1|1.3MB/s"）
regions = {}
speeds = []
if os.path.exists('result/all.yaml'):
    txt = open('result/all.yaml', encoding='utf-8').read()
    for n in re.findall(r'(?<![a-z])name:\s*"((?:[^"\\]|\\.)*)"', txt):
        m = re.search(r'([A-Z]{2})_\d+', n)
        if m:
            regions[m.group(1)] = regions.get(m.group(1), 0) + 1
        sp = re.search(r'(\d+(?:\.\d+)?)(KB|MB)/s', n)
        if sp:
            speeds.append(float(sp.group(1)) / (1 if sp.group(2) == 'MB' else 1024))
top = sorted(regions.items(), key=lambda x: -x[1])[:8]
top_txt = '、'.join('{} {}个'.format(c, n) for c, n in top) if top else '暂无数据'
if speeds:
    speeds.sort(reverse=True)
    sp_txt = '最快 {:.1f} MB/s，平均 {:.2f} MB/s'.format(speeds[0], sum(speeds) / len(speeds))
else:
    sp_txt = '本轮无测速数据'

now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
ts = now.strftime('%Y-%m-%d %H:%M')
run_url = os.environ.get('RUN_URL', '')

files = []
for f in ('clash_full.yaml', 'all.yaml', 'base64.txt'):
    p = 'result/' + f
    if os.path.exists(p):
        files.append('- `{}`（{:.0f} KB）'.format(f, os.path.getsize(p) / 1024))

md = """# 📡 节点检测报告

**{ts}（北京时间）· subs-check 每 6 小时自动检测**

## 本轮结果

- **可用节点：{usable} 个** {delta_txt}
- 抓取输入：{total} → 去重：{dedup} → 真实测活存活：{alive}
- 速度：{sp_txt}
- 地区分布：{top_txt}

## 订阅

```
https://ghfast.top/https://raw.githubusercontent.com/leo0769/subs-check/master/result/clash_full.yaml
```

Clash 更新订阅即可拿到最新节点；此链接长期不变，每 6 小时自动刷新。

## 结果文件

{files}

[查看本次运行详情]({run_url})

---
🤖 由 GitHub Actions 自动发送 · 免费节点仅供参考，请勿传输敏感数据
""".format(ts=ts, usable=usable, delta_txt=delta_txt, total=total, dedup=dedup,
           alive=alive, sp_txt=sp_txt, top_txt=top_txt,
           files=chr(10).join(files) if files else '本轮无结果文件', run_url=run_url)

open('mail_report.md', 'w', encoding='utf-8').write(md)
print(md)
