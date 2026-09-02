import sqlite3
import os
from typing import Dict, Any

DB_PATH = "dictionary.db"

def init_db():
    """データベースおよび必要なテーブルの初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 注文・約定ログテーブル
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trade_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            pair TEXT NOT NULL,
            style TEXT NOT NULL,
            side TEXT NOT NULL,
            entry_price REAL NOT NULL,
            stop_loss REAL NOT NULL,
            take_profit REAL NOT NULL,
            rr_ratio REAL NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    
    # システムエラー・例外ログテーブル
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            level TEXT NOT NULL,
            message TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def log_trade(order_plan: Dict[str, Any]):
    """発注プラン・約定データを記録"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO trade_logs (timestamp, pair, style, side, entry_price, stop_loss, take_profit, rr_ratio, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        order_plan['timestamp'],
        order_plan['pair'],
        order_plan['style'],
        order_plan['side'],
        order_plan['entry_price'],
        order_plan['stop_loss'],
        order_plan['take_profit'],
        order_plan['rr_ratio'],
        order_plan['status']
    ))
    conn.commit()
    conn.close()

def log_system(level: str, message: str, timestamp: str):
    """システムログ・例外エラーを記録"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO system_logs (timestamp, level, message)
        VALUES (?, ?, ?)
    ''', (timestamp, level, message))
    conn.commit()
    conn.close()
