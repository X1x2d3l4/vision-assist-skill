#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""PDF 取图工具：把 PDF 页面渲染成 PNG，或提取页内嵌图片。

用法:
  python pdf_to_images.py <pdf路径> [--mode page|embedded] [--pages 1,3-5] [--dpi 200] [--out 目录]

输出:
  stdout 打印 JSON: {"mode": "...", "count": N, "images": ["...png", ...]}

依赖:
  PyMuPDF（fitz），本机已安装。
"""

import argparse
import json
import os
import re
import sys

import fitz


def parse_pages(spec, total):
    """把 "1,3-5" 或 "all" 解析成页码列表（1 起）。"""
    if not spec or spec.strip().lower() == "all":
        return list(range(1, total + 1))
    pages = set()
    for part in spec.split(","):
        part = part.strip()
        match = re.match(r"^(\d+)(?:-(\d+))?$", part)
        if not match:
            raise ValueError(f"页码格式错误: {part}")
        start = int(match.group(1))
        end = int(match.group(2) or start)
        if start > end:
            raise ValueError(f"页码区间错误: {part}")
        for p in range(start, end + 1):
            if 1 <= p <= total:
                pages.add(p)
    if not pages:
        raise ValueError("指定页码超出文档范围")
    return sorted(pages)


def _write_bytes(path, data):
    with open(path, "wb") as f:
        f.write(data)


def page_mode(doc, pages, dpi, out, stem):
    """整页渲染：每页一张高清 PNG。"""
    images = []
    for p in pages:
        pix = doc[p - 1].get_pixmap(dpi=dpi)
        name = f"{stem}-p{p:03d}.png"
        path = os.path.join(out, name)
        _write_bytes(path, pix.tobytes("png"))
        images.append(path)
    return images


def embedded_mode(doc, pages, out, stem):
    """提取页内嵌图片：按 xref 去重，保留原图格式。"""
    images = []
    seen = set()
    for p in pages:
        for img in doc[p - 1].get_images(full=True):
            xref = img[0]
            if xref in seen:
                continue
            seen.add(xref)
            info = doc.extract_image(xref)
            ext = info.get("ext", "png")
            name = f"{stem}-p{p:03d}-x{xref}.{ext}"
            path = os.path.join(out, name)
            _write_bytes(path, info["image"])
            images.append(path)
    return images


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="PDF 取图工具")
    parser.add_argument("pdf", help="PDF 文件路径")
    parser.add_argument("--mode", choices=["page", "embedded"], default="page",
                        help="page=整页渲染(默认)，embedded=提取页内嵌图片")
    parser.add_argument("--pages", default="all",
                        help='页码，如 "1,3-5"；默认全部')
    parser.add_argument("--dpi", type=int, default=200, help="渲染分辨率(默认 200)")
    parser.add_argument("--out", help="输出目录(默认 PDF 同目录/<文件名>_vision)")
    args = parser.parse_args(argv)

    if not os.path.isfile(args.pdf):
        print(f"文件不存在: {args.pdf}", file=sys.stderr)
        return 1

    pdf_path = os.path.abspath(args.pdf)
    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    out = args.out or os.path.join(os.path.dirname(pdf_path), f"{stem}_vision")
    os.makedirs(out, exist_ok=True)

    try:
        doc = fitz.open(pdf_path)
        try:
            pages = parse_pages(args.pages, doc.page_count)
            if args.mode == "page":
                images = page_mode(doc, pages, args.dpi, out, stem)
            else:
                images = embedded_mode(doc, pages, out, stem)
        finally:
            doc.close()
    except Exception as exc:
        print(f"PDF 取图失败: {exc}", file=sys.stderr)
        return 1

    print(json.dumps({
        "mode": args.mode,
        "count": len(images),
        "images": images,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
