#!/usr/bin/env python3
import dns.resolver
import dns.edns
from pathlib import Path

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

    # 正确设置 ECS
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
    ips = resolve_ips()
    print(f"解析到 {len(ips)} 个 IP: {ips}")

    # 只取前两个
    selected = ips[:2]

    # 不足 2 个时用已有的补齐，保证始终两行
    while len(selected) < 2 and selected:
        selected.append(selected[0])

    if not selected:
        content = "0.0.0.0#0.0.0.0\n0.0.0.0#0.0.0.0\n"
        print("警告：解析失败，写入占位 IP")
    else:
        content = f"{selected[0]}#{selected[0]}\n{selected[1]}#{selected[1]}\n"

    OUTPUT_FILE.write_text(content, encoding="utf-8")
    print("已写入 ips.txt：")
    print(content.strip())

if __name__ == "__main__":
    main()
