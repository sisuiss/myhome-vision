# Contributing — MyHome Vision

社内・関係者向けの開発ガイドです。Phase 0 PoC 期は少人数での開発を想定していますが、Phase 1 以降を見据えて、最初から以下のルールで進めます。

## ブランチ戦略

- `main` — 常にデプロイ可能。直 push 禁止、PR + レビュー + CI green が必須。
- `develop` — 次期リリース候補。Feature ブランチはここから切る。
- `feature/<topic>` — 機能開発（例: `feature/quality-gate-arcface`）
- `fix/<topic>` — バグ修正
- `infra/<topic>` — CI・Docker・スクリプト系
- `docs/<topic>` — ドキュメントのみ

## コミットメッセージ

Conventional Commits をゆるく採用します。

```
<type>(<scope>): <subject>

<body (optional)>
```

- type: `feat` / `fix` / `refactor` / `test` / `docs` / `chore` / `infra` / `perf`
- scope: `providers` / `quality-gate` / `circuit-breaker` / `comfyui` / `eval` / `api` / `infra` 等
- subject: 現在形・命令形・日本語 or 英語（どちらでも可、混ぜない）

例:
```
feat(providers): add Viggle v2 polling backoff
fix(quality-gate): handle None uncanny score as pass
```

## PR 作成の流れ

1. Issue があれば Issue にリンクする（`Closes #12` 等）
2. `.github/PULL_REQUEST_TEMPLATE.md` のチェックリストを埋める
3. 自分でローカル確認（下記）
4. CI green を確認してから Reviewer を割り当て
5. 1人以上のレビュー + CI green で merge 可

## ローカル確認（最低限）

```bash
# backend 起動確認
bash scripts/bootstrap.sh
uvicorn app.main:app --reload  # 別ターミナル
curl http://localhost:8000/health

# Lint / Format
ruff check backend tests eval
ruff format --check backend tests eval

# Type check
mypy backend/app

# Test
pytest tests -v
```

## コードスタイル

- Python 3.11+、`from __future__ import annotations` を基本使用
- Type hint 必須（`mypy` は Phase 0 warn-only → Phase 1 で strict 化予定）
- 公開関数・クラスには docstring（日本語可）
- プライベートは `_leading_underscore`
- 例外は握りつぶさない。プロバイダー系は `ProviderError` / `ProviderUnavailable` に統一

## プライバシー・セキュリティ原則（必読）

- **平文PIIをログ・DB・例外メッセージに絶対に書かない**
- `failed_generations` など失敗記録を書く場合は必ず
  `backend/app/core/anonymization.py` の `anonymize_id` / `anonymize_timestamp` を経由
- 外部プロバイダーに送るデータは、同意レベル（L1/L2/L3）のゲートを通ったものだけ
- 新規プロバイダー連携は **フィーチャーフラグでデフォルト OFF**（Dark Launch）

詳細は `SECURITY.md` を参照。

## PoC 期の「やらないこと」

以下は Phase 0 では意図的にスコープ外です。PR では追加しないでください（Issue 化して Phase 1 以降に回す）。

- 認証・認可（Phase 1 で Auth0 or 自前）
- 本番 DB / マイグレーション（Phase 0 は SQLite / in-memory）
- フロントエンド（接客 UI は Phase 1）
- 本番運用ダッシュボード（Phase 1/2）
- 子供 / ペット subject 対応（Phase 3a / 3b）

## 質問・相談

- 技術判断: GitHub Issue に `discussion` ラベルを付けて立てる
- セキュリティ案件: `SECURITY.md` の手順で非公開報告
