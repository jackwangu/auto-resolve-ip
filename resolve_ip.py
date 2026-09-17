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
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [DNS_SERVER]
    resolver.lifetime = 8
    resolver.timeout = 5

    # 添加 ECS
    ecs_option = dns.edns.ECSOption.from_text(ECS_SUBNET)

    try:
        answer = resolver.resolve(
            DOMAIN,
            "A",
            raise_on_no_answer=True,
            edns=0,
            options=[ecs_option]
        )
        ips = [rdata.address for rdata in answer]
        return ips
    except Exception as e:
        print(f"解析失败: {e}")
        return []

def main():
    ips = resolve_ips()
    print(f"解析到 {len(ips)} 个 IP: {ips}")

    # 只取前两个
    selected = ips[:2]

    # 如果不足 2 个，用已有的补齐（保证文件始终有两行）
    while len(selected) < 2 and selected:
        selected.append(selected[0])

    if not selected:
        # 解析失败时写入空占位，避免文件损坏
        content = "【0.0.0.0#0.0.0.0】\n【0.0.0.0#0.0.0.0】\n"
    else:
        content = f"【{selected[0]}#{selected[0]}】\n【{selected[1]}#{selected[1]}】\n"

    OUTPUT_FILE.write_text(content, encoding="utf-8")
    print("已写入 ips.txt：")
    print(content)

if __name__ == "__main__":
    main()
