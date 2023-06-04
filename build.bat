pyinstaller --clean --noconfirm svgbuilder.spec
copy ".\overrides\SDL2.dll" ".\dist\svgbuilder"
del /f /q ".\dist\svg2fontbuilder.zip"
7z a dist/svg2fontbuilder.zip dist/svgbuilder/*