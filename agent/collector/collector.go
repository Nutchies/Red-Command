package collector

import (
	"bufio"
	"bytes"
	"context"
	"os"
	"os/exec"
	"strings"
	"time"

	"github.com/red-team/agent/db"
	"github.com/red-team/agent/model"
)

type Collector struct {
	db  *db.DB
	seq int
	// 记录已处理的命令，避免重复执行
	processedCommands map[string]bool
}

func New(database *db.DB) *Collector {
	return &Collector{
		db:                database,
		processedCommands: make(map[string]bool),
	}
}

func (c *Collector) Collect() error {
	// 只收集系统信息，跳过bash_history（避免执行历史命令导致卡住）
	if err := c.collectSystemInfo(); err != nil {
		return err
	}
	return nil
}

func (c *Collector) shouldSkip(cmd string) bool {
	return false
}

func (c *Collector) executeAndCapture(cmd string) (string, int, error) {
	// 使用context设置10秒超时
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	bashCmd := exec.CommandContext(ctx, "bash", "-c", cmd+" 2>&1")
	var stdout, stderr bytes.Buffer
	bashCmd.Stdout = &stdout
	bashCmd.Stderr = &stderr

	err := bashCmd.Run()
	exitCode := 0
	if err != nil {
		if exitError, ok := err.(*exec.ExitError); ok {
			exitCode = exitError.ExitCode()
		} else {
			exitCode = -1
		}
		if ctx.Err() == context.DeadlineExceeded {
			result := stdout.String()
			if result != "" {
				result += "\n"
			}
			result += "[Agent] Command timed out (10s)"
			return result, -1, nil
		}
	}

	result := stdout.String()
	if stderr.Len() > 0 {
		if result != "" {
			result += "\n"
		}
		result += "[stderr] " + stderr.String()
	}

	return result, exitCode, nil
}

func (c *Collector) collectBashHistory() error {
	home := os.Getenv("HOME")
	if home == "" {
		home = "/root"
	}

	historyFile := home + "/.bash_history"

	file, err := os.Open(historyFile)
	if err != nil {
		return err
	}
	defer file.Close()

	var lastLines []string
	scanner := bufio.NewScanner(file)
	// 增加缓冲区大小到10MB，避免长命令行报错
	scanner.Buffer(make([]byte, 1024*1024), 10*1024*1024)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line != "" && !strings.HasPrefix(line, "#") {
			lastLines = append(lastLines, line)
		}
	}

	// 只取最后30条
	if len(lastLines) > 30 {
		lastLines = lastLines[len(lastLines)-30:]
	}

	for _, cmd := range lastLines {
		// 避免重复处理同一命令
		if c.processedCommands[cmd] {
			continue
		}
		c.processedCommands[cmd] = true

		c.seq++
		action := &model.Action{
			Seq:       c.seq,
			Type:      "command",
			Content:   cmd,
			Timestamp: float64(time.Now().Unix()),
		}

		// 执行命令并捕获输出
		result, exitCode, _ := c.executeAndCapture(cmd)
		// 无论成功与否都保存result
		if result != "" {
			action.Result = result
		}
		action.ExitCode = exitCode

		c.db.SaveAction(action)
	}

	return nil
}

func (c *Collector) collectSystemInfo() error {
	c.seq++
	action := &model.Action{
		Seq:       c.seq,
		Type:      "collect",
		Content:   "system_info",
		Timestamp: float64(time.Now().Unix()),
	}

	var buf bytes.Buffer

	// 获取主机名
	if hostname, err := exec.Command("hostname").Output(); err == nil {
		buf.WriteString("Hostname: ")
		buf.Write(hostname)
	}

	// 获取用户名
	if user, err := exec.Command("whoami").Output(); err == nil {
		buf.WriteString("User: ")
		buf.Write(user)
	}

	// 获取IP
	if ip, err := exec.Command("hostname", "-I").Output(); err == nil {
		buf.WriteString("IP: ")
		buf.Write(ip)
	}

	// 获取当前目录
	if pwd, err := exec.Command("pwd").Output(); err == nil {
		buf.WriteString("PWD: ")
		buf.Write(pwd)
	}

	action.Result = buf.String()
	return c.db.SaveAction(action)
}
