# t2ai MVP Monorepo

FastAPI (uv) + React/TypeScript (Vite) のローカルMVP用モノレポです。

## 必要ツール
- Python 3.11+（3.12推奨）
- uv
- Node.js LTS

## 起動手順
バックエンドとフロントエンドを同時に起動します。

```bash
make dev
```

個別に起動したい場合は以下を使います。

```bash
make dev-backend
make dev-frontend
```

## 使用ポート
- Backend: http://localhost:8000
- Frontend: http://localhost:5173

## 疎通確認
バックエンドのヘルスチェック:

```bash
curl http://localhost:8000/health
```

フロントエンドにアクセスして以下が表示されればOKです。
- Frontend OK
- Backend health: ok（またはエラー内容）
