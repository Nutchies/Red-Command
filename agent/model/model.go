package model

type Action struct {
	ID        int64   `json:"id"`
	Seq       int     `json:"seq"`
	Type      string  `json:"action_type"`
	Content   string  `json:"content"`
	Result    string  `json:"result,omitempty"`
	ExitCode  int     `json:"exit_code,omitempty"`
	Timestamp float64 `json:"timestamp"`
	Synced    bool    `json:"-"`
}

type HeartbeatRequest struct {
	ClientID string `json:"client_id"`
	Hostname string `json:"hostname"`
	IP       string `json:"ip"`
	Version  string `json:"version"`
}

type SyncRequest struct {
	ClientID string   `json:"client_id"`
	Actions  []Action `json:"actions"`
}
