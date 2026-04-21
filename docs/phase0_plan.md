# Phase 0 PoC 実行計画（W1〜W5）

04_ロードマップ v0.3 §3.0 を実装観点で具体化したもの。

## 目的再掲

1. 夫婦2名の全身合成 表示成功率 ≥ 95%（Over-gen 2倍 Quality-gate 後）
2. E2E 生成時間 p95 ≤ 8分（720p）
3. 1接客AI原価 ¥70〜¥150
4. Viggle / Runway API 可用性 ≥ 99%
5. Level 1（国内完結）E2E 動作

## Go/No-Go 判定メトリクス（PoC 終了時）

| 指標 | Go基準 |
|---|---|
| 最終表示人手評価 | 平均 7.0以上 |
| 夫婦一貫性（パターン間別人率） | ≤ 20% |
| 顧客視点表示成功率 | 100% |
| Pattern A 時間 p95 | ≤ 6分 |
| 全4パターン時間 p95 | ≤ 12分 |
| 1接客コスト | ¥70〜150 |
| R1-R5 動作 | 全段階確認 |

## 週次スケジュール

### W1: 環境構築・素材収集
- ComfyUI のセットアップ（自社GPU or 管理GPU 比較）
- MimicMotion / AnimateDiff / CatVTON の動作確認
- 代役モーション素材（3〜5本）を撮影 or 収集
- 試作ベース動画（「朝のコーヒー」720p）を制作
- 評価被写体（夫婦5組）の標準写真セット準備
- バックエンド scaffold（本リポジトリ）の起動確認

### W2: プロバイダー品質評価
- Exp-1: ComfyUI / Viggle / Runway Act One / Kling（Dark Launch 評価だけ実施）
- 被写体5ペア × シーン3 = 15本/プロバイダー を生成
- `eval/runner.py` で ArcFace / Pose / Uncanny スコア取得
- 人手評価（10段階×5項目）を実施し PoC DB に集約
- **成果物**: `docs/reports/exp1_provider_quality.md`

### W3: 一貫性・時間計測
- Exp-2: 夫婦一貫性（Over-gen 2倍 での Quality-gate 通過率）
- Exp-3: 生成時間ベンチマーク（Pattern A 単独 / 4パターン並列 / 3組同時ピーク）
- プログレッシブ配信（WebSocket）の動作確認
- **成果物**: `docs/reports/exp2_consistency.md`, `docs/reports/exp3_timing.md`

### W4: コスト・リカバリー・エッジケース
- Exp-4: コスト実測（Runpod Serverless / SaladCloud / RunComfy 比較、Provider 請求）
- Exp-5: R1-R5 リカバリー動作検証（API 500 注入、Circuit Breaker 発火、L4 レビュー、F-15 Couple Generic、F-16 48h Email）
- Exp-6: エッジケース（高齢者、眼鏡、多人種、暗所写真）
- **成果物**: `docs/reports/exp4_cost.md`, `docs/reports/exp5_recovery.md`, `docs/reports/exp6_edge.md`

### W5: E2E統合・総括
- Exp-7: iPad 実機 + 本番相当バックエンドで 10連続セッション
- Level 1/2/3 切替動作確認
- Kling Dark Launch フラグ動作確認（OFF 状態で priority から消えていること、ON で登場すること）
- Go/No-Go 判定書作成、推奨構成書、PoC 総括レポート
- **成果物**: `docs/reports/poc_summary.md`, `docs/reports/recommended_stack.md`, `docs/reports/go_nogo.md`

## リスクと緩和

| リスク | 緩和策 |
|---|---|
| ComfyUI の運用が複雑 | Runpod Serverless を W1 早期に試す |
| 代役モーション素材不足 | PoC では既存のMocapライブラリ（Mixamo 等）を併用 |
| ArcFace が日本人顔で弱い | InsightFace の buffalo_l → antelopev2 も併用 |
| GPU コスト超過 | Spot / Preemptible GPU、720p 維持、Over-gen 比率を動的調整 |
| Kling Dark Launch の誤発火 | feature_flag を CI で検査、Level 3 でのみ priority 入り |
