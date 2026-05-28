#!/usr/bin/env python3
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlretrieve

REPO_ROOT = Path(__file__).resolve().parent
PDF_DIR = REPO_ROOT / 'pdfs'
PAPERS_DIR = REPO_ROOT / 'papers'
TMP_DIR = REPO_ROOT / '.tmp_pdftext'
MANIFEST = REPO_ROOT / 'papers-manifest.json'
LOCAL_INDEX = REPO_ROOT / 'LOCAL_PDF_INDEX.md'
READING_QUEUE = REPO_ROOT / 'reading-queue.md'


def run(cmd):
    return subprocess.run(cmd, check=True, text=True, capture_output=True)


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = re.sub(r'-+', '-', text).strip('-')
    return text or 'paper'


def extract_arxiv_id(name: str) -> str | None:
    m = re.search(r'(\d{4}\.\d{4,5})(?:v\d+)?', name)
    return m.group(1) if m else None


def is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {'http', 'https'} and bool(parsed.netloc)


def normalize_arxiv_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.netloc not in {'arxiv.org', 'www.arxiv.org'}:
        return value
    paper_id = extract_arxiv_id(value)
    if not paper_id:
        return value
    return f'https://arxiv.org/pdf/{paper_id}.pdf'


def download_pdf(url: str) -> Path:
    normalized_url = normalize_arxiv_url(url)
    suffix = f"-{extract_arxiv_id(normalized_url)}.pdf" if extract_arxiv_id(normalized_url) else '.pdf'
    fd, tmp_path = tempfile.mkstemp(prefix='auto_generate_paper_note-', suffix=suffix)
    os.close(fd)
    tmp_file = Path(tmp_path)
    try:
        urlretrieve(normalized_url, tmp_file)
    except Exception:
        if tmp_file.exists():
            tmp_file.unlink()
        raise
    return tmp_file


def parse_args():
    p = argparse.ArgumentParser(description='根据本地 PDF 或 arXiv 链接生成论文精读 markdown 骨架与提取文本')
    p.add_argument('pdf', help='PDF 路径，或 arXiv abs/pdf 链接')
    p.add_argument('--title', help='手动指定论文标题')
    p.add_argument('--slug', help='手动指定 slug')
    p.add_argument('--paper-id', help='手动指定 arXiv id / paper id')
    p.add_argument('--scope', default='general', choices=['general', 'coding-agentic', 'multimodal'], help='任务类别前缀')
    p.add_argument('--turn-type', default='single-turn', choices=['single-turn', 'multi-turn'], help='单轮还是多轮')
    p.add_argument('--artifact-type', default='method', choices=['method', 'dataset', 'benchmark', 'survey', 'repo'], help='论文/资料类型')
    p.add_argument('--copy', action='store_true', help='把 PDF 复制进仓库 pdfs/ 目录')
    return p.parse_args()


def ensure_dirs():
    PDF_DIR.mkdir(exist_ok=True)
    PAPERS_DIR.mkdir(exist_ok=True)
    TMP_DIR.mkdir(exist_ok=True)


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8') if path.exists() else ''


def write_text(path: Path, content: str):
    path.write_text(content, encoding='utf-8')


def find_existing_note_by_id(paper_id: str) -> Path | None:
    matches = sorted(PAPERS_DIR.glob(f'*-{paper_id}-*.md'))
    return matches[0] if matches else None


def build_prefix(scope: str, turn_type: str, artifact_type: str) -> str:
    return f'{scope}-{turn_type}-{artifact_type}'


def maybe_copy_pdf(src: Path, paper_id: str | None, slug: str, prefix: str) -> Path:
    if paper_id:
        dst_name = f'{prefix}-{paper_id}-{slug}.pdf'
    else:
        dst_name = src.name
    dst = PDF_DIR / dst_name
    if src.resolve() != dst.resolve():
        shutil.copy2(src, dst)
    return dst


def extract_pdf_text(pdf_path: Path, stem: str) -> Path:
    txt_path = TMP_DIR / f'{stem}.txt'
    run(['pdftotext', '-layout', str(pdf_path), str(txt_path)])
    return txt_path


def infer_title_from_text(text: str) -> str:
    lines = [ln.strip() for ln in text.splitlines()[:40] if ln.strip()]
    for ln in lines:
        if len(ln) > 20 and not ln.lower().startswith(('arxiv', 'preprint', 'abstract')):
            return ln
    return '待补标题'


def build_note(title: str, paper_id: str, slug: str, pdf_path: Path, txt_path: Path) -> str:
    paper_link = f'https://arxiv.org/abs/{paper_id}' if paper_id else '待补论文链接'
    return f'''# {title}

## 1. 论文基本信息
- 标题：{title}
- 作者 / 机构：待补
- 发表时间：待补
- 会议 / 期刊：待补
- 论文链接：{paper_link}
- 代码链接：未验证到公开代码仓库
- 本地 PDF：`{pdf_path.relative_to(REPO_ROOT)}`
- 抽取文本：`{txt_path.relative_to(REPO_ROOT)}`

## 2. 一句话总结
- 总结：待基于 PDF 精读补充。

## 3. 研究问题
### 3.1 核心问题是什么？
- 待补。

### 3.2 为什么这个问题重要？
- 待补。

### 3.3 主要优化目标是什么？
- 待补。

## 4. 方法概览
### 4.1 提出的方法是什么？
- 待补。

### 4.2 Router 的输入是什么？
- 待补。

### 4.3 Router 的输出是什么？
- 待补。

### 4.4 Routing 决策如何产生？
- 待补。

### 4.5 是否需要训练 Router？
- 待补。

### 4.6 涉及哪些学习机制？
- 待补。

## 5. 系统架构
### 5.1 整体 Pipeline
- 待补。

### 5.2 包含哪些模型 / 模块？
- 待补。

### 5.3 路由发生在哪个阶段？
- 待补。

### 5.4 是否支持 fallback / cascade / online update？
- 待补。

### 5.5 我的理解
- 待补。

## 6. 实验设置
### 6.1 使用了哪些数据集？
- 待补。

### 6.2 对比了哪些 Baseline？
- 待补。

### 6.3 评估了哪些任务类型？
- 待补。

### 6.4 使用了哪些大模型或专家模型？
- 待补。

### 6.5 主要评估指标是什么？
- 待补。

## 7. 核心结果
### 7.1 最重要的实验结果是什么？
- 待补。

### 7.2 相比 Baseline 提升了什么？
- 待补。

### 7.3 trade-off 如何？
- 待补。

### 7.4 Ablation / Sensitivity / Appendix 关键补充
- 待补。

## 8. 贡献与创新点
### 8.1 主要贡献
- 待补。

### 8.2 相比已有方法的新意
- 待补。

### 8.3 创新类型
- 待补。

## 9. 局限性
### 9.1 方法假设
- 待补。

### 9.2 依赖特定模型 / 数据 / 标注吗？
- 待补。

### 9.3 泛化、稳定性、成本、延迟、部署问题
- 待补。

### 9.4 作者自己提到的 limitation
- 待补。

### 9.5 我认为的潜在问题
- 待补。

## 10. 对我的启发
### 10.1 对 agentic router 的帮助
- 待补。

### 10.2 可借鉴的方法部件
- 待补。

### 10.3 可扩展想法
- 待补。

### 10.4 适用场景
- 待补。

## 11. 可复现性记录
### 11.1 是否开源代码？
- 未验证到公开代码仓库

### 11.2 是否开源数据？
- 待补：公开 / 部分公开 / 未验证到公开入口

### 11.3 关键实现细节是否清楚？
- 待补。

### 11.4 复现难度
- 待补。

### 11.5 如果我要复现，第一步应该做什么？
- 待补。

## 12. 横向比较字段
- Routing 对象：待补
- Routing 粒度：待补
- Router 类型：待补
- 是否训练：待补
- 训练信号：待补
- 优化目标：待补
- 支持的模型数量：待补
- 是否考虑成本：待补
- 是否考虑延迟：待补
- 是否 online：待补
- 是否开源：待补
- 主要优点：待补
- 主要缺点：待补

## 13. 阅读后的评分
- 相关性：待补
- 方法新颖性：待补
- 实验可信度：待补
- 工程可落地性：待补
- 对我研究 / 工作的启发：待补

### 总评
- 是否值得精读：待补
- 是否值得复现：待补
- 是否值得纳入自己的系统设计：待补
- 一句话结论：待补
'''


def update_manifest(paper_id: str, title: str, slug: str, pdf_rel: str, md_rel: str, scope: str, turn_type: str, artifact_type: str):
    if not MANIFEST.exists():
        return
    data = json.loads(read_text(MANIFEST) or '[]')
    found = False
    for item in data:
        if item.get('paper_id') == paper_id or item.get('id') == paper_id:
            item['title'] = title
            item['slug'] = slug
            item['pdf_path'] = pdf_rel
            item['note_path'] = md_rel
            item['paper_id'] = paper_id
            item['group'] = scope
            item['interaction'] = turn_type
            item['artifact_type'] = artifact_type
            item['filename_prefix'] = build_prefix(scope, turn_type, artifact_type)
            found = True
            break
    if not found:
        data.append({
            'paper_id': paper_id,
            'title': title,
            'slug': slug,
            'pdf_path': pdf_rel,
            'note_path': md_rel,
            'group': scope,
            'interaction': turn_type,
            'artifact_type': artifact_type,
            'filename_prefix': build_prefix(scope, turn_type, artifact_type),
        })
    write_text(MANIFEST, json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def append_if_missing(path: Path, marker: str, line: str):
    text = read_text(path)
    if marker in text or line in text:
        return
    write_text(path, text.rstrip() + '\n' + line + '\n')


def append_row_if_missing(path: Path, marker: str, row: str):
    text = read_text(path)
    if marker in text:
        return
    write_text(path, text.rstrip() + '\n' + row + '\n')


def main():
    args = parse_args()
    ensure_dirs()

    cleanup_pdf = False
    if is_url(args.pdf):
        pdf_input = download_pdf(args.pdf)
        cleanup_pdf = True
    else:
        pdf_input = Path(args.pdf)
        if not pdf_input.is_absolute():
            pdf_input = (REPO_ROOT / pdf_input).resolve()
    if not pdf_input.exists():
        print(f'PDF 不存在: {pdf_input}', file=sys.stderr)
        sys.exit(1)

    try:
        paper_id = args.paper_id or extract_arxiv_id(args.pdf) or extract_arxiv_id(pdf_input.name) or ''

        tmp_probe = TMP_DIR / '__probe__.txt'
        run(['pdftotext', '-f', '1', '-l', '2', '-layout', str(pdf_input), str(tmp_probe)])
        first_pages = read_text(tmp_probe)
        if tmp_probe.exists():
            tmp_probe.unlink()

        title = args.title or infer_title_from_text(first_pages)
        slug = args.slug or slugify(title)

        prefix = build_prefix(args.scope, args.turn_type, args.artifact_type)
        pdf_path = maybe_copy_pdf(pdf_input, paper_id or None, slug, prefix) if args.copy else pdf_input
        stem = f'{prefix}-{paper_id}-{slug}' if paper_id else f'{prefix}-{slug}'
        txt_path = extract_pdf_text(pdf_path, stem)

        existing_note = find_existing_note_by_id(paper_id) if paper_id else None
        note_name = existing_note.name if existing_note else (f'{prefix}-{paper_id}-{slug}.md' if paper_id else f'{prefix}-{slug}.md')
        note_path = existing_note if existing_note else (PAPERS_DIR / note_name)
        if not note_path.exists():
            write_text(note_path, build_note(title, paper_id, slug, pdf_path, txt_path))

        pdf_rel = str(pdf_path.relative_to(REPO_ROOT)) if pdf_path.is_relative_to(REPO_ROOT) else str(pdf_path)
        md_rel = str(note_path.relative_to(REPO_ROOT))

        if paper_id:
            update_manifest(paper_id, title, slug, pdf_rel, md_rel, args.scope, args.turn_type, args.artifact_type)
            append_if_missing(READING_QUEUE, f'({paper_id})', f'- [ ] {title} ({paper_id})')
            file_size = pdf_path.stat().st_size if pdf_path.exists() else 0
            append_row_if_missing(LOCAL_INDEX, f'| {args.scope} | {args.turn_type} | {args.artifact_type} | {paper_id} |', f'| {args.scope} | {args.turn_type} | {args.artifact_type} | {paper_id} | {title} | `{Path(pdf_rel).name}` | {file_size} | ok |')

        result = {
            'title': title,
            'paper_id': paper_id,
            'slug': slug,
            'pdf_path': pdf_rel,
            'text_path': str(txt_path.relative_to(REPO_ROOT)),
            'note_path': md_rel,
            'next_step': f'让 Hermes 基于 {md_rel} + {txt_path.relative_to(REPO_ROOT)} 做高强度精读并清理待补字段'
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        if cleanup_pdf and pdf_input.exists() and not pdf_input.is_relative_to(REPO_ROOT):
            pdf_input.unlink()


if __name__ == '__main__':
    main()
