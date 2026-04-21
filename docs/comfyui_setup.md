# ComfyUI 環境構築ガイド（Phase 0 W1）

## 3つの管理GPU候補を比較する

| 選択肢 | 強み | 弱み | 想定月額（PoC 時） |
|---|---|---|---|
| **Runpod Serverless** | コールドスタート速い、従量課金、日本リージョンあり | 各ノード独立、state 持ち難い | ¥30,000〜60,000 |
| **SaladCloud** | GPU 単価が最安級 | Consumer GPU、SLA 弱め | ¥20,000〜40,000 |
| **RunComfy** | ComfyUI 専用マネージド、UI 提供 | カスタムノード追加に制限 | ¥40,000〜80,000 |
| 自社オンプレ | 原価最安、データ外部流出なし | 調達リードタイム、運用負担 | 初期 ¥100万+、運用 ¥20,000/月 |

Phase 0 W1 で少なくとも2つ（Runpod Serverless 必須、RunComfy 推奨）を評価し、Phase 1 までに1つに絞る。

## 必要なカスタムノード（PoC 時点の想定）

1. **MimicMotion** — 全身モーション転送（本PJの主役）
2. **AnimateDiff** — 時間軸の一貫性確保
3. **CatVTON** — 衣服・体型の整合
4. **ControlNet (OpenPose / DWPose)** — 骨格ガイド
5. **InsightFace (ArcFace)** — 評価用
6. **Video Helper Suite** — 動画 I/O

## ワークフロー JSON 配置

```
prototype/comfyui/workflows/
├── morning_coffee_v0.json       # 朝のコーヒー（PoC W1 雛形）
├── balcony_v0.json              # （W2 で追加）
├── living_day_v0.json           # （W2 で追加）
└── weekend_bedroom_v0.json      # （W2 で追加）
```

バックエンドからは `${BASE_VIDEO_PATH}` `${MOTION_REF_PATH}` `${SUBJECT_REFS}` `${SEED}` を
差し込んで `/prompt` エンドポイントに POST する。

## セキュリティ / Level 対応

- Level 1（国内完結）では Runpod の **日本リージョン** か自社GPU のみを選択
- Level 2/3 では米国リージョン許可、ただし `send_logs` に必ず記録
- 画像アップロードは全て S3 署名付きURL 経由、ComfyUI サーバーには平文保存しない
- API キーは .env に、本番は AWS Secrets Manager / GCP Secret Manager に移行

## W1 の完了条件

- [ ] Runpod Serverless 上で ComfyUI が起動し、`/prompt` が叩ける
- [ ] `morning_coffee_v0.json` でダミー被写体 1名の全身合成が 1本生成できる
- [ ] GPU 時間・コストの実測値が記録されている
- [ ] `prototype/backend` の `/health` が Runpod エンドポイントを向いた状態で green
