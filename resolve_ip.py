#!/usr/bin/env python3
import dns.resolver
import dns.edns
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import yaml

CONFIG_FILE = Path("config.yaml")

def get_beijing_time() -> str:
    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    return now.strftime("%m%d-%H%M")

def resolve_ips(domain: str, dns_server: str, ecs_subnet: str) -> list[str]:
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = [dns_server]
    resolver.timeout = 5
    resolver.lifetime = 10

    try:
        ecs = dns.edns.ECSOption.from_text(ecs_subnet)
        resolver.use_edns(edns=True, options=[ecs])
        answer = resolver.resolve(domain, "A")
        return [rdata.address for rdata in answer]
    except Exception as e:
        print(f"[{domain}] 解析失败: {type(e).__name__}: {e}")
        return []

def process_route(route: dict, time_str: str):
    name = route["name"]
    domain = route["domain"]
    dns_server = route["dns"]
    ecs = route["ecs"]
    count = int(route.get("count", 2))

    output_file = Path(f"ips-{name}")

    print(f"\n===== 处理通路: {name} =====")
    print(f"域名: {domain} | DNS: {dns_server} | ECS: {ecs} | 需要数量: {count}")

    ips = resolve_ips(domain, dns_server, ecs)
    print(f"实际解析到 {len(ips)} 个 IP: {ips}")

    if not ips:
        # 失败或 0 个 IP：覆盖写入一行保底内容
        content = f"{domain}#{domain}@{time_str}\n"
        output_file.write_text(content, encoding="utf-8")
        print(f"失败，已写入保底内容到 {output_file}")
        return

    # 成功：取前 count 个（不足则有几个写几个，不填充）
    selected = ips[:count]
    lines = [f"{ip}#{ip}@{time_str}" for ip in selected]
    content = "\n".join(lines) + "\n"

    output_file.write_text(content, encoding="utf-8")
    print(f"成功，已写入 {len(selected)} 个 IP 到 {output_file}")

def main():
    if not CONFIG_FILE.exists():
        print(f"错误：找不到配置文件 {CONFIG_FILE}")
        return

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    routes = config.get("routes", [])
    if not routes:
        print("配置文件中没有定义任何通路")
        return

    time_str = get_beijing_time()
    print(f"当前北京时间标记: {time_str}")
    print(f"共加载 {len(routes)} 路配置")

    for route in routes:
        process_route(route, time_str)

    print("\n全部处理完成")

if __name__ == "__main__":
    main()
