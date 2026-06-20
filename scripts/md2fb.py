#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
# Windows 終端機 UTF-8 輸出修正
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
"""
md2fb.py — Markdown -> Facebook 純文字轉換腳本
用法：python md2fb.py path/to/post/index.md
輸出：腳本所在目錄下，以輸入資料夾名稱命名的 .txt 檔
"""

import re
import sys
import os

# ─────────────────────────────────────────────
# LaTeX -> Unicode 替換字典（可自行擴充）
# ─────────────────────────────────────────────
LATEX_SYMBOLS = {
    # 集合論
    r"\subsetneq":      "⊊",
    r"\subseteq":       "⊆",
    r"\supseteq":       "⊇",
    r"\supsetneq":      "⊋",
    r"\subset":         "⊂",
    r"\supset":         "⊃",
    r"\in":             "∈",
    r"\notin":          "∉",
    r"\cup":            "∪",
    r"\cap":            "∩",
    r"\emptyset":       "∅",
    r"\varnothing":     "∅",
    # 數字與比較
    r"\infty":          "∞",
    r"\leq":            "≤",
    r"\geq":            "≥",
    r"\le":             "≤",
    r"\ge":             "≥",
    r"\neq":            "≠",
    r"\ne":             "≠",
    r"\approx":         "≈",
    r"\equiv":          "≡",
    r"\sim":            "∼",
    r"\ll":             "≪",
    r"\gg":             "≫",
    # 算術
    r"\times":          "×",
    r"\cdot":           "·",
    r"\div":            "÷",
    r"\pm":             "±",
    r"\mp":             "∓",
    # 箭頭
    r"\to":             "→",
    r"\rightarrow":     "→",
    r"\leftarrow":      "←",
    r"\Rightarrow":     "⇒",
    r"\Leftarrow":      "⇐",
    r"\Leftrightarrow": "⟺",
    r"\leftrightarrow": "↔",
    # 邏輯
    r"\forall":         "∀",
    r"\exists":         "∃",
    r"\nexists":        "∄",
    r"\neg":            "¬",
    r"\lnot":           "¬",
    r"\land":           "∧",
    r"\lor":            "∨",
    r"\oplus":          "⊕",
    # 根號與積分
    r"\sqrt":           "√",
    r"\int":            "∫",
    r"\sum":            "∑",
    r"\prod":           "∏",
    # 函數名稱（移除反斜線）
    r"\log":            "log",
    r"\ln":             "ln",
    r"\sin":            "sin",
    r"\cos":            "cos",
    r"\tan":            "tan",
    r"\exp":            "exp",
    r"\max":            "max",
    r"\min":            "min",
    r"\gcd":            "gcd",
    r"\lcm":            "lcm",
    r"\lim":            "lim",
    r"\sup":            "sup",
    r"\inf":            "inf",
    r"\det":            "det",
    # 希臘字母（小寫）
    r"\alpha":          "α",
    r"\beta":           "β",
    r"\gamma":          "γ",
    r"\delta":          "δ",
    r"\epsilon":        "ε",
    r"\varepsilon":     "ε",
    r"\zeta":           "ζ",
    r"\eta":            "η",
    r"\theta":          "θ",
    r"\iota":           "ι",
    r"\kappa":          "κ",
    r"\lambda":         "λ",
    r"\mu":             "μ",
    r"\nu":             "ν",
    r"\xi":             "ξ",
    r"\pi":             "π",
    r"\rho":            "ρ",
    r"\sigma":          "σ",
    r"\tau":            "τ",
    r"\upsilon":        "υ",
    r"\phi":            "φ",
    r"\varphi":         "φ",
    r"\chi":            "χ",
    r"\psi":            "ψ",
    r"\omega":          "ω",
    # 希臘字母（大寫）
    r"\Gamma":          "Γ",
    r"\Delta":          "Δ",
    r"\Theta":          "Θ",
    r"\Lambda":         "Λ",
    r"\Xi":             "Ξ",
    r"\Pi":             "Π",
    r"\Sigma":          "Σ",
    r"\Phi":            "Φ",
    r"\Psi":            "Ψ",
    r"\Omega":          "Ω",
    # 其他常用
    r"\ldots":          "…",
    r"\cdots":          "⋯",
    r"\vdots":          "⋮",
    r"\ddots":          "⋱",
    r"\partial":        "∂",
    r"\nabla":          "∇",
    r"\perp":           "⊥",
    r"\parallel":       "∥",
    r"\angle":          "∠",
    r"\prime":          "′",
    r"\mathbb{R}":      "ℝ",
    r"\mathbb{N}":      "ℕ",
    r"\mathbb{Z}":      "ℤ",
    r"\mathbb{Q}":      "ℚ",
    r"\mathbb{C}":      "ℂ",
}

# 上標 Unicode 映射（數字 0-9 及部分符號）
SUPERSCRIPT_MAP = str.maketrans("0123456789+-=()", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾")

# 下標 Unicode 映射（數字 0-9 及部分符號）
SUBSCRIPT_MAP = str.maketrans("0123456789+-=()", "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎")

# 階層標題
HEADING_L1 = ["壹", "貳", "參", "肆", "伍", "陸", "柒", "捌", "玖", "拾"]
HEADING_L2 = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
ROMAN_L4   = ["Ⅰ", "Ⅱ", "Ⅲ", "Ⅳ", "Ⅴ", "Ⅵ", "Ⅶ", "Ⅷ", "Ⅸ", "Ⅹ",
               "Ⅺ", "Ⅻ"]


def strip_front_matter(text):
    """移除 YAML front matter，回傳 (標題或None, 正文)"""
    title = None
    fm_pattern = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
    m = fm_pattern.match(text)
    if m:
        fm_block = m.group(1)
        title_m = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', fm_block, re.MULTILINE)
        if title_m:
            title = title_m.group(1).strip().strip('"\'')
        text = text[m.end():]
    return title, text


def replace_mermaid(text, warnings):
    """將 ```mermaid ... ``` 整段替換為佔位符"""
    pattern = re.compile(r"```mermaid\r?\n.*?```", re.DOTALL)
    count = len(pattern.findall(text))
    if count:
        warnings.append(f"[!]  發現 {count} 個 Mermaid 圖表佔位，請手動替換為圖片後上傳")
    return pattern.sub("【圖表佔位：此處原有一段 Mermaid 流程圖，請手動替換成圖片】", text)


def replace_code_blocks(text, warnings):
    """將 ```lang ... ``` 的一般程式碼區塊替換為佔位符"""
    pattern = re.compile(r"```[^\n]*\r?\n.*?```", re.DOTALL)
    count = len(pattern.findall(text))
    if count:
        warnings.append(f"[!]  發現 {count} 個程式碼區塊佔位，請手動決定是否保留或改寫")
    return pattern.sub("【程式碼佔位：此處原有一段程式碼，請手動決定是否保留或改寫為純文字】", text)


def _to_superscript(s):
    try:
        return s.translate(SUPERSCRIPT_MAP)
    except Exception:
        return s


def _to_subscript(s):
    try:
        return s.translate(SUBSCRIPT_MAP)
    except Exception:
        return s


def replace_latex(text, warnings):
    """LaTeX 指令、上下標 -> Unicode，然後移除 $ 定界符"""
    # 先處理帶大括號的容器指令（順序很重要：先處理 \mathbb 等需要保留內容的）
    text = re.sub(r"\\boxed\{([^}]*)\}",        r"\1", text)
    text = re.sub(r"\\mathbf\{([^}]*)\}",       r"\1", text)
    text = re.sub(r"\\mathcal\{([^}]*)\}",      r"\1", text)
    text = re.sub(r"\\text\{([^}]*)\}",         r"\1", text)
    text = re.sub(r"\\mathrm\{([^}]*)\}",       r"\1", text)
    text = re.sub(r"\\operatorname\{([^}]*)\}",  r"\1", text)

    # 逐一替換 LATEX_SYMBOLS（由長到短排序）
    for cmd, unicode_char in sorted(LATEX_SYMBOLS.items(), key=lambda x: -len(x[0])):
        text = text.replace(cmd, unicode_char)

    # 上標 ^{多字元}
    text = re.sub(r"\^\{([0-9+\-=()\s]+)\}",
                  lambda m: _to_superscript(m.group(1).replace(" ", "")), text)
    # 上標 ^單字元
    text = re.sub(r"\^([0-9])",
                  lambda m: _to_superscript(m.group(1)), text)
    # 下標 _{多字元}
    text = re.sub(r"_\{([0-9+\-=()\s]+)\}",
                  lambda m: _to_subscript(m.group(1).replace(" ", "")), text)
    # 下標 _單字元（僅數字）
    text = re.sub(r"_([0-9])",
                  lambda m: _to_subscript(m.group(1)), text)

    # 偵測殘留的 \command 並標記
    residual = re.findall(r"\\[a-zA-Z]+", text)
    if residual:
        unique_residual = sorted(set(residual))
        warnings.append(
            "[!]  發現 {} 個無法自動轉換的 LaTeX 指令，已加【待處理】標記：{}".format(
                len(residual), ", ".join(unique_residual[:10])
            )
        )
        text = re.sub(r"\\[a-zA-Z]+", lambda m: "【待處理LaTeX：{}】".format(m.group(0)), text)

    # 移除 $$ 和 $ 定界符
    text = re.sub(r"\$\$(.*?)\$\$", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"\$([^$\n]+?)\$", r"\1", text)

    return text


def extract_links(text, warnings):
    """將 Markdown 連結轉為 顯示文字[N]，並蒐集腳注"""
    refs = []
    counter = [0]

    def replacer(m):
        display = m.group(1)
        target  = m.group(2).strip()
        counter[0] += 1
        refs.append((counter[0], target))
        return "{}[{}]".format(display, counter[0])

    pattern = re.compile(r"\[([^\[\]]+?)\]\(([^)]+?)\)")
    text = pattern.sub(replacer, text)

    if refs:
        warnings.append("[i]  共收錄 {} 個連結為腳注，請在文末確認".format(len(refs)))
    return text, refs


def replace_images(text, warnings):
    """將 ![alt](src) 替換為佔位符"""
    pattern = re.compile(r"!\[([^\]]*)\]\([^)]*\)")
    count = len(pattern.findall(text))
    if count:
        warnings.append("[!]  發現 {} 張圖片佔位，請手動插入圖片後上傳".format(count))

    def replacer(m):
        alt = m.group(1) or "（無說明）"
        return "【圖片佔位：此處原有圖片「{}」，請手動插入圖片】".format(alt)

    return pattern.sub(replacer, text)


def convert_headings(text):
    """
    #    -> 壹/貳/參...
    ##   -> 一、二、三...
    ###  -> （1）/（2）...
    #### -> （Ⅰ）/（Ⅱ）...
    """
    counters = {1: 0, 2: 0, 3: 0, 4: 0}
    lines = text.split("\n")
    result = []

    for line in lines:
        m4 = re.match(r"^####\s+(.*)", line)
        m3 = re.match(r"^###\s+(.*)",  line)
        m2 = re.match(r"^##\s+(.*)",   line)
        m1 = re.match(r"^#\s+(.*)",    line)

        if m4:
            counters[4] += 1
            idx = counters[4] - 1
            num = ROMAN_L4[idx] if idx < len(ROMAN_L4) else str(counters[4])
            result.append("（{}）{}".format(num, m4.group(1)))
        elif m3:
            counters[3] += 1
            counters[4] = 0
            result.append("（{}）{}".format(counters[3], m3.group(1)))
        elif m2:
            counters[2] += 1
            counters[3] = 0
            counters[4] = 0
            idx = counters[2] - 1
            num = HEADING_L2[idx] if idx < len(HEADING_L2) else str(counters[2])
            result.append("{}、{}".format(num, m2.group(1)))
        elif m1:
            counters[1] += 1
            counters[2] = 0
            counters[3] = 0
            counters[4] = 0
            idx = counters[1] - 1
            num = HEADING_L1[idx] if idx < len(HEADING_L1) else str(counters[1])
            result.append("{}、{}".format(num, m1.group(1)))
        else:
            result.append(line)

    return "\n".join(result)


def clean_emphasis(text):
    """移除 **粗體**、*斜體*、`行內程式碼` 的標記符號"""
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"\*\*(.+?)\*\*",     r"\1", text, flags=re.DOTALL)
    text = re.sub(r"\*(.+?)\*",         r"\1", text, flags=re.DOTALL)
    text = re.sub(r"__(.+?)__",         r"\1", text, flags=re.DOTALL)
    text = re.sub(r"_([^_\s].*?[^_\s])_", r"\1", text)
    text = re.sub(r"`([^`]+)`",         r"\1", text)
    return text


def replace_shortcodes(text, warnings):
    """移除殘留的 {{< ... >}} shortcode"""
    pattern = re.compile(r"\{\{<.*?>}}", re.DOTALL)
    count = len(pattern.findall(text))
    if count:
        warnings.append("[!]  發現 {} 個殘留 Hugo shortcode，已加佔位符，請手動處理".format(count))
    def replacer(m):
        return "【Hugo shortcode 佔位：{}】".format(m.group(0).strip())
    return pattern.sub(replacer, text)


def clean_blockquotes(text):
    """移除 > [!NOTE] 等 Alert 標記行，其餘引用移除 > 前綴"""
    lines = text.split("\n")
    result = []
    for line in lines:
        alert_m = re.match(r"^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*$", line, re.IGNORECASE)
        if alert_m:
            continue
        bq_m = re.match(r"^>\s?(.*)", line)
        if bq_m:
            result.append(bq_m.group(1))
        else:
            result.append(line)
    return "\n".join(result)


def clean_hr(text):
    """--- / *** / ___ -> Unicode 分隔線"""
    return re.sub(r"^(\-{3,}|\*{3,}|_{3,})\s*$", "━━━━━━━━━━━━━━━━━━━━━━", text, flags=re.MULTILINE)


def convert_lists(text):
    """無序清單 - / * -> ・；有序清單保留"""
    lines = text.split("\n")
    result = []
    for line in lines:
        m = re.match(r"^(\s*)[*\-]\s+(.*)", line)
        if m:
            result.append("{}・{}".format(m.group(1), m.group(2)))
        else:
            result.append(line)
    return "\n".join(result)


def clean_whitespace(text):
    """統一換行符，壓縮連續空行（最多保留 1 個空行）"""
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def append_footnotes(text, refs):
    """在文章末尾附加參考資料腳注"""
    if not refs:
        return text
    lines = ["", "", "━━━━━━━━━━━━━━━━━━━━━━", "參考資料", ""]
    for n, target in refs:
        lines.append("[{}] {}".format(n, target))
    return text + "\n".join(lines)


def convert(input_path):
    warnings = []

    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    title, text = strip_front_matter(text)
    text = replace_mermaid(text, warnings)
    text = replace_code_blocks(text, warnings)
    text = replace_latex(text, warnings)
    text, refs = extract_links(text, warnings)
    text = replace_images(text, warnings)
    text = convert_headings(text)
    text = clean_emphasis(text)
    text = replace_shortcodes(text, warnings)
    text = clean_blockquotes(text)
    text = clean_hr(text)
    text = convert_lists(text)
    text = clean_whitespace(text)

    if title:
        text = "【{}】\n\n".format(title) + text

    text = append_footnotes(text, refs)
    return text, warnings


def main():
    if len(sys.argv) < 2:
        print("用法：python md2fb.py path/to/post/index.md")
        sys.exit(1)

    input_path = os.path.abspath(sys.argv[1])
    if not os.path.isfile(input_path):
        print("[ERROR] 找不到檔案：{}".format(input_path))
        sys.exit(1)

    folder_name = os.path.basename(os.path.dirname(input_path))
    if not folder_name:
        folder_name = os.path.splitext(os.path.basename(input_path))[0]
    script_dir  = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "{}_fb.txt".format(folder_name))

    text, warnings = convert(input_path)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    print("[OK] 轉換完成：{}".format(output_path))
    for w in warnings:
        print(w)


if __name__ == "__main__":
    main()
