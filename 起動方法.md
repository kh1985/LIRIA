# 起動方法

## プレイヤー向け最小手順

コマンドを覚える必要はありません。
プレイヤーは、Codex/GM に次のように自然文で言えば始められます。

- 「LIRIAを新規で始めて」
- 「前回の続きから再開して」
- 「この場面を漫画化したい」
- 「ヒロインPVを作りたい」
- 「この子の三面図がほしい」

CLI は Codex/GM 側が内部で使うため、プレイヤーが直接覚えるものではありません。
漫画化、ヒロインPV、三面図は、保存済みの Appearance Profile、Visual Character Sheet、Manga Export Candidates をもとに自然文で依頼できます。

## Codex/GM 側の内部コマンド

### 新規ゲーム

```bash
bash play.sh new
```

session 名を省略した `new` は、旧 `session_001` を避けるため、空の `saves/` でも `session_002` から自動採番します。

### 名前付きで新規 session 作成

```bash
bash play.sh new liria session_002
```

### 続きから再開、最新 session を自動選択

```bash
bash play.sh resume
```

### session 指定で再開

```bash
bash play.sh liria resume session_002
```

### Codex で再開

```bash
bash play.sh resume -codex
```

### session 一覧

```bash
bash play.sh list-sessions
```
