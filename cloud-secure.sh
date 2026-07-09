#!/bin/bash
# cloud-secure.sh — UFW + Docker 安全加固（正确方案）
# Docker 的端口映射绕过 UFW 是因为它在 iptables FORWARD 链优先级高于 ufw-user-forward
# 解决方案：在 DOCKER-USER 链中加白名单（Docker 尊重此链，UFW 也能与之共存）
# 运行: sudo bash cloud-secure.sh

set -e

ALLOW_IPS="100.126.188.44 100.120.73.47"

echo "=== 1. 配置 UFW ==="
ufw --force reset
ufw default deny incoming
ufw default allow outgoing

# 公开端口（不需要白名单）
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8080/tcp
ufw allow 5678/tcp
ufw allow 22/tcp

# API/敏感端口 — 仅白名单 IP
for ip in $ALLOW_IPS; do
    ufw allow from $ip to any port 8001 proto tcp
    ufw allow from $ip to any port 8000 proto tcp
    ufw allow from $ip to any port 5432 proto tcp
done

ufw --force enable

echo ""
echo "=== 2. 修复 Docker 绕过 — DOCKER-USER 链白名单 ==="

# 清除旧 DOCKER-USER 规则
iptables -F DOCKER-USER 2>/dev/null || true

# 默认：允许已建立连接、允许 Docker 内部网络、拒绝外部访问容器端口
iptables -I DOCKER-USER -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -I DOCKER-USER -s 172.16.0.0/12 -j ACCEPT
iptables -I DOCKER-USER -s 127.0.0.1 -j ACCEPT

# 白名单 IP 可访问所有容器端口
for ip in $ALLOW_IPS; do
    iptables -I DOCKER-USER -s $ip -j ACCEPT
done

# 公开端口（80, 443, 8080, 5678）— 所有 IP 可访问
iptables -I DOCKER-USER -p tcp --dport 80 -j ACCEPT
iptables -I DOCKER-USER -p tcp --dport 443 -j ACCEPT
iptables -I DOCKER-USER -p tcp --dport 8080 -j ACCEPT
iptables -I DOCKER-USER -p tcp --dport 5678 -j ACCEPT

# 默认拒绝其他所有
iptables -A DOCKER-USER -j DROP

# 持久化
if command -v netfilter-persistent &>/dev/null; then
    netfilter-persistent save
elif command -v iptables-save &>/dev/null; then
    iptables-save > /etc/iptables/rules.v4 2>/dev/null || true
fi

echo ""
echo "=== 3. 加固 docker-compose — PostgreSQL 不暴露到外网 ==="
# 修改 docker-compose.yml: 移除 PostgreSQL 的 ports 映射
cd /home/administrator/news-intel-platform
sed -i '/5432:5432/d' docker-compose.yml
docker compose up -d

echo ""
echo "=== 4. 验证结果 ==="
echo "--- UFW ---"
ufw status verbose
echo ""
echo "--- DOCKER-USER rules ---"
iptables -L DOCKER-USER -n -v
echo ""
echo "--- 容器端口 ---"
docker ps --format "table {{.Names}}\t{{.Ports}}"
echo ""
echo "✅ 加固完成！5432 已移除公网暴露，8001 仅白名单IP可达"
