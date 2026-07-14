#!/bin/bash
# deploy_agent_bash.sh - Bash 环境部署脚本

set -e

AGENT_DIR="/opt/red-agent"
SERVER_URL="https://你的Server地址:8443"

echo "=========================================="
echo "Red Team Agent 部署脚本 (Bash)"
echo "=========================================="

# 1. 安装依赖
echo "[1/5] 安装依赖 (socat)..."
if command -v apt &> /dev/null; then
    sudo apt update && sudo apt install -y socat
elif command -v yum &> /dev/null; then
    sudo yum install -y socat
elif command -v pacman &> /dev/null; then
    sudo pacman -S socat
else
    echo "警告: 未检测到支持的包管理器，请手动安装 socat"
fi

# 2. 创建目录
echo "[2/5] 创建目录..."
sudo mkdir -p $AGENT_DIR
sudo chown $(whoami):$(whoami) $AGENT_DIR
echo "     Agent目录: $AGENT_DIR"

# 3. 配置Bash钩子
echo "[3/5] 配置Shell钩子..."

BASH_HOOK='
# Red Team Agent - 实时命令捕获钩子 (Bash)
if [ -n "$_RED_BASH_HOOK_LOADED" ]; then
    return
fi
_RED_BASH_HOOK_LOADED=1

RED_AGENT_SOCKET="/tmp/red-agent.sock"

red_send_to_agent() {
    local cmd="$1"
    if [ -n "$cmd" ] && [ ${#cmd} -ge 2 ]; then
        if [ "$cmd" = "$_red_last_sent" ]; then
            local now=$(date +%s)
            if [ $((now - _red_last_sent_time)) -lt 1 ]; then
                return
            fi
        fi
        _red_last_sent="$cmd"
        _red_last_sent_time=$(date +%s)
        if [ -S "$RED_AGENT_SOCKET" ]; then
            echo "$cmd" | socat - UNIX-CONNECT:"$RED_AGENT_SOCKET" 2>/dev/null
        fi
    fi
}

red_preexec() {
    local cmd="$BASH_COMMAND"
    if [ -n "$cmd" ] && [ "$cmd" != "$PROMPT_COMMAND" ] && [ "$cmd" != "red_preexec" ]; then
        red_send_to_agent "cd $(pwd) && $cmd"
    fi
}

if [ -z "$_RED_DEBUG_TRAP_SET" ]; then
    _RED_DEBUG_TRAP_SET=1
    trap "red_preexec" DEBUG
fi
'

# 检查是否已添加钩子
if ! grep -q "Red Team Agent" /etc/bash.bashrc 2>/dev/null; then
    echo "$BASH_HOOK" | sudo tee -a /etc/bash.bashrc > /dev/null
    echo "     已添加钩子到 /etc/bash.bashrc"
else
    echo "     钩子已存在，跳过"
fi

# 4. 复制Agent可执行文件
echo "[4/5] 复制Agent..."
if [ -f "./red-agent" ]; then
    cp ./red-agent $AGENT_DIR/
    chmod +x $AGENT_DIR/red-agent
    echo "     已复制 red-agent"
else
    echo "     警告: 当前目录未找到 red-agent，请先复制到此处"
fi

# 5. 启动Agent
echo "[5/5] 启动Agent..."
cd $AGENT_DIR
nohup ./red-agent --server $SERVER_URL > agent.log 2>&1 &
sleep 2

# 验证
if pgrep -f "./red-agent" > /dev/null; then
    echo ""
    echo "=========================================="
    echo "部署完成！"
    echo "=========================================="
    echo "Agent目录: $AGENT_DIR"
    echo "日志文件: $AGENT_DIR/agent.log"
    echo "Socket: /tmp/red-agent.sock"
    echo ""
    echo "请关闭此终端，重新打开一个新终端"
    echo "查看日志: tail -f $AGENT_DIR/agent.log"
    echo "验证记录: sqlite3 $AGENT_DIR/agent.db \"SELECT * FROM actions LIMIT 3;\""
else
    echo "Agent启动失败，请查看日志: $AGENT_DIR/agent.log"
fi
