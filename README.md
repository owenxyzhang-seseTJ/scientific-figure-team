# Scientific Figure Team / 科研绘图专家团 / 科学図作成チーム

Python-first, raw-data-gated scientific figure plugin for MOF and general research figures. It requires method search before preprocessing, creates an English figure plan for confirmation, writes Python code with Chinese comments, exports publication-ready figures, and runs final rendered-image/readability audit before delivery.

Python-first 科研绘图插件。定量图强制使用原始数据，预处理前先检索文献/仪器/软件处理方法，先生成英文图件计划等待确认，再预处理和出图。图中文字默认英文，Python 代码批注默认中文；终稿图片和可读性审核不通过时必须打回重画。

Python-first の科学図作成プラグインです。定量図では生データを必須とし、前処理前に文献・装置・ソフトウェアの処理方法を確認し、英語の作図計画を承認してから前処理と描画を行います。図中テキストは英語、Python コード注釈は中国語が既定で、最終レンダリングと可読性監査に不合格の場合は再描画します。

---

## 中文

### 上传目标

上传或安装整个仓库根目录：

```text
./
```

跨平台入口：

- Codex：`.codex-plugin/plugin.json`
- Claude Code：`.claude-plugin/plugin.json`
- WorkBuddy / CodeBuddy：`plugin.json`、`settings.json`、`.codebuddy-plugin/plugin.json`
- ZCode：`.zcode-plugin/plugin.json`
- 通用 Agent Skills：`skills/scientific-figure-team/SKILL.md`
- 团队 subagents：`agents/*.md`

### 强制工作流

1. 定量图必须上传原始、机器可读数据；截图或文字总结不能替代 raw data。
2. 预处理前必须搜索相关文献、仪器/软件文档，或读取用户提供的 Methods/SI。
3. 填写 `method_search_packet.md`：来源、采用方法、理由、假设、未采用方法。
4. 生成英文 `figure_plan.md`，等待用户确认。
5. 确认后才预处理，输出到 `data_processed/`，不覆盖 `data_raw/`。
6. 预处理后才绘图；图中文字默认英文，代码批注默认中文。
7. 导出前检查中文批注、图面重叠、原生上下标、格式和科学边界。
8. 终稿渲染图必须通过 `figure-image-final-auditor`；若审核不通过，打回 `figure-python-plotter` 重画并重新审核。
9. 可读性硬规则：默认无网格线；备注不使用框；多图 `a/b/c` 放在子图外侧左上角；默认可见文字不低于 8.5 pt，任何文字不得低于 8 pt；整张图只使用一个实际字体，优先 Arial，若未安装则统一用 DejaVu Sans；如果需要面积、模块或背景填色，默认使用轻微渐变，避免大块单色填充；默认文字位置只是起点，若遮挡数据、虚线、图例或坐标轴，必须移动到空白位或用短引导线错开。

### 团队角色

| Agent | 中文角色 | 职责 |
| --- | --- | --- |
| `figure-team-lead` | 图件总控 | 调度原始数据、方法检索、英文计划确认、预处理、出图和 QA |
| `figure-task-router` | 任务分流员 | 判断任务类型，检查 raw data gate 和 method-search gate |
| `figure-execution-planner` | 执行包规划员 | 生成 method packet、预处理方案、英文 figure plan、panel map 和图注草稿 |
| `figure-python-plotter` | Python 出图员 | 确认方法包和计划后预处理/绘图，导出 SVG/PDF/TIFF/PNG |
| `figure-qa-reviewer` | 图件质检员 | 检查方法追踪、预处理、科学逻辑、图面重叠、导出质量和中文批注 |
| `figure-image-final-auditor` | 终稿看图审核员 | 检查最终图片中的上下标、单位、虚线、PXRD 标注、字体过小、文字溢出/重叠、框备注、网格线和 panel label 位置；不通过则打回重画 |

### MOF 模板

支持模板：

- `pxrd`：独立归一化，默认 simulated、as-synthesized、solvent-exchanged、activated 依次上下错峰，并在每条曲线最右端附近的曲线上方直接标注对应内容。
- `tga`：起始点归一化到 100%；activated 且存在 hold/cooling/reheating 时，用 reheating 起点作为 100%。
- `adsorption`：散点图，adsorption 实心，desorption 空心；横轴默认 `P/P$_0$`，若原始数据给出 `pressure_unit` 则保持原始单位。
- `qst`：`Q$_{st}$` vs loading，不自动发明热力学计算。
- `iast`：需要 gas pair、composition、pressure、selectivity。
- `breakthrough`：`C/C$_0$` vs time 或 bed volume；气体分子默认使用原生下标，横轴默认 `min/g`，不默认添加虚线 threshold，除非计划或原始数据明确确认。
- `cv`：轻度平滑需先记录处理方法；多扫速 CV 的扫速说明默认放在对应子图框内，并选择不遮挡 CV 曲线的位置。
- `raman` / `ftir` / 其它堆叠谱图：曲线标签优先放在曲线右端上方；若遮挡谱峰或虚线，改放到邻近空白区，必要时用短引导线连接。

新建 MOF 模板项目：

```bash
python3 skills/scientific-figure-team/scripts/mof_figure_templates.py init mof_job
```

预处理与出图示例：

```bash
python3 skills/scientific-figure-team/scripts/mof_figure_templates.py preprocess pxrd mof_job/data_raw/pxrd_raw.csv mof_job/data_processed/pxrd_processed.csv --method-packet mof_job/method_search_packet.md
python3 skills/scientific-figure-team/scripts/mof_figure_templates.py plot pxrd mof_job/data_processed/pxrd_processed.csv mof_job/outputs --plan mof_job/figure_plan.md
```

### 代码规则

任何影响视觉输出的 Python 行都必须有中文行尾注释：

```python
fig, ax = plt.subplots(figsize=(7.2, 4.8), constrained_layout=True)  # 控制整张图尺寸并自动压紧面板间距
ax.plot(x, y, color="#5DA9A6", lw=1.8, marker="o")  # 设置主曲线颜色、线宽和数据点标记
fig.savefig("figure.svg", bbox_inches="tight")  # 导出可编辑 SVG 并裁掉多余白边
```

检查命令：

```bash
python3 skills/scientific-figure-team/scripts/validate_python_comments.py path/to/plot_script.py
python3 skills/scientific-figure-team/scripts/audit_rendered_figure.py path/to/figure.svg path/to/plot_script.py
```

### Demo 图

已生成 demo 项目：

```text
./demo_mof_templates
./demo_general_figure
```

PNG 预览：

- `demo_mof_templates/outputs/pxrd.png`
- `demo_mof_templates/outputs/tga.png`
- `demo_mof_templates/outputs/gas_adsorption.png`
- `demo_mof_templates/outputs/qst.png`
- `demo_mof_templates/outputs/iast.png`
- `demo_mof_templates/outputs/breakthrough.png`
- `demo_general_figure/outputs/figure_demo.png`

每个 MOF demo 同时包含 SVG/PDF、`*_overlap_report.txt` 和 `final_image_audit_report.md`；通用 demo 包含 SVG/PDF/PNG 和 `final_image_audit_report.md`；实际模板运行时仍会导出 TIFF。

### 验证状态

- Codex manifest、skill frontmatter、JSON manifest 验证通过。
- `scaffold_figure_project.py`、`mof_figure_templates.py`、`validate_python_comments.py` 通过 `py_compile`。
- 通用脚手架和 MOF 模板脚本通过中文视觉批注检查。
- 本机已检测到 Arial，MOF 与通用 demo SVG 的普通文字、数字和上下标均统一为 Arial；若运行环境没有 Arial，模板会统一回退到 DejaVu Sans。
- 通用 demo 的面积填色已改为轻微渐变，并通过渲染可读性审计。
- PXRD、TGA、adsorption、Qst、IAST、breakthrough 预处理测试通过。
- 未确认 `figure_plan.md` 时拒绝绘图；坏 `method_search_packet.md` 时拒绝预处理。
- 已用临时 venv 安装 matplotlib 并生成 6 类 MOF demo 图和 1 个通用 demo 图。
- 已加入最终渲染图审核员；审核不通过时必须打回重画。

---

## English

### Upload Target

Upload or install the repository root:

```text
./
```

Entrypoints:

- Codex: `.codex-plugin/plugin.json`
- Claude Code: `.claude-plugin/plugin.json`
- WorkBuddy / CodeBuddy: `plugin.json`, `settings.json`, `.codebuddy-plugin/plugin.json`
- ZCode: `.zcode-plugin/plugin.json`
- Agent Skills: `skills/scientific-figure-team/SKILL.md`
- Subagents: `agents/*.md`

### Required Workflow

1. Quantitative figures require raw machine-readable data.
2. Search relevant papers, instrument/software documentation, or user-provided Methods/SI before preprocessing.
3. Complete `method_search_packet.md` with sources, chosen method, rationale, assumptions, and rejected alternatives.
4. Create an English `figure_plan.md` and wait for confirmation.
5. Preprocess only after confirmation; save outputs to `data_processed/`.
6. Plot after preprocessing. Figure labels default to English; Python comments default to Chinese.
7. Before delivery, check Chinese code comments, text/image overlap, native sub/superscripts, export formats, and scientific limits.
8. Final rendered images must pass `figure-image-final-auditor`; failed audits are sent back to `figure-python-plotter` for redraw and re-audit.
9. Readability hard rules: no default gridlines; no boxed remarks; multi-panel `a/b/c` labels sit outside each subplot's upper-left; default visible text is at least 8.5 pt and no text is below 8 pt; use one actual font family throughout, preferring Arial and falling back to one unified DejaVu Sans font when Arial is unavailable; use subtle gradients for area, module, or background fills instead of flat solid color blocks; default text positions are only starting points, and any label that overlaps data, guide lines, legends, or axes must move to whitespace or use a short leader line.

### MOF Templates

Supported templates:

- `pxrd`: independently normalize each pattern, vertically offset simulated, as-synthesized, solvent-exchanged, activated, and place direct labels above each trace near the curve's right end.
- `tga`: normalize the selected start point to 100%; activated hold/cooling/reheating data use the reheating start as 100%.
- `adsorption`: scatter plot; adsorption filled, desorption hollow; x-axis defaults to `P/P$_0$` and respects `pressure_unit` from raw data.
- `qst`: `Q$_{st}$` vs loading; no silent thermodynamic computation.
- `iast`: requires gas pair, composition, pressure, and selectivity.
- `breakthrough`: `C/C$_0$` vs time or bed volume; molecule labels use native subscripts, x-axis defaults to `min/g`, and dashed threshold lines are omitted unless explicitly confirmed.
- `cv`: document the smoothing method first; scan-rate labels for multi-scan CV panels stay inside the corresponding axes box by default and use the least obstructive corner.
- `raman` / `ftir` / other stacked spectra: trace labels first try above the curve near the right end; if that overlaps peaks or guide lines, move them to nearby whitespace and use a short leader line when needed.

Create a MOF template project:

```bash
python3 skills/scientific-figure-team/scripts/mof_figure_templates.py init mof_job
```

Example:

```bash
python3 skills/scientific-figure-team/scripts/mof_figure_templates.py preprocess pxrd mof_job/data_raw/pxrd_raw.csv mof_job/data_processed/pxrd_processed.csv --method-packet mof_job/method_search_packet.md
python3 skills/scientific-figure-team/scripts/mof_figure_templates.py plot pxrd mof_job/data_processed/pxrd_processed.csv mof_job/outputs --plan mof_job/figure_plan.md
```

Rendered-readability audit:

```bash
python3 skills/scientific-figure-team/scripts/audit_rendered_figure.py mof_job/outputs/pxrd.svg mof_job/scripts/plot_figure.py
```

### Demo Figures

Generated demo project:

```text
./demo_mof_templates
./demo_general_figure
```

PNG previews:

- `demo_mof_templates/outputs/pxrd.png`
- `demo_mof_templates/outputs/tga.png`
- `demo_mof_templates/outputs/gas_adsorption.png`
- `demo_mof_templates/outputs/qst.png`
- `demo_mof_templates/outputs/iast.png`
- `demo_mof_templates/outputs/breakthrough.png`
- `demo_general_figure/outputs/figure_demo.png`

MOF demos include SVG/PDF exports, overlap reports, and `final_image_audit_report.md`; the general demo includes SVG/PDF/PNG and `final_image_audit_report.md`. TIFF export is still generated by the templates during normal runs.

---

## 日本語

### アップロード対象

次のリポジトリルート全体をアップロードまたはインストールしてください。

```text
./
```

対応入口：

- Codex：`.codex-plugin/plugin.json`
- Claude Code：`.claude-plugin/plugin.json`
- WorkBuddy / CodeBuddy：`plugin.json`、`settings.json`、`.codebuddy-plugin/plugin.json`
- ZCode：`.zcode-plugin/plugin.json`
- Agent Skills：`skills/scientific-figure-team/SKILL.md`
- サブエージェント：`agents/*.md`

### 必須ワークフロー

1. 定量図には機械可読な生データが必須です。
2. 前処理前に関連論文、装置/ソフトウェア文書、またはユーザー提供の Methods/SI を確認します。
3. `method_search_packet.md` に参照元、採用した処理法、理由、仮定、採用しなかった方法を記録します。
4. 英語の `figure_plan.md` を作成し、承認を待ちます。
5. 承認後にのみ前処理し、結果を `data_processed/` に保存します。
6. 前処理後に描画します。図中テキストは英語、Python コード注釈は中国語が既定です。
7. 納品前に中国語コード注釈、文字/画像の重なり、ネイティブ上下付き文字、出力形式、科学的限界を確認します。
8. 最終レンダリング画像は `figure-image-final-auditor` に合格する必要があります。不合格の場合は `figure-python-plotter` に戻して再描画し、再監査します。
9. 可読性の必須ルール：既定ではグリッド線を使わない、注釈を枠で囲まない、複数パネルの `a/b/c` は各サブプロット外側の左上に置く、通常の可視テキストは 8.5 pt 以上、すべての文字は 8 pt 以上。図全体で実際に使うフォントは 1 種類に統一し、Arial を優先し、未インストールの場合は DejaVu Sans に統一します。面、モジュール、背景を塗る場合は、平坦な単色ではなく控えめなグラデーションを使います。既定の文字位置は出発点にすぎず、データ、補助線、凡例、軸と重なる場合は空白領域へ移動するか短いリーダー線でずらします。

### MOF テンプレート

対応テンプレート：

- `pxrd`：各パターンを独立に正規化し、simulated、as-synthesized、solvent-exchanged、activated の順に縦方向へオフセットし、各曲線の右端付近で線の上側に直接ラベルを配置します。
- `tga`：開始点を 100% に正規化。activated の hold/cooling/reheating データでは reheating 開始点を 100% とします。
- `adsorption`：散布図。adsorption は塗りつぶし、desorption は白抜き。横軸は既定で `P/P$_0$` とし、生データの `pressure_unit` があればそれを優先します。
- `qst`：`Q$_{st}$` と loading。熱力学計算は勝手に行いません。
- `iast`：gas pair、composition、pressure、selectivity が必要です。
- `cv`：平滑化方法を先に記録します。複数掃引速度の CV では、掃引速度ラベルを既定で各サブプロット枠内の邪魔にならない位置に置きます。
- `raman` / `ftir` / その他の積み重ねスペクトル：曲線ラベルはまず右端付近の線上に置きます。ピークや補助線と重なる場合は近い空白領域へ移動し、必要に応じて短いリーダー線を使います。
- `breakthrough`：`C/C$_0$` と time または bed volume。気体分子はネイティブ下付き文字で表示し、横軸は既定で `min/g`、破線 threshold は明示確認がある場合のみ追加します。

MOF テンプレートプロジェクトを作成：

```bash
python3 skills/scientific-figure-team/scripts/mof_figure_templates.py init mof_job
```

例：

```bash
python3 skills/scientific-figure-team/scripts/mof_figure_templates.py preprocess pxrd mof_job/data_raw/pxrd_raw.csv mof_job/data_processed/pxrd_processed.csv --method-packet mof_job/method_search_packet.md
python3 skills/scientific-figure-team/scripts/mof_figure_templates.py plot pxrd mof_job/data_processed/pxrd_processed.csv mof_job/outputs --plan mof_job/figure_plan.md
```

### デモ図

生成済みデモプロジェクト：

```text
./demo_mof_templates
./demo_general_figure
```

PNG プレビュー：

- `demo_mof_templates/outputs/pxrd.png`
- `demo_mof_templates/outputs/tga.png`
- `demo_mof_templates/outputs/gas_adsorption.png`
- `demo_mof_templates/outputs/qst.png`
- `demo_mof_templates/outputs/iast.png`
- `demo_mof_templates/outputs/breakthrough.png`
- `demo_general_figure/outputs/figure_demo.png`

MOF デモには SVG/PDF、overlap report、`final_image_audit_report.md` が含まれています。汎用デモには SVG/PDF/PNG と `final_image_audit_report.md` が含まれています。通常実行時には TIFF も生成されます。
