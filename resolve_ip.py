#!/usr/bin/env python3
import dns.resolver
import dns.edns
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

# ==================== 配置 ====================
DOMAIN = "ct.877774.xyz"
DNS_SERVER = "8.8.8.8"
ECS_SUBNET = "14.153.0.0/24"
OUTPUT_FILE = Path("ips.txt")
# ==============================================

def resolve_ips():
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = [DNS_SERVER]
    resolver.timeout = 5
    resolver.lifetime = 10

    ecs = dns.edns.ECSOption.from_text(ECS_SUBNET)
    resolver.use_edns(edns=True, options=[ecs])

    try:
        answer = resolver.resolve(DOMAIN, "A")
        ips = [rdata.address for rdata in answer]
        return ips
    except Exception as e:
        print(f"解析失败: {type(e).__name__}: {e}")
        return []

def main():
    # 北京时间
    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    time_str = now.strftime("%m%d-%H%M")   # 例如 0918-0204

    ips = resolve_ips()
    print(f"解析到 {len(ips)} 个 IP: {ips}")
    print(f"时间标记: {time_str}")

    if not ips:
        # 解析失败：追加一行，不覆盖原内容
        fail_line = f"{DOMAIN}#解析失败 {time_str}\n"
        with OUTPUT_FILE.open("a", encoding="utf-8") as f:
            f.write(fail_line)
        print("解析失败，已追加记录：")
        print(fail_line.strip())
        return

    # 成功：取前两个（不足则补齐）
    selected = ips[:2]
    while len(selected) < 2:
        selected.append(selected[0])

    content = (
        f"{selected[0]}#{selected[0]} {time_str}\n"
        f"{selected[1]}#{selected[1]} {time_str}\n"
    )

    OUTPUT_FILE.write_text(content, encoding="utf-8")
    print("已覆盖写入 ips.txt：")
    print(content.strip())

if __name__ == "__main__":
    main()
