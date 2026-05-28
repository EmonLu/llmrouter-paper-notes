# 论文自动精读工作流

这个仓库现在提供一个最小自动化入口：

- 你给我一篇 PDF，或者一个 arXiv 链接
- 我先用脚本把它纳入仓库
- 自动生成对应的 `papers/<scope>-<turn-type>-<artifact-type>-<id>-<slug>.md` 骨架
- 自动抽取 `pdftotext` 文本到 `.tmp_pdftext/`
- 同步更新 `papers-manifest.json`、`reading-queue.md`、`LOCAL_PDF_INDEX.md`
- 然后再让 Hermes 按当前高强度模板继续补全内容

## 1. 脚本入口

仓库根目录下：

`auto_generate_paper_note.py`

## 2. 典型用法

把一个新 PDF 复制进仓库并生成笔记骨架：

`python3 auto_generate_paper_note.py /绝对路径/你的论文.pdf --copy`

如果直接给 arXiv abs 链接：

`python3 auto_generate_paper_note.py https://arxiv.org/abs/2601.17814 --copy --scope multimodal --turn-type single-turn --artifact-type benchmark`

如果直接给 arXiv pdf 链接：

`python3 auto_generate_paper_note.py https://arxiv.org/pdf/2601.17814.pdf --copy --scope multimodal --turn-type single-turn --artifact-type benchmark`

如果你已经把 PDF 放进仓库里，也可以直接：

`python3 auto_generate_paper_note.py pdfs/general-single-turn-method-2606.12345-some-paper.pdf`

如果标题识别不准，可以手动指定：

`python3 auto_generate_paper_note.py /绝对路径/paper.pdf --copy --scope multimodal --turn-type single-turn --artifact-type benchmark --paper-id 2606.12345 --title "Some Paper Title" --slug some-paper`

## 2.1 命名维度

- scope 可选值：`general` / `coding-agentic` / `multimodal`
- turn-type 可选值：`single-turn` / `multi-turn`
- artifact-type 可选值：`method` / `dataset` / `benchmark` / `survey` / `repo`

## 3. 脚本会做什么

1. 如果输入是 arXiv `abs` / `pdf` 链接，先自动下载 PDF（`abs` 会自动转成对应 `pdf`）
2. 尝试从文件名或链接中推断 `paper_id`
3. 用 `pdftotext` 抽取前两页，粗略推断标题
4. 结合 `scope / turn-type / artifact-type` 生成统一前缀
5. 生成：
   - `papers/<scope>-<turn-type>-<artifact-type>-<paper_id>-<slug>.md`
   - `.tmp_pdftext/<scope>-<turn-type>-<artifact-type>-<paper_id>-<slug>.txt`
6. 若传了 `--copy`，把 PDF 复制进 `pdfs/`
7. 若能识别 `paper_id`，同步更新：
   - `papers-manifest.json`
   - `reading-queue.md`
   - `LOCAL_PDF_INDEX.md`

## 4. 当前自动化边界

这个脚本现在是“自动建档 + 自动抽取 + 自动建骨架”，不是“一步到位替你写完整精读”。

原因是高质量精读仍需要：
- 补 appendix 表
- 核开源链接
- 判断数据开放状态
- 清理不确定表述
- 做面向 agentic router 的系统设计映射

这些步骤仍建议继续由 Hermes 接着完成。

## 5. 推荐配套使用方式

先运行：

`python3 auto_generate_paper_note.py /path/to/paper.pdf --copy`

然后对 Hermes 说：

`请继续按仓库当前高强度标准精读 papers/<新文件>.md，并补 appendix / 开源链接 / 数据开放状态，然后清理待补字段。`

## 6. 后续可以再升级的方向

如果你要把这件事做成更彻底的自动流程，下一步可以继续加：

1. 自动调用 arXiv API 拉 metadata
2. 自动抓 arXiv abs / html 页提取 GitHub / HF / project 链接
3. 自动在生成初稿后跑 leftover scan
4. 自动把完成的论文移动到 README / reading-queue 的“已读/已完成二轮精修”区域
5. 再包一个 shell 命令，例如：
   - `./ingest-paper /path/to/paper.pdf`

## 7. 注意事项

- `.tmp_pdftext/` 只是中间产物，commit 前应清理
- 标题自动识别只是粗略启发式，不保证完全正确
- 老论文 / 扫描版 PDF 的抽取质量可能较差
- 若没有 arXiv id，脚本仍能生成 note，但不会完整更新索引字段
