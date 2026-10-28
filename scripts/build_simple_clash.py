#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 subs-check 生成的纯节点 all.yaml，合成带极简分组+本地规则的 clash_full.yaml。
关键：自动选择分组用 include-all: true 自动包含全部节点，
完全不做名字提取/匹配，规避转义名导致的 not found。
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
      - DIRECT
  - name: "♻️ 自动选择"
    type: url-test
    include-all: true
    url: "http://www.gstatic.com/generate_204"
    interval: 300
    tolerance: 50
"""

rules = """rules:
  - GEOIP,CN,DIRECT
  - MATCH,🚀 节点选择
"""

out = header + node_yaml + '\n' + groups + '\n' + rules
open(DST, 'w', encoding='utf-8', newline='\n').write(out)
print('[ok] 已生成', DST)
