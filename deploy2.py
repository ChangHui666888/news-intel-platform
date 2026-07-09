import paramiko, os, tarfile, io, time

HOST = "100.107.117.23"
USER = "administrator"
PASS = "root123root!@"
PROJECT_DIR = r"C:\Users\ChangHui\AppData\Local\hermes\profiles\outside-deepdeek\skills\research\search-engine-v2\scripts\news-intel-platform"

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username=USER, password=PASS, timeout=15)

# Upload
tar_buffer = io.BytesIO()
with tarfile.open(fileobj=tar_buffer, mode='w:gz') as tar:
    for root, dirs, files in os.walk(PROJECT_DIR):
        dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__', 'node_modules')]
        for f in files:
            if f in ('deploy_check.py', 'deploy.py'):
                continue
            full = os.path.join(root, f)
            arc = os.path.relpath(full, PROJECT_DIR)
            tar.add(full, arc)
tar_buffer.seek(0)
sftp = c.open_sftp()
sftp.putfo(tar_buffer, 'project.tar.gz')
sftp.close()

stdin, stdout, stderr = c.exec_command(
    'cd /home/administrator && tar xzf project.tar.gz -C news-intel-platform --overwrite && rm project.tar.gz && echo UPLOAD_OK',
    timeout=15)
print("upload:", stdout.read().decode().strip())

# Build web (which failed before)
stdin, stdout, stderr = c.exec_command(
    'cd /home/administrator/news-intel-platform && docker compose build web 2>&1',
    timeout=300)
out = stdout.read().decode().strip()
print("build:", out[-500:] if len(out) > 500 else out)

# Start all
stdin, stdout, stderr = c.exec_command(
    'cd /home/administrator/news-intel-platform && docker compose up -d 2>&1',
    timeout=120)
print("up:", stdout.read().decode().strip())

time.sleep(15)

# Check
stdin, stdout, stderr = c.exec_command(
    'cd /home/administrator/news-intel-platform && docker compose ps 2>&1 && echo --- && curl -s http://localhost:8000/health && echo --- && curl -s -o /dev/null -w "%{http_code}" http://localhost:80/',
    timeout=15)
print("status:\n", stdout.read().decode().strip())

c.close()
