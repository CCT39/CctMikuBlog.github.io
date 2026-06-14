# CCT的咪苦筆記

這是一個使用 [Hugo](https://gohugo.io/) 與 [PaperMod](https://github.com/adityatelange/hugo-PaperMod) 主題建立的個人部落格，專門存放與初音未來及 VOCALOID 相關的硬核長文。

## 特色

- 深入的VOCALOID相關研究
- 歷史考據與數據分析文章
- 支援數學公式（LaTeX）

## 技術堆疊

- **靜態網站生成器**: Hugo
- **主題**: PaperMod
- **部署**: GitHub Pages
- **CI/CD**: GitHub Actions

## 專案結構

```
├── archetypes/          # Hugo 範本
├── assets/              # 資源檔案（CSS 等）
├── content/             # 文章內容
│   ├── posts/           # 部落格文章
│   ├── about.md         # 關於我頁面
│   ├── privacy.md       # 隱私權政策
├── layouts/             # Hugo 版面配置
├── public/              # 建構輸出（由 Hugo 生成）
├── themes/              # Hugo 主題
├── hugo.toml            # Hugo 設定檔
└── .github/workflows/   # GitHub Actions 設定
```

## 本機開發

### 前置需求

- [Hugo Extended](https://gohugo.io/getting-started/installing/) v0.163.1 或更新版本

### 啟動開發伺服器

```bash
hugo server -D
```

網站將在 `http://localhost:1313/` 啟動。

### 建構網站

```bash
hugo --minify
```

## 支持本專案

我們沒有放正式的斗內功能，但是歡迎私下斗內(#

## 致謝

本專案使用了以下優秀的開源資源：
- **[霞鶩文楷 TC](https://github.com/lxgw/LxgwWenkaiTC)** by [lxgw](https://github.com/lxgw) - 優雅的開源中文字型

## 授權條款

本站圖文內容除另有標示外，均採用 [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/deed.zh_TW) 授權條款。

## 聯絡方式

- **GitHub**: [cct39](https://github.com/cct39)
- **X (Twitter)**: [@CCT_39](https://x.com/CCT_39)
- **Gmail**: cct3939@gmail.com
