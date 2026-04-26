# LIRIA AI Player Personas

AI人格に実プレイ風ログを生成させるための persona YAML を置く場所です。

既定では `kenji_style_player.yaml` が使われます。

```bash
bash scripts/run_ai_persona_playtest.sh session_kenji_ai_test_001 --turns 1000
```

別人格を使う場合:

```bash
bash scripts/run_ai_persona_playtest.sh session_ai_playtest_other --turns 8 --persona personas/other_player.yaml
```

複数personaをまとめて試走する場合:

```bash
bash scripts/run_ai_player_harness.sh --config tests/ai_player_harness/sample.yaml --turns 8
```

この runner は persona YAML を厳密にパースせず、Codex CLI に渡すプレイヤー人格テキストとして読み込みます。形式を増やす場合も、人間が読みやすい `summary`, `voice`, `romance`, `crisis`, `turn_policy`, `do_not` のような塊に分けると調整しやすくなります。
