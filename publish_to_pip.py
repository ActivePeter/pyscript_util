#!/usr/bin/env python3
"""
PyPI发布脚本 - pyscript_util
自动化构建、检查和发布到PyPI的完整流程
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# 适配系统选择python命令
pythoncmd = "python3"
if sys.platform == "win32":
    pythoncmd = "python"

def run_command(cmd, check=True, shell=True):
    """执行命令并处理输出"""
    print(f"🔧 执行命令: {cmd}")
    result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
    
    if result.stdout:
        print(f"📝 输出: {result.stdout}")
    if result.stderr:
        print(f"⚠️ 错误输出: {result.stderr}")
    
    if check and result.returncode != 0:
        print(f"❌ 命令执行失败: {cmd}")
        sys.exit(1)
    
    return result

def check_requirements():
    """检查发布所需的工具"""
    print("🔍 检查发布工具...")
    required_tools = ['twine', 'build']
    
    for tool in required_tools:
        result = run_command(f"{pythoncmd} -m pip show {tool}", check=False)
        if result.returncode != 0:
            print(f"⚠️ 缺少工具 {tool}，正在安装...")
            run_command(f"{pythoncmd} -m pip install {tool}")
    
    print("✅ 发布工具检查完成")

def clean_build_dirs():
    """清理构建目录"""
    print("🧹 清理构建目录...")
    dirs_to_clean = ['build', 'dist', '*.egg-info']
    
    for pattern in dirs_to_clean:
        if '*' in pattern:
            # 处理通配符
            import glob
            for path in glob.glob(pattern):
                if os.path.exists(path):
                    shutil.rmtree(path)
                    print(f"   删除: {path}")
        else:
            if os.path.exists(pattern):
                shutil.rmtree(pattern)
                print(f"   删除: {pattern}")
    
    print("✅ 构建目录清理完成")

def get_version():
    """从setup.py获取版本号"""
    import re
    with open('setup.py', 'r', encoding='utf-8') as f:
        content = f.read()
        match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
    return "unknown"

def build_package():
    """构建包"""
    print("📦 构建包...")
    run_command(f"{pythoncmd} -m build")
    print("✅ 包构建完成")

def check_package():
    """检查包的质量"""
    print("🔍 检查包质量...")
    
    # 检查dist目录下的文件
    dist_files = list(Path('dist').glob('*'))
    if not dist_files:
        print("❌ 没有找到构建的包文件")
        sys.exit(1)
    
    print("📋 构建的文件:")
    for file in dist_files:
        print(f"   {file}")
    
    # 使用twine检查包
    run_command(f"{pythoncmd} -m twine check dist/*")
    print("✅ 包质量检查完成")

def upload_to_testpypi():
    """上传到TestPyPI进行测试"""
    print("🧪 上传到TestPyPI...")
    print("⚠️ 请确保你已经配置了TestPyPI的API token")
    
    confirm = input("是否要上传到TestPyPI进行测试? (y/N): ").strip().lower()
    if confirm in ['y', 'yes']:
        run_command(f"{pythoncmd} -m twine upload --repository testpypi dist/*")
        print("✅ 已上传到TestPyPI")
        print("🔗 查看: https://test.pypi.org/project/pyscript-util/")
        return True
    else:
        print("⏭️ 跳过TestPyPI上传")
        return False

def upload_to_pypi():
    """上传到正式PyPI"""
    print("🚀 上传到正式PyPI...")
    print("⚠️ 请确保你已经配置了PyPI的API token")
    
    version = get_version()
    print(f"📌 当前版本: {version}")
    
    confirm = input("确认要发布到正式PyPI吗? (y/N): ").strip().lower()
    if confirm in ['y', 'yes']:
        run_command(f"{pythoncmd} -m twine upload dist/*")
        print("✅ 已发布到PyPI!")
        print(f"🔗 查看: https://pypi.org/project/pyscript-util/")
        print(f"📦 安装命令: pip install pyscript-util=={version}")
        return True
    else:
        print("❌ 取消发布")
        return False

def main():
    """主函数"""
    print("🚀 pyscript_util PyPI发布脚本")
    print("=" * 50)
    print(f"🐍 使用Python命令: {pythoncmd}")
    
    # 检查是否在正确的目录
    if not os.path.exists('setup.py'):
        print("❌ 未找到setup.py文件，请在项目根目录运行此脚本")
        sys.exit(1)
    
    try:
        # 1. 检查工具
        check_requirements()
        
        # 2. 清理构建目录
        clean_build_dirs()
        
        # 3. 构建包
        build_package()
        
        # 4. 检查包质量
        check_package()
        
        # 5. 选择发布目标
        print("\n📋 发布选项:")
        print("1. 仅测试 (TestPyPI)")
        print("2. 测试 + 正式发布 (TestPyPI -> PyPI)")
        print("3. 直接正式发布 (PyPI)")
        print("4. 退出")
        
        choice = input("请选择 (1-4): ").strip()
        
        if choice == "1":
            upload_to_testpypi()
        elif choice == "2":
            if upload_to_testpypi():
                input("按回车键继续发布到正式PyPI...")
                upload_to_pypi()
        elif choice == "3":
            upload_to_pypi()
        elif choice == "4":
            print("👋 退出发布流程")
        else:
            print("❌ 无效选择")
            sys.exit(1)
        
        print("\n🎉 发布流程完成!")
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 