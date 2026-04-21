#!/usr/bin/env bash
# prototype 環境を初期化するスクリプト
set -euo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"
cd "$HERE/backend"

echo "[1/3] Python venv 作成"
python3 -m venv .venv
source .venv/bin/activate

echo "[2/3] 依存関係インストール"
pip install --upgrade pip
pip install -r requirements.txt

echo "[3/3] .env 準備"
if [ ! -f .env ]; then
  cp .env.example .env
  echo ".env を作成しました。必要に応じて編集してください。"
fi

echo ""
echo "起動: cd backend && source .venv/bin/activate && uvicorn app.main:app --reload"
echo "疎通: curl http://localhost:8000/health"
