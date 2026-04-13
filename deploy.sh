#!/bin/bash
set -e

echo "=== 1. 安装系统依赖 ==="
apt-get update && apt-get install -y python3 python3-venv python3-pip git

echo "=== 2. 创建项目目录 ==="
mkdir -p /opt/douban-monitor
cd /opt/douban-monitor

echo "=== 3. 克隆代码 ==="
if [ -d ".git" ]; then
  git pull
else
  git clone https://github.com/dengruihan/Douban_Film_Comment-monitoring.git .
fi

echo "=== 4. 创建虚拟环境并安装依赖 ==="
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "=== 5. 配置环境变量 ==="
if [ ! -f .env ]; then
  cat > .env << 'ENVFILE'
DEEPSEEK_API_KEY=
ZHIPU_AI_API_KEY=
DEEPSEEK_MODEL=deepseek-chat
ENVFILE
  echo "已创建 .env 文件，如需配置 API Key 请手动编辑: nano /opt/douban-monitor/.env"
fi

echo "=== 6. 安装 systemd 服务 ==="
cat > /etc/systemd/system/douban-monitor.service << 'SERVICE'
[Unit]
Description=Douban Film Comment Monitoring (Streamlit)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/douban-monitor
Environment=PATH=/opt/douban-monitor/venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/opt/douban-monitor/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true --browser.gatherUsageStats false
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable douban-monitor
systemctl restart douban-monitor

echo "=== 7. 检查服务状态 ==="
sleep 3
systemctl status douban-monitor --no-pager

echo ""
echo "============================================"
echo "  部署完成！"
echo "  访问地址: http://47.98.161.252:8501"
echo "============================================"
echo ""
echo "常用命令:"
echo "  查看状态: systemctl status douban-monitor"
echo "  查看日志: journalctl -u douban-monitor -f"
echo "  重启服务: systemctl restart douban-monitor"
echo "  更新代码: cd /opt/douban-monitor && git pull && systemctl restart douban-monitor"
