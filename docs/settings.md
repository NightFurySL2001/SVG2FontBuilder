## SVG2FontBuilder

### Theme 主题
Choose to use Dark or Light theme. Why would you choose Light?  
选择黑暗或者光亮模式。为什么要选光亮？

### Language 语言
Choose UI language, duh.  
选择界面语言（白目）。

### Normalize SVG 规范化 SVG
Choose if you want to use `picosvg` to normalise your SVG outlines, including tracing strokes and clip paths to normal outlines. If this option is off, you may see different glyphs if you use strokes or clip paths.  
选择是否要使用 `picosvg` 来规范化 SVG 轮廓，包括将描边和蒙版路径转换为标准轮廓。如果关闭此选项，您可能看到使用描边和蒙版路径的字形会和导入后不一样。

### Strict mode 严格模式
Choose if you want to exclude SVG files in the selected folder (and subfolders) if it is not listed in the CSV file. Only works if you use CSV mapping file. If this option is off, SVG files that are not listed in CSV will be imported using their file names.  
选择是否排除不在 CSV 文件内，但是在选择的文件夹内的 SVG 文件。只在使用 CSV 映射表时应用。如果关闭此选项，不在 CSV 内的 SVG 文件夹会依据文件名导入字体。

#### Example 示例

CSV mapping file 映射文件
```csv
Artboard 1.svg,uni4E00
Artboard 2.svg,你
Artboard 3.svg,好
test/Artboard X.svg,yen
```

SVG folder structure 文件夹目录结构
```structure
.
├───Artboard 1.svg
├───Artboard 2.svg
├───Artboard 3.svg
├───Artboard 4.svg
├───Artboard 5.svg
├───test
│   ├───Artboard X.svg
│   ├───Artboard Y.svg
│   └───Artboard Z.svg
└───folder2
    ├───uni2F00.svg
    ├───ㄅ.svg
    └───zero.svg
```

Strict mode on: Font contains glyphs  
严格模式开启：字型内的字形包含

`uni4E00` (U+4E00 一), `uni4F60` (U+4F60, 你), `uni597D` (U+597D, 好), `yen` (U+00A5, ¥)

Strict mode off: Font contains glyphs  
严格模式关闭：字型内的字形包含

`uni4E00` (U+4E00 一), `uni4F60` (U+4F60, 你), `uni597D` (U+597D, 好), `Artboard4`, `Artboard5`,  
`yen` (U+00A5, ¥), `ArtboardY`, `ArtboardZ`,  
`uni2F00` (U+2F00, ⼀), `uni3015` (U+3015, ㄅ), `zero` (U+0030, 0)