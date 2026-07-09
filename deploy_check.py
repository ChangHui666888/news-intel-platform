import paramiko
import time

HOST = "100.107.117.23"
USER = "administrator"
PASS = "root123root!@"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(HOST, username=USER, password=PASS, timeout=15)
    print("✅ 已连接")
    
    commands = [
        ("whoami", "用户"),
        ("docker --version 2>&1", "Docker"),
        ("docker compose version 2>&1", "Docker Compose"),
        ("git --version 2>&1", "Git"),
        ("ls news-intel-platform 2>&1 || echo 'NOT_EXISTS'", "项目目录"),
        ("sudo -n echo OK 2>&1 || echo 'NO_SUDO_PASS'", "Sudo权限"),
    ]
    
    for cmd, desc in commands:
        stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        print(f"[{desc}] {out[:200]}")
        if err: print(f"  err: {err[:100]}")
    
    client.close()
except Exception as e:
    print(f"❌ {e}")
