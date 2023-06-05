![Banner of SVG2FontBuilder](images/banner.png)
# SVG2FontBuilder

A program that converts SVG vector diagram files into a font file.  
将 SVG 向量图转换成字型文件的软件。

**[Download here. 在此下载。](https://github.com/NightFurySL2001/SVG2FontBuilder/releases)**

___

## How this works 如何运作

This programs loads multiple SVG files and import them as glyph outlines using FontTools. Currently only OpenType `.otf` files can be exported.  
此软件将多个 SVG 向量图文件作为字形轮廓线导入 FontTools。目前只支持导出 OpenType `.otf` 文件。

A detailed software usage **tutorial** may be found in [`docs` folder](docs/设计师如何制作一套字库%20手把手教你生成字库教程.md) (currently only available in Chinese). Details for the settings can be found in [settings.md](docs/settings.md).  
详细的软件使用**教程**可以参考 [`docs` 文件夹内的文本](docs/设计师如何制作一套字库%20手把手教你生成字库教程.md)。设置部分的详细功能可在 [settings.md](docs/settings.md) 阅读。

## Currently supported formats 支援格式

**Import**: SVG outlines including `path`, `g`, `rect`, `clip_path` and more as supported by `picosvg` (see dependencies section). Text elements (`text`, `textPath`, `tspan`) are not converted to outlines due to inaccessible font, and bitmap diagrams (`image`) are removed before importing. Currently `picosvg` does not support CSS stylesheet (`style` block), so please use inline style if you have applied important transformation on your outlines.  
**导入**：SVG 轮廓包括 `path`、`g`、`rect`、`clip_path` 和其他 `picosvg` 支援的轮廓（见下面依赖模块）。文字元素（`text`、`textPath`、`tspan`）不会转换成轮廓因为无法寻找字型；点阵图（`image`）在导入前会被移除。目前 `picosvg` 不支持 CSS 层叠样式（`style` 元素），因此导出时请使用样式元素。

**Export**: OpenType/CFF (Bézier curve) font.
**导出**：OpenType/CFF（贝兹曲线）字型。

**Mapping**: You may provide a CSV mapping file with the first column is the relative path of SVG files and the second column is the character to be mapped onto. Characters may be specified using the character itself (limited to length of 1), using the Unicode codepoint (e.g. `uni4E00` or `u2F000`), or using Adobe AGLFN names. See more information on this in [settings.md](docs/settings.md).  
您可以提供 CSV 映射表，其中第一列（直下）是 SVG 文件的相对路径，第二列是映射至的字符。字符可以使用字符本身（长度限制为 1）、使用 Unicode 编码（例如 `uni4E00` 或 `u2F000`）、或使用 Adobe AGLFN 名称指定。在 [settings.md](docs/settings.md) 内可以阅读更详细内容。

Alternatively, you may choose to tick the "Use filename to auto assign Unicode codepoint" option, which uses the filename (excluding file extension) to determine the character to be mapped to. The options for naming the character is the same as above.  
或者。您也可以勾选“使用文件名自动辨识 Unicode 码位”选项，软件就会自动使用文件名（扣除扩展名）判断应该映射的字符。可以指定字符的名称同上。

## Dependencies 依赖模块

* `kivymd` (+ `kivy`)  
  For software display.   
  使用于软件显示。

* [`fontTools`](https://github.com/fonttools/fonttools)  
  Generate OpenType fonts from T2 outlines.    
  使用 T2 轮廓生成 OpenType 字型。

* [`picosvg`](https://github.com/googlefonts/picosvg)  
  Normalise SVG outlines, including tracing strokes and clip paths to normal outlines.  
  规范化 SVG 轮廓，包括将描边和蒙版路径转换为标准轮廓。

* [`pyinstaller`](https://github.com/pyinstaller/pyinstaller)  
  Build executable for Windows in [release](https://github.com/NightFurySL2001/SVG2FontBuilder/releases/latest).  
  编译软件成可执行软件。[发布版](https://github.com/NightFurySL2001/SVG2FontBuilder/releases/latest)内提供 Windows 版本。
  
##  License 授权

This software is licensed under [MIT License](https://opensource.org/licenses/MIT). Details of the license can be found in the [accompanying `LICENSE` file](LICENSE).  
本软件以 [MIT 授权条款](https://opensource.org/licenses/MIT)发布。授权详情可在[随附的 `LICENSE` 文件内](LICENSE)查阅。

## To build 如何构建

Please install [latest version of Python 3](https://www.python.org/downloads/).  
请先安装[最新版本的 Python 3](https://www.python.org/downloads/)。

### Building software 构建软件
```
# Install dependency requirements
pip3 install -r requirements.txt

# To build single language
pyinstaller svgbuilder.spec
# replace SDL2.dll for Chinese IME
copy ".\overrides\SDL2.dll" ".\dist\svgbuilder"

# Full command to build and zip file
.\build.bat
```

## Contributions 贡献

Thanks to [@anthrotype](https://github.com/anthrotype) for helping out in `picosvg` and pointers for using `SVGPen` in FontTools.  
感谢 [@anthrotype](https://github.com/anthrotype) 在 `picosvg` 的协助和 FontTools 内使用 `SVGPen`。

Thanks to [@MY1L](https://github.com/MY1L) for designing the software icon.  
感谢 [@MY1L](https://github.com/MY1L) 设计软件图标。

## To-do 待办事项

* Export UFO?

## Changelog 更新日志

Refer to [HISTORY.md](HISTORY.md).  
参考[HISTORY.md](HISTORY.md)。

