import paramiko, os, tarfile, io, time

HOST = "100.107.117.23"
USER = "administrator"
PASS = "root123root!@"
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

def run_sudo(client, cmd, desc="", timeout=120):
    """通过 sudo + 密码管道的安全方式执行命令"""
    full_cmd = f"echo '{PASS}' | sudo -S bash -c '{cmd}' 2>&1"
    print(f"  [{desc}] ...")
    stdin, stdout, stderr = client.exec_command(full_cmd, timeout=timeout)
    out = stdout.read().decode().strip()
    # 过滤掉 sudo 的密码提示行
    lines = [l for l in out.split('\n') if '[sudo]' not in l and 'password' not in l.lower()]
    clean = '\n'.join(lines)
    if clean: print(f"    {clean[:600]}")
    return clean

def run_cmd(client, cmd, desc="", timeout=30):
    print(f"  [{desc}] ...")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print(f"    {out[:400]}")
    if err: print(f"    ERR: {err[:200]}")
    return out

print("=== 1. 连接 + 检查 ===")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)

# 添加 administrator 到 docker 组
print("=== 2. 修复 Docker 权限 ===")
run_sudo(client, "usermod -aG docker administrator", "加入docker组")
run_sudo(client, "systemctl restart docker 2>&1 || service docker restart 2>&1", "重启docker")

# 让新组生效（需要新会话）
time.sleep(3)

# 重连
client.close()
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)

# 用 sudo 直接操作
print("=== 3. 清理旧容器 ===")
run_sudo(client, "cd /home/administrator/news-intel-platform && docker compose down 2>&1", "compose down")

print("=== 4. 启动 ===")
run_sudo(client, "cd /home/administrator/news-intel-platform && docker compose up -d --build 2>&1", "compose up", timeout=300)

print("=== 5. 等待服务 ===")
time.sleep(10)
run_sudo(client, "cd /home/administrator/news-intel-platform && docker compose ps 2>&1", "容器状态")

print("=== 6. 验证 ===")
run_cmd(client, "curl -s http://localhost:8000/health 2>&1", "API健康")
run_cmd(client, "curl -s -o /dev/null -w '%{http_code}' http://localhost:80/ 2>&1", "前端状态")

client.close()
print(f"\n✅ 部署完成！http://{HOST}")
