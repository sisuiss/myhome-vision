# CLAUDE.md — MyHome Vision 引き継ぎメモ

> このファイルは Claude Code / Cowork など、将来このリポジトリに入ってくる AI アシスタントが
> **ゼロから文脈に乗る** ためのメモです。人間の開発者も最初に読むと早いです。

---

## 1. プロダクト概要

**MyHome Vision** は、マンション購入検討客向けの AI 動画合成サービス。
モデルルームで撮影した家族写真を、事前制作した物件紹介動画に AI で合成し、
「この部屋で暮らす自分たちの未来」を接客中に視聴体験させる B2B サービスです。

- 顧客: マンションデベロッパー（モデルルーム運営者）
- 料金モデル: ¥40万/月 + 超過 ¥5,000/世帯
- エンドユーザー体験: モデルルームで写真撮影 → 8分以内に完成動画を視聴
- 根拠書類（docx/pdf）: リポジトリ外の `QLEA_AIComposite/` に格納
  - `01_企画書_MyHomeVision.{md,docx,pdf}` (v0.3)
  - `02_要件定義書_MyHomeVision.{md,docx,pdf}` (v0.3)
  - `03_機能仕様書_MyHomeVision.{md,docx,pdf}` (v0.3)
  - `04_ロードマップ_MyHomeVision.{md,docx,pdf}` (v0.3)
  - 旧版は `_old_20260421/` に退避済

---

## 2. 現在地（2026-04 時点）

**Phase 0 PoC** のコードスカフォールドを組んだ直後。
実機での ComfyUI 接続・外部 API 実呼び出し・実計測はこれから。

| Phase | 期間 | ステータス |
|-------|-----|---------|
| Phase 0 PoC | 4〜5週 | 🟢 **進行中（スカフォールド完了）** |
| Phase 1 MVP | 2.5〜3ヶ月 | 未着手 |
| Phase 2 Pilot | 1.5ヶ月 | 未着手 |
| Phase 3a V2 子供 | 3ヶ月 | 未着手（スコープ外） |
| Phase 3b V3 ペット | 2ヶ月 | 未着手（スコープ外） |
| Phase 4 本格展開 | 継続 | 未着手 |

### Phase 0 の Go/No-Go 指標（判定対象）

1. 夫婦2名の全身合成 表示成功率（Over-gen 2倍 + Quality-gate 後）**≥ 95%**
2. E2E 生成時間 **p95 ≤ 8分**（720p、Over-gen 2倍込み）
3. 1接客あたり AI 原価 **¥70〜¥150**
4. Viggle / Runway の API 可用性 **各 ≥ 99%**
5. Level 1 構成（国内完結）の E2E 動作確認

---

## 3. 決定済み設計方針（変えるな、変えるなら議事を残せ）

### 3.1 手法

- **モーション代役 × 全身 AI 生成**。Face Swap ではない。
  - 代役俳優が事前に演技した基礎動画 → 顧客顔＋体型特徴を条件に全身を再生成
  - 背景（物件内装）は base video の余白付きで固定

### 3.2 プロバイダー構成（4本立て）

| Provider | 同意レベル | 既定 | 役割 |
|---------|-----------|-----|------|
| **ComfyUI** | L1 / L2 / L3 | 有効 | **主軸**。MimicMotion + AnimateDiff。国内 / 自前 GPU |
| **Viggle** | L2 / L3 | 有効 | モーション転写の比較用・緊急フォールバック（US） |
| **Runway Act One** | L2 / L3 | 有効 | 比較・高品質バックアップ（US） |
| **Kling AI** | L3 のみ | **無効**（`KLING_ENABLED=false`） | Dark Launch。品質 A/B 用、顧客提供は未許可 |

優先順位: `["comfyui", "viggle", "runway_act_one", "kling"]`
（`backend/app/providers/registry.py` の `DEFAULT_PRIORITY`）

### 3.3 同意レベル

- **L1 国内完結**: 国内事業者のみ可（ComfyUI のみ）
- **L2 US 許可**: Viggle / Runway を追加
- **L3 全許可**: Kling 含む全て（ただし Kling は flag OFF）

### 3.4 品質・冗長化

- **Over-generation × 2**: 表示枚数 × 2 倍を生成
  （例: 接客で 4 枚見せる → 8 枚生成して品質通過分のみ）
- **Quality-gate 3軸**:
  - ArcFace（顔一致度） ≥ 0.65
  - Pose（姿勢妥当性） ≥ 0.70
  - Uncanny（不気味の谷） ≤ 0.30
  - **3/3 通過 → ACCEPT**、**2/3 → BORDERLINE（L4 人間レビュー送り）**、それ未満 → REJECT
- **Circuit Breaker**: プロバイダー単位で CLOSED / OPEN / HALF_OPEN
  - `error_rate_threshold = 0.2`、`window = 300s`、`cooldown = 600s`

### 3.5 5階層検出（L1〜L5）× 5段リカバリ（R1〜R5）

| 層 | 検出 | リカバリ |
|---|-----|---------|
| L1 | 事前チェック（同意・写真妥当性） | R1 自動リトライ（同プロバイダー） |
| L2 | 生成中モニタ（Circuit Breaker） | R2 プロバイダーフォールバック |
| L3 | 自動品質判定 | R3 人間レビュワー（L4 送り） |
| L4 | 人間レビュー | R4 営業介入（再撮影 / 別シーン提案） |
| L5 | 顧客フィードバック | R5 開発エスカレーション |

### 3.6 プライバシー

- **平文 PII を DB・ログに書かない**。`backend/app/core/anonymization.py` の
  `anonymize_id` (SHA256 + salt) / `anonymize_timestamp`（月精度まで落とす）を必ず経由
- **`failed_generations` テーブル**: 匿名化後のみ、保持期間 **730日（2年）**
- 新プロバイダーは **Feature Flag OFF デフォルト（Dark Launch）** で入れる

### 3.7 拡張 5 原則（V2/V3 を見越した設計）

1. `subjects[]` 配列スキーマ（現在は 2人固定だが配列は可変長前提）
2. ComfyUI ワークフローはパラメトリック（人数・年齢帯で分岐）
3. ベース動画は「人物スペース」に余白を持たせて収録
4. UI は N 人対応前提
5. 品質指標は N 人用に集約ロジックを持つ

---

## 4. コード構成（責務マップ）

```
myhome-vision/
├── backend/app/
│   ├── api/routes.py          # /health, /providers/status, POST /jobs, GET /jobs/{id}
│   ├── core/
│   │   ├── config.py          # Pydantic Settings（全環境変数をここで）
│   │   ├── anonymization.py   # PII 匿名化ユーティリティ
│   │   ├── circuit_breaker.py # スレッドセーフなプロバイダー単位 CB
│   │   └── logging.py         # structlog 設定
│   ├── models/schemas.py      # Subject, ConsentLevel, Scene, JobCreateRequest 等
│   ├── providers/
│   │   ├── base.py            # AIVideoProvider 抽象 + GenerateParams/Result 等
│   │   ├── registry.py        # DEFAULT_PRIORITY / eligible_for_level()
│   │   ├── comfyui.py         # 主軸プロバイダー（HTTP stub + real モード）
│   │   ├── viggle.py          # L2/L3
│   │   ├── runway.py          # L2/L3
│   │   └── kling.py           # L3 only、flag OFF で ProviderUnavailable
│   └── services/
│       ├── job_manager.py     # R1 リトライ + R2 フォールバック、CB 反映
│       ├── over_generation.py # calculate_total_attempts()
│       └── quality_gate.py    # judge() → ACCEPT / BORDERLINE / REJECT
├── comfyui/workflows/         # ComfyUI ワークフロー JSON（MimicMotion + AnimateDiff）
├── eval/                      # ArcFace / Pose / Uncanny スタブ + runner
├── tests/                     # pytest（5ファイル、まずスタブ前提で通る）
├── scripts/bootstrap.sh       # venv 作成 + 依存インストール
└── docs/
    ├── phase0_plan.md         # W1〜W5 詳細計画
    ├── comfyui_setup.md       # Runpod / SaladCloud / RunComfy 比較
    └── github_setup.md        # 初回 repo 設定手順（画面ポチポチ + gh CLI）
```

### 主要な抽象

- `AIVideoProvider`（抽象クラス）: `generate / poll / fetch / cancel` と
  `supports_consent_level(level)` を実装
- `GenerateParams` に `overgen_index` を渡す（同ジョブ内の複数試行を識別）
- 例外: `ProviderError`（再試行可能）/ `ProviderUnavailable`（リタイアして R2 へ）

---

## 5. 開発コマンド

```bash
# 初期化（一度だけ）
bash scripts/bootstrap.sh

# サーバー起動
cd backend && source .venv/bin/activate
uvicorn app.main:app --reload

# 疎通
curl http://localhost:8000/health
# 期待: {"status":"ok","providers":{"comfyui":"stub","viggle":"stub","runway":"stub","kling":"disabled"}}

# テスト
pytest tests -v

# Lint / Format
ruff check backend tests eval
ruff format --check backend tests eval

# 型チェック（Phase 0 は warn-only）
mypy backend/app
```

サンプルジョブ投入（スタブモード）:

```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"scene":"morning_coffee","consent_level":1,"subjects":[{"role":"adult","gender":"male","age_band":"40s"},{"role":"adult","gender":"female","age_band":"30s"}]}'
```

---

## 6. スコープ外（PR で追加しないこと）

Phase 0 では以下を **意図的に実装しない**。必要なら Issue を立てて Phase 1 以降に回す:

- 認証・認可（Phase 1 で Auth0 or 自前）
- 本番 DB / Alembic マイグレーション（Phase 0 は SQLite / in-memory）
- フロントエンド UI（接客 UI は Phase 1 Next.js で）
- 本番運用ダッシュボード（Phase 1/2）
- **子供 subject 対応**（Phase 3a 専用。Uncanny 閾値・プロンプト設計も別途）
- **ペット subject 対応**（Phase 3b 専用）

---

## 7. 次の一手（着手候補）

優先順位付き。迷ったら上から。

1. **GitHub へ初回 push**
   - すでに `git init` 済み、初回コミット `5db7688` 入り、remote origin 登録済
   - `cd myhome-vision && git push -u origin main`
   - push 後、`docs/github_setup.md` の手順で branch protection / Security / labels を設定
2. **Phase 0 W1 の Issue 起票**
   - `docs/phase0_plan.md` を読んで W1 のタスクを GitHub Issue に分解
   - ラベル: `phase-0` + 該当 `provider:*` / `priority-*`
3. **ComfyUI 実機接続（主軸プロバイダーの本実装）**
   - `backend/app/providers/comfyui.py` の stub モードを real モードに切替
   - `comfyui/workflows/morning_coffee_v0.json` をローカル ComfyUI で実行検証
   - MimicMotion ノードの LoRA / 量子化設定を決める
4. **ArcFace / OpenPose の実評価を結線**
   - `eval/*.py` は今スタブ（固定値を返す）。InsightFace / mediapipe を実装
   - `tests/` に評価パイプのユニットテストを足す
5. **Viggle / Runway の最小 API 呼び出し**
   - 有料 API キーを取得 → 1回だけ実呼び出しで所要時間・可用性を測る
   - Circuit Breaker の実動作を観測

---

## 8. このリポジトリにおける AI アシスタントへのお願い

- **平文 PII を絶対にコード例・テストデータ・ログに書かない**（顔写真・氏名・住所・電話）
- `failed_generations` に書く箇所を修正する時は匿名化経由を必ず確認
- 新プロバイダーを足す時は **Feature Flag OFF から始める**（Dark Launch 原則）
- 同意レベル（L1/L2/L3）のゲートを迂回する設計変更は事前相談
- Phase 3a/3b 機能（子供 / ペット）は Phase 0/1 中に混ぜない
- 「Face Swap で良くない？」は **No**（企画意図とリスク管理上の決定事項）
- コミットメッセージは Conventional Commits（`feat(scope): ...`）
- 主要な判断は `CONTRIBUTING.md` / `SECURITY.md` と整合させる

不明点は README → CONTRIBUTING → SECURITY → docs/ の順で当たってください。
