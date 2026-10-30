#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 subs-check 生成的纯节点 all.yaml，合成带分组 + 本地规则的 clash_full.yaml。

v2 变更：
1. 修复「节点选择」只有「自动选择 + DIRECT」的问题 —— 原模板把节点选择写死成
   只引用两个成员，节点全部堆在 url-test 组里，用户无法手动挑节点。
   现在改为标准四级结构：节点选择 / 自动选择 / 故障转移 / 手动选择 / 负载均衡，
   其中「手动选择」用 include-all 承载全部节点。
2. url-test 的探测地址由 http 改为 https（http 会被部分出口/中间件改写，
   导致延迟测不准、迟迟不出数字），并补 lazy / timeout。
3. 仍然完全不做「节点名 → 分组」的字符串匹配，规避转义名导致 not found。

注意：include-all 只在 mihomo（Clash.Meta）内核生效；
原版 Clash / Clash for Windows 不支持，会退化成空组。
"""
import sys

SRC = 'output/all.yaml'
DST = 'result/clash_full.yaml'

try:
    node_yaml = open(SRC, encoding='utf-8').read()
except FileNotFoundError:
    print('[skip] 未找到', SRC)
    sys.exit(0)

node_yaml = node_yaml.rstrip()

header = """# 由 subs-check 自动生成（本地规则版，无联网依赖）
"""

groups = """proxy-groups:
  - name: "🚀 节点选择"
    type: select
    proxies:
      - "♻️ 自动选择"
      - "🔄 故障转移"
      - "🎯 手动选择"
      - "⚖️ 负载均衡"
      - DIRECT
  - name: "♻️ 自动选择"
    type: url-test
    include-all: true
    url: "https://www.gstatic.com/generate_204"
    interval: 300
    timeout: 5000
    tolerance: 50
    lazy: false
  - name: "🔄 故障转移"
    type: fallback
    include-all: true
    url: "https://www.gstatic.com/generate_204"
    interval: 300
    timeout: 5000
    lazy: false
  - name: "🎯 手动选择"
    type: select
    include-all: true
  - name: "⚖️ 负载均衡"
    type: load-balance
    include-all: true
    url: "https://www.gstatic.com/generate_204"
    interval: 300
    timeout: 5000
    lazy: false
"""

rules = """rules:
  - GEOIP,CN,DIRECT
  - MATCH,🚀 节点选择
"""

out = header + node_yaml + '\n' + groups + '\n' + rules
open(DST, 'w', encoding='utf-8', newline='\n').write(out)
print('[ok] 已生成', DST)
