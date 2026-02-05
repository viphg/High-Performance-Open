@echo off
setlocal enabledelayedexpansion

echo ========================================
echo High-Performance 版本基线保护设置
echo ========================================
echo.

:: 检查Git是否安装
echo [1/8] 检查Git环境...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git未安装，请先安装Git: https://git-scm.com/
    pause
    exit /b 1
)
echo ✅ Git已安装

:: 进入项目目录
echo [2/8] 进入项目目录...
cd /d "D:\OPENPROJECT\High-Performance-Open"
if %errorlevel% neq 0 (
    echo ❌ 无法进入项目目录
    pause
    exit /b 1
)
echo ✅ 项目目录: %CD%

:: 初始化Git仓库
echo [3/8] 初始化Git仓库...
if not exist ".git" (
    git init
    if %errorlevel% neq 0 (
        echo ❌ Git初始化失败
        pause
        exit /b 1
    )
    echo ✅ Git仓库初始化成功
) else (
    echo ⚠️  Git仓库已存在，跳过初始化
)

:: 配置Git用户信息
echo [4/8] 配置Git用户信息...
git config user.name "High-Performance Developer"
git config user.email "developer@highperformance.com"
echo ✅ Git用户配置完成

:: 添加所有文件
echo [5/8] 添加文件到Git...
git add .
if %errorlevel% neq 0 (
    echo ❌ 添加文件失败
    pause
    exit /b 1
)
echo ✅ 文件添加成功

:: 创建初始提交
echo [6/8] 创建初始提交...
git commit -m "feat: v1.0.0 baseline - 完整的任务管理平台"
if %errorlevel% neq 0 (
    echo ❌ 提交创建失败
    pause
    exit /b 1
)
echo ✅ 初始提交创建成功

:: 创建基线标签
echo [7/8] 创建v1.0.0基线标签...
git tag -a v1.0.0 -m "Production baseline - 完整的任务管理平台"
if %errorlevel% neq 0 (
    echo ❌ 标签创建失败
    pause
    exit /b 1
)
echo ✅ v1.0.0基线标签创建成功

:: 创建分支结构
echo [8/8] 创建分支结构...
git checkout -b develop
git checkout -b feature/intelligent-recommendations
if %errorlevel% neq 0 (
    echo ❌ 分支创建失败
    pause
    exit /b 1
)
echo ✅ 分支结构创建成功

:: 显示最终状态
echo.
echo ========================================
echo 🎉 版本基线保护设置完成！
echo ========================================
echo.

:: 显示Git状态
echo 📊 Git状态信息:
git branch -a
echo.
echo 📋 最近提交:
git log --oneline -3
echo.
echo 🏷️  标签列表:
git tag -l
echo.

:: 创建备份目录
if not exist "backups" mkdir backups

echo 📁 备份目录已创建: backups\
echo.
echo 🔄 下一步操作:
echo 1. 运行备份系统: python scripts\backup_system.py --create-backup --version v1.0.0
echo 2. 创建开发环境配置: copy .env.example .env.dev
echo 3. 开始智能推荐功能开发
echo.
pause