package sync

import (
	"bytes"
	"crypto/tls"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net"
	"net/http"
	"net/url"
	"time"

	"github.com/red-team/agent/config"
	"github.com/red-team/agent/db"
	"github.com/red-team/agent/model"
)

type SyncClient struct {
	cfg *config.Config
	db  *db.DB
}

func New(cfg *config.Config, database *db.DB) *SyncClient {
	return &SyncClient{cfg: cfg, db: database}
}

func (s *SyncClient) Heartbeat() error {
	req := model.HeartbeatRequest{
		ClientID: s.cfg.ClientID,
		Hostname: s.cfg.Hostname,
		IP:       getLocalIP(),
		Version:  "1.0.0",
	}

	return s.post("/api/heartbeat", req)
}

func (s *SyncClient) Sync() error {
	actions, err := s.db.GetUnsynced(100)
	if err != nil {
		return fmt.Errorf("获取未同步数据失败: %v", err)
	}

	log.Printf("[Agent] Sync: 获取到 %d 条未同步数据, ClientID: %s", len(actions), s.cfg.ClientID)

	if len(actions) == 0 {
		return nil
	}

	req := model.SyncRequest{
		ClientID: s.cfg.ClientID,
		Actions:  actions,
	}

	if err := s.post("/api/actions", req); err != nil {
		return fmt.Errorf("同步数据失败: %v", err)
	}

	ids := make([]int64, len(actions))
	for i, a := range actions {
		ids[i] = a.ID
	}
	return s.db.MarkSynced(ids)
}

func (s *SyncClient) post(path string, data interface{}) error {
	jsonData, err := json.Marshal(data)
	if err != nil {
		return err
	}

	u, err := url.Parse(s.cfg.ServerURL + path)
	if err != nil {
		return err
	}

	req, err := http.NewRequest("POST", u.String(), bytes.NewBuffer(jsonData))
	if err != nil {
		return err
	}

	req.Header.Set("Content-Type", "application/json")

	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	client := &http.Client{Timeout: 10 * time.Second, Transport: tr}
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("服务器返回错误: %d - %s", resp.StatusCode, string(body))
	}

	return nil
}

func getLocalIP() string {
	addrs, err := net.InterfaceAddrs()
	if err != nil {
		return "127.0.0.1"
	}
	for _, addr := range addrs {
		if ipnet, ok := addr.(*net.IPNet); ok && !ipnet.IP.IsLoopback() {
			if ipnet.IP.To4() != nil {
				return ipnet.IP.String()
			}
		}
	}
	return "127.0.0.1"
}
