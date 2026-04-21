# MyHome Vision

AI動画合成による住空間（マンション）未来体験サービス。モデルルームで撮影した家族写真を、事前制作した物件紹介動画にAIで合成し、「この部屋で暮らす自分たちの未来」を購入検討客に体験してもらうサービスです。

本リポジトリは **Phase 0 PoC** から順次、MVP（Phase 1）→ パイロット（Phase 2）→ V2/V3 拡張（Phase 3a/3b）→ 本格展開（Phase 4）まで育てていく、プロダクト全体のモノレポです。

実装は `01_企画書` / `02_要件定義書` / `03_機能仕様書` / `04_ロードマップ` (v0.3) に基づき、**モーション代役×全身AI生成** パイプラインを **ComfyUI 主軸＋Viggle / Runway Act One / Kling AI (Dark Launch)** の4プロバイダー体制で構築します。

## Phase 0 の Go/No-Go 判定材料

1. 夫婦2名の全身合成 表示成功率（Over-generation 2倍・Quality-gate 後）≥ 95%
2. E2E生成時間 p95 ≤ 8分（720p、Over-gen 2倍）
3. 1接客あたりAI原価 ¥70〜¥150 以内
4. Viggle / Runway の API可用性 それぞれ 99% 以上
5. Level 1 構成（国内完結）のE2E 動作確認

## ディレクトリ構成（モノレポ）

```
myhome-vision/
├── backend/              # FastAPI バックエンド（Phase 0 は最小構成、Phase 1 以降で拡張）
│   └── app/
│       ├── api/          # HTTP エンドポイント
│       ├── core/         # 設定・共通ユーティリティ・Circuit Breaker / feature_flag
│       ├── models/       # データモデル（Pydantic / SQLAlchemy）
│       ├── providers/    # AIVideoProvider 抽象＋4プロバイダー実装
│       └── services/     # ジョブ管理・Over-gen / Quality-gate ロジック
├── comfyui/              # ComfyUI ワークフロー（JSON）と接続スクリプト
│   └── workflows/
├── eval/                 # ArcFace / OpenPose などの品質評価スクリプト
├── scripts/              # セットアップ・運用スクリプト
├── tests/                # pytest
├── docs/                 # 設計・運用メモ（Phase別のプラン、ComfyUI構築手順等）
└── .github/              # CI / Issue / PR テンプレート
```

企画書・要件定義書・機能仕様書・ロードマップ（v0.3）の本体（docx / pdf）は別途社内共有の `QLEA_AIComposite/` に配置されています。追って本リポジトリの `docs/specs/` へ移送予定です。

## クイックスタート（ローカル開発）

### 前提
- Python 3.11+
- （任意）Docker / Docker Compose
- （任意）ComfyUI ローカル or Runpod Serverless アカウント

### セットアップ
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

もしくは同梱のブートストラップスクリプト:
```bash
bash scripts/bootstrap.sh
```

### 疎通確認
```bash
curl http://localhost:8000/health
# {"status":"ok","providers":{"comfyui":"stub","viggle":"stub","runway":"stub","kling":"disabled"}}
```

### サンプルジョブ投入（スタブ）
```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"scene":"morning_coffee","consent_level":1,"subjects":[{"role":"adult","gender":"male","age_band":"40s"},{"role":"adult","gender":"female","age_band":"30s"}]}'
```

### テスト実行
```bash
cd backend && source .venv/bin/activate
pytest ../tests -v
```

## ロードマップ（概要）

| Phase | 期間 | 目的 | 主なスコープ |
|-------|-----|------|------------|
| Phase 0 | 4〜5週 | Go/No-Go 判定 | 4プロバイダー評価・ComfyUI 基本パイプライン・品質ゲート |
| Phase 1 | 2.5〜3ヶ月 | MVP | 夫婦2名・4シーン・B2B パイロット契約可能レベル |
| Phase 2 | 1.5ヶ月 | パイロット運用 | 実モデルルーム投入・運用ログ収集 |
| Phase 3a | 3ヶ月 | V2 拡張 | 子供 subject 追加 |
| Phase 3b | 2ヶ月 | V3 拡張 | ペット subject 追加 |
| Phase 4 | 継続 | 本格展開 | 複数物件・複数デベロッパー対応 |

詳細は `docs/phase0_plan.md` を参照。ComfyUI 環境構築（Runpod Serverless / SaladCloud / RunComfy 比較）は `docs/comfyui_setup.md` を参照。

## 主要設計原則

- **モーション代役×全身AI生成**（Face Swap ではない）
- **Over-generation + Quality-gated Display**（2倍生成して品質通過分のみ表示）
- **5階層検出（L1〜L5）** × **5段階リカバリ（R1〜R5）**
- **同意レベル L1（国内）/ L2（US 許可）/ L3（全許可）**
- **Dark Launch**（Kling AI は `KLING_ENABLED=false` 既定）
- **拡張5原則**（subjects[] 配列 / パラメトリックワークフロー / 余白付きベース動画 / N人UI / N人品質指標）

## ライセンス

社内／関係者限定。詳細は `LICENSE` を参照。外部プロバイダー連携コードはフィーチャーフラグで個別にON/OFF可能です。

## セキュリティ / 貢献

- セキュリティ上の問題を見つけた場合は `SECURITY.md` を参照の上、非公開で報告してください。
- 開発フロー・ブランチ戦略・レビュー手順は `CONTRIBUTING.md` を参照してください。
