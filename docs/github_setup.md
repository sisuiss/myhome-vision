# GitHub 初回セットアップ手順

このリポジトリを GitHub (`https://github.com/sisuiss/myhome-vision`) に初めて push した直後に、
一度だけ実行する設定メモです。画面ポチポチ版と `gh` CLI 版を併記します。

---

## 0. 前提

- 初回 `git push -u origin main` 完了済
- Actions タブで **CI が 1 度は走り終わっている** こと
  （status check を「必須」に指定するプルダウンに `CI` が出てくるのは、1回走ってから）

### ⚠️ 共同開発者が増えるまでは `Required approvals = 0` にすること

1人開発の間に `Required approvals = 1` にすると、自分の PR を自分では承認できず
merge 不能になります。共同開発者が増えた時点で 1 に上げてください。

---

## 1. Branch protection for `main`

### UI 手順

1. リポジトリ → **Settings** タブ
2. 左メニュー **Code and automation** > **Branches**
3. **Add branch ruleset**（古い UI なら「Add rule」）
4. フォーム入力:
   - **Ruleset Name**: `protect-main`
   - **Enforcement status**: `Active`
   - **Target branches** → **Add target** → **Include by pattern** → `main`
   - **Rules**:
     - ✅ Restrict deletions
     - ✅ Block force pushes
     - ✅ Require a pull request before merging
       - Required approvals: **0**（1人の間）
       - ✅ Dismiss stale pull request approvals when new commits are pushed
     - ✅ Require status checks to pass
       - Add checks: `Lint & Test (Python 3.11)`, `Lint & Test (Python 3.12)`, `ComfyUI Workflow JSON validation`
       - ✅ Require branches to be up to date before merging
5. **Create** で確定

---

## 2. Code security and analysis

1. Settings → 左メニュー **Security** > **Code security and analysis**
2. 各行を **Enable** に:
   - Dependency graph
   - Dependabot alerts
   - Dependabot security updates
   - Secret scanning
   - Push protection（コミットに token/secret が混入した瞬間ブロック）
   - Private vulnerability reporting（`SECURITY.md` の報告経路）

保存ボタンは無し、トグル時点で反映。

---

## 3. Actions → Workflow permissions

1. Settings → **Actions** > **General**
2. 一番下 **Workflow permissions**
3. **Read and write permissions** を選択
4. ✅ Allow GitHub Actions to create and approve pull requests
5. **Save**

---

## 4. Issue ラベル作成

### 4.1 UI 手順

1. リポジトリ → **Issues** タブ → 右上 **Labels**（または URL 末尾 `/labels`）
2. **New label** で 1 個ずつ作成

### 4.2 gh CLI で一括作成（推奨）

ローカルで `gh auth login` 済なら、以下を丸ごと貼るだけ:

```bash
cd /path/to/myhome-vision

gh label create phase-0        --color 0E8A16 --description "PoC 期（Go/No-Go 判定）" --force
gh label create phase-1        --color 1D76DB --description "MVP（夫婦2名）" --force
gh label create phase-2        --color 5319E7 --description "パイロット運用" --force
gh label create phase-3a       --color B60205 --description "V2 子供対応" --force
gh label create phase-3b       --color D93F0B --description "V3 ペット対応" --force

gh label create priority-high  --color E11D21 --description "最優先" --force
gh label create priority-med   --color FBCA04 --description "中優先" --force
gh label create priority-low   --color C2E0C6 --description "余裕があれば" --force

gh label create discussion     --color CC317C --description "技術判断の相談" --force
gh label create privacy        --color 5319E7 --description "PII / 同意レベル" --force

gh label create provider:comfyui --color 0366D6 --description "ComfyUI 関連" --force
gh label create provider:viggle  --color 0366D6 --description "Viggle 関連" --force
gh label create provider:runway  --color 0366D6 --description "Runway Act One 関連" --force
gh label create provider:kling   --color 0366D6 --description "Kling AI (Dark Launch)" --force
```

`--force` は同名があっても色/説明を上書きする指定。

---

## 5. その他あとで

- **Repository description / topics** を設定
  - description: `AI video composition service for condominium buyers (MyHome Vision)`
  - topics: `ai`, `video-generation`, `comfyui`, `real-estate`, `fastapi`
- **Default branch** が `main` になっているか確認（`git init -b main` で作ってあるはず）
- 共同開発者が増えたら:
  - Branch protection の Required approvals を 1 に引き上げ
  - CODEOWNERS に追加（現状は全パス `@sisuiss`）
