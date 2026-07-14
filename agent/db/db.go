package db

import (
	"database/sql"
	"sync"

	_ "github.com/mattn/go-sqlite3"
	"github.com/red-team/agent/model"
)

type DB struct {
	conn *sql.DB
	mu   sync.Mutex
	seq  int
}

func New(path string) (*DB, error) {
	conn, err := sql.Open("sqlite3", path)
	if err != nil {
		return nil, err
	}

	db := &DB{conn: conn}
	db.init()
	return db, nil
}

func (d *DB) init() {
	d.conn.Exec(`
		CREATE TABLE IF NOT EXISTS actions (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			seq INTEGER NOT NULL,
			type TEXT NOT NULL,
			content TEXT,
			result TEXT,
			exit_code INTEGER DEFAULT 0,
			timestamp REAL NOT NULL,
			synced INTEGER DEFAULT 0
		)
	`)
	d.conn.Exec(`CREATE INDEX IF NOT EXISTS idx_actions_synced ON actions(synced)`)
}

func (d *DB) SaveAction(action *model.Action) error {
	d.mu.Lock()
	defer d.mu.Unlock()

	d.seq++
	action.Seq = d.seq

	result, err := d.conn.Exec(
		`INSERT INTO actions (seq, type, content, result, exit_code, timestamp, synced) VALUES (?, ?, ?, ?, ?, ?, 0)`,
		action.Seq, action.Type, action.Content, action.Result, action.ExitCode, action.Timestamp,
	)
	if err != nil {
		return err
	}

	id, err := result.LastInsertId()
	if err != nil {
		return err
	}
	action.ID = id
	return nil
}

func (d *DB) GetUnsynced(limit int) ([]model.Action, error) {
	rows, err := d.conn.Query(
		`SELECT id, seq, type, content, result, exit_code, timestamp FROM actions WHERE synced=0 ORDER BY id LIMIT ?`,
		limit,
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var actions []model.Action
	for rows.Next() {
		var a model.Action
		if err := rows.Scan(&a.ID, &a.Seq, &a.Type, &a.Content, &a.Result, &a.ExitCode, &a.Timestamp); err != nil {
			return nil, err
		}
		actions = append(actions, a)
	}
	return actions, nil
}

func (d *DB) UpdateAction(action *model.Action) error {
	d.mu.Lock()
	defer d.mu.Unlock()

	_, err := d.conn.Exec(
		`UPDATE actions SET result=?, exit_code=? WHERE id=?`,
		action.Result, action.ExitCode, action.ID,
	)
	return err
}

func (d *DB) MarkSynced(ids []int64) error {
	if len(ids) == 0 {
		return nil
	}
	d.mu.Lock()
	defer d.mu.Unlock()

	query := "UPDATE actions SET synced=1 WHERE id IN ("
	args := make([]interface{}, len(ids))
	for i, id := range ids {
		if i > 0 {
			query += ","
		}
		query += "?"
		args[i] = id
	}
	query += ")"

	_, err := d.conn.Exec(query, args...)
	return err
}

func (d *DB) Close() error {
	return d.conn.Close()
}
