# onyourmark Radio — Podcast Archive

2020〜2022年に配信された全23エピソードのアーカイブ。SoundCloudから移行し、GitHub Pages + Releases でホスト。

## URLs

- **配信ページ**: https://artico-dev.github.io/onyourmark-radio/
- **RSSフィード**: https://artico-dev.github.io/onyourmark-radio/feed.xml
- **音声ファイル**: GitHub Releases (`v1.0` タグ) のアセット

## 構成

```
.
├── feed.xml                  # Apple Podcasts互換のRSS（自動生成）
├── index.html                # 一覧ページ（自動生成）
├── show-artwork.jpg          # 番組ジャケット (1400x1400)
├── thumbnails/ep##.jpg       # エピソード個別アートワーク
├── metadata/*.info.json      # yt-dlp由来の元メタデータ
├── audio/ep##.mp3            # ローカル保管（.gitignore で除外。Releases にアップ）
├── generate_feed.py          # RSS生成スクリプト
└── generate_index.py         # index.html生成スクリプト
```

## 再生成

エピソード追加や説明文修正時:

```bash
python3 generate_feed.py
python3 generate_index.py
git commit -am "update feed"
git push
```

新エピソードのMP3は GitHub Release `v1.0` にアセット追加（または新バージョンタグを切る）。

## 配信先設定

- **Apple Podcasts Connect**: feed URL を上記に差し替え
- **Spotify for Podcasters**: 同上
- 旧 SoundCloud は半年〜1年残してリスナー移行待ち推奨
