# Apple Podcasts / Spotify への移行手順

旧SoundCloud RSSから新GitHub Pages RSSへの切り替えガイド。

## 新フィードURL

```
https://artico-dev.github.io/onyourmark-radio/feed.xml
```

切り替え前に必ず https://castfeedvalidator.com/ で検証を通すこと。

---

## Apple Podcasts

### 既存リスナーを引き継ぐ「Change Feed URL」フロー

1. https://podcastsconnect.apple.com/ にログイン
2. 該当番組を選択
3. `Settings` → `Show URLs` の **New Feed URL** に新URLを入力
4. 旧feedからリダイレクトする方が確実だが、SoundCloudの旧feedは301を返せないので、Apple側の "New Feed URL" 機能だけで切替（24〜48hで反映）
5. 旧feedは半年〜1年は **削除しない**（Apple以外のクライアント、古いキャッシュへの保険）

### 注意点

- 番組タイトル・itunes:owner email・category などが旧feedと一致していないと別番組扱いされる可能性あり
- `guid` は旧SoundCloud feedと別形式 (`onyourmark-radio-{track_id}`) なので、エピソードは全件「新規」として扱われる恐れがある
  - 旧SoundCloud feedのguid形式を確認できれば、`generate_feed.py` の guid 生成ロジックを合わせることで重複を防げる

---

## Spotify (Spotify for Podcasters)

1. https://podcasters.spotify.com/ にログイン
2. 該当番組 → `Settings` → `Availability` → **RSS URL** を新URLに更新
3. Spotifyは比較的素直に切り替わる（Apple ほど厳密でない）

---

## 移行後チェックリスト

- [ ] castfeedvalidator.com でfeed.xml検証パス
- [ ] iTunes / Apple Podcasts アプリで新エピソードが従来通り見える
- [ ] Spotifyで番組ページが正常表示
- [ ] index.htmlのリンク先（Apple/Spotifyのリンク）を本番番組URLに差し替え
- [ ] 旧SoundCloud Pro契約のダウングレード判断（最低1年は維持を推奨）

---

## カスタムドメイン（オプション・将来）

将来のホスティング移行に備え、`podcast.onyourmark.jp` などのカスタムドメインを当てるのが理想:

1. DNSで `podcast` の CNAME → `artico-dev.github.io`
2. リポジトリの `CNAME` ファイルに `podcast.onyourmark.jp` を記載
3. `generate_feed.py` / `generate_index.py` の URL 定数を更新
4. Apple/Spotifyのfeed URLも新ドメインに変更

これをやっておくと、将来GitHubから別ホストに移すとき feed URL を変えずに済みリスナーを失わない。
