package config

import (
	"crypto/md5"
	"fmt"
	"net"
	"os"
	"runtime"
)

type Config struct {
	ServerURL string
	ClientID  string
	Hostname  string
}

func New(serverURL string) *Config {
	return &Config{
		ServerURL: serverURL,
		ClientID:  getClientID(),
		Hostname:  getHostname(),
	}
}

func getClientID() string {
	clientIDFile := "client_id.txt"
	
	if data, err := os.ReadFile(clientIDFile); err == nil {
		return string(data)
	}
	
	raw := generateUniqueIdentifier()
	clientID := fmt.Sprintf("%x", md5.Sum([]byte(raw)))[:16]
	
	os.WriteFile(clientIDFile, []byte(clientID), 0644)
	
	return clientID
}

func generateUniqueIdentifier() string {
	hostname, _ := os.Hostname()
	
	var macs []string
	ifaces, err := net.Interfaces()
	if err == nil {
		for _, iface := range ifaces {
			if iface.HardwareAddr != nil && iface.HardwareAddr.String() != "" {
				macs = append(macs, iface.HardwareAddr.String())
			}
		}
	}
	
	if len(macs) > 0 {
		return fmt.Sprintf("%s-%s-%s", hostname, macs[0], runtime.GOARCH)
	}
	
	return fmt.Sprintf("%s-%s", hostname, runtime.GOARCH)
}

func getHostname() string {
	hostname, _ := os.Hostname()
	if hostname == "" {
		return "unknown"
	}
	return hostname
}
