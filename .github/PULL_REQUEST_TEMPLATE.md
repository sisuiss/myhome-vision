# PR 概要

<!-- 何を、なぜ変えたかを1〜3文で -->

## 種別
- [ ] バグ修正
- [ ] 機能追加
- [ ] リファクタ
- [ ] ドキュメント
- [ ] CI / インフラ
- [ ] 依存ライブラリ更新

## 関連 Issue / 仕様

- Closes #
- 仕様参照: `03_機能仕様書 vX.X §X.X` / `04_ロードマップ vX.X Phase X`

## 変更点

-
-

## 動作確認

- [ ] `pytest tests -v` が通る
- [ ] `ruff check` が通る
- [ ] `ruff format --check` が通る
- [ ] （該当する場合）手動で `/health` / `/jobs` を叩いた
- [ ] （該当する場合）ComfyUI ワークフローJSONを validate した

## 影響範囲

- [ ] プロバイダー抽象（`backend/app/providers/`）
- [ ] Circuit Breaker（`backend/app/core/circuit_breaker.py`）
- [ ] Quality-gate / Over-generation（`backend/app/services/`）
- [ ] Consent Level / feature_flag
- [ ] Infra / CI
- [ ] その他

## セキュリティ / プライバシー観点の確認

- [ ] 個人識別情報（顔画像・氏名・住所・電話番号）をログ／DBに平文で保存していない
- [ ] `failed_generations` に書く場合、匿名化ユーティリティ（`anonymize_id` / `anonymize_timestamp`）を経由している
- [ ] 新規の外部プロバイダー連携は feature_flag で off にできる
- [ ] 同意レベル（L1/L2/L3）の境界を壊していない

## 破壊的変更

- [ ] なし
- [ ] あり（詳細↓）

<!-- ある場合: 移行手順・古いAPIの扱い等を書く -->

## スクリーンショット / ログ
<!-- UI変更やリカバリ動作などあれば -->
