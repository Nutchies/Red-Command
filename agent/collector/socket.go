package collector

import (
	"bufio"
	"log"
	"net"
	"os"
	"strings"
	"time"

	"github.com/red-team/agent/db"
	"github.com/red-team/agent/model"
)

type SocketServer struct {
	db       *db.DB
	collector *Collector
	socketPath string
	listener  net.Listener
}

func NewSocketServer(database *db.DB, collector *Collector) *SocketServer {
	return &SocketServer{
		db:        database,
		collector: collector,
		socketPath: "/tmp/red-agent.sock",
	}
}

func (s *SocketServer) Start() error {
	// 删除已存在的socket文件
	os.Remove(s.socketPath)

	// 创建Unix socket
	listener, err := net.Listen("unix", s.socketPath)
	if err != nil {
		return err
	}
	s.listener = listener

	// 设置socket文件权限为所有人可读写
	os.Chmod(s.socketPath, 0666)

	log.Printf("[Agent] Socket服务器启动: %s", s.socketPath)

	go s.acceptLoop()
	return nil
}

func (s *SocketServer) acceptLoop() {
	for {
		conn, err := s.listener.Accept()
		if err != nil {
			log.Printf("[Agent] Socket accept错误: %v", err)
			continue
		}
		go s.handleConnection(conn)
	}
}

func (s *SocketServer) handleConnection(conn net.Conn) {
	defer conn.Close()

	reader := bufio.NewReader(conn)
	for {
		line, err := reader.ReadString('\n')
		if err != nil {
			return
		}

		cmd := strings.TrimSpace(line)
		log.Printf("[Agent] Socket收到命令: %q", cmd)
		if cmd == "" {
			continue
		}

		// 处理实时命令
		go s.processCommand(cmd)
	}
}

func (s *SocketServer) processCommand(cmd string) {
	trimmedCmd := strings.TrimSpace(cmd)
	
	if len(trimmedCmd) < 2 {
		return
	}

	// 跳过内部命令
	skipPatterns := []string{"socat", "export ", "alias ", "source ", "unset ", "local ", "declare "}
	for _, pattern := range skipPatterns {
		if strings.HasPrefix(trimmedCmd, pattern) {
			return
		}
	}

	// 提取真实命令
	realCmd := trimmedCmd
	
	// 处理 CMD: 前缀
	if strings.HasPrefix(realCmd, "CMD:") {
		realCmd = strings.TrimSpace(realCmd[4:])
	}
	
	// 处理 echo "CMD:xxx" 格式（递归命令）
	if strings.HasPrefix(realCmd, `echo "CMD:`) || strings.HasPrefix(realCmd, `echo 'CMD:`) {
		var prefix string
		if strings.HasPrefix(realCmd, `echo "CMD:`) {
			prefix = `echo "CMD:`
		} else {
			prefix = `echo 'CMD:`
		}
		rest := realCmd[len(prefix):]
		if idx := strings.LastIndex(rest, `"`); idx > 0 {
			realCmd = strings.TrimSpace(rest[:idx])
		} else if idx := strings.LastIndex(rest, `'`); idx > 0 {
			realCmd = strings.TrimSpace(rest[:idx])
		}
		if realCmd == "" || strings.HasPrefix(strings.TrimSpace(realCmd), "echo") || strings.HasPrefix(strings.TrimSpace(realCmd), "socat") {
			return
		}
	}

	// 提取原始命令（去掉cd ... && 前缀）
	originalCmd := realCmd
	if strings.HasPrefix(realCmd, "cd ") {
		if idx := strings.Index(realCmd, " && "); idx != -1 {
			originalCmd = strings.TrimSpace(realCmd[idx+4:])
		}
	}
	
	if len(originalCmd) < 2 {
		return
	}
	
	if strings.HasPrefix(originalCmd, "socat") || strings.HasPrefix(originalCmd, "echo") {
		return
	}

	// 保存到数据库（先保存命令，再异步执行）
	action := &model.Action{
		Type:      "realtime_command",
		Content:   originalCmd,
		Timestamp: float64(time.Now().Unix()),
	}

	if err := s.db.SaveAction(action); err != nil {
		log.Printf("[Agent] 保存实时命令失败: %v", err)
		return
	}
	log.Printf("[Agent] 实时捕获命令: %s", originalCmd)

	// 对交互式命令（ssh等）不执行，避免挂起
	if strings.HasPrefix(originalCmd, "ssh ") || strings.HasPrefix(originalCmd, "telnet ") || strings.HasPrefix(originalCmd, "ftp ") {
		return
	}

	// 执行命令并捕获输出（异步更新，不阻塞主流程）
	go func(actionID int64) {
		result, exitCode, _ := s.collector.executeAndCapture(originalCmd)
		updateAction := &model.Action{
			ID:       actionID,
			Result:   result,
			ExitCode: exitCode,
		}
		if err := s.db.UpdateAction(updateAction); err != nil {
			log.Printf("[Agent] 更新命令结果失败: %v", err)
		}
	}(action.ID)
}

func (s *SocketServer) Stop() {
	if s.listener != nil {
		s.listener.Close()
	}
	os.Remove(s.socketPath)
}