@echo off
echo 🚀 快速安装AI多Agent产品Demo生成器（使用清华镜像源）

set MIRROR=https://pypi.tuna.tsinghua.edu.cn/simple

echo 📦 使用清华大学PyPI镜像源加速安装...

REM 升级pip
python -m pip install --upgrade pip -i %MIRROR%

REM 方式1：尝试使用requirements.txt
echo 🔧 尝试使用requirements.txt安装...
pip install -r requirements.txt -i %MIRROR%
if %errorlevel% equ 0 (
    echo ✅ 使用requirements.txt安装成功！
    goto success
)

echo ❌ requirements.txt安装失败，尝试备用方案...

REM 方式2：使用备用requirements文件
echo 🔧 尝试使用备用requirements文件...
pip install -r requirements-alternative.txt -i %MIRROR%
if %errorlevel% equ 0 (
    echo ✅ 使用备用requirements文件安装成功！
    goto success
)

echo ❌ 备用方案也失败，请检查网络连接或手动安装
pause
exit /b 1

:success
echo ✅ 所有依赖安装完成！
echo 🚀 现在可以运行 python app.py 启动应用
pause 