# cleanup.py - 智能清理脚本（不会删除重要文件）
import os
import shutil
import glob

def safe_cleanup():
    """安全清理，只删除缓存文件，保留你的代码和数据"""
    
    # 要清理的缓存文件类型
    cache_patterns = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        ".pytest_cache",
        ".mypy_cache",
        ".vscode/settings.json",  # 只删设置，不删整个文件夹
        "*.log",
        "pip-log.txt"
    ]
    
    # 要保留的重要文件
    important_files = [
        "my_app.py",
        "my_data.csv", 
        "requirements.txt",
        "cleanup.py",
        "README.md"
    ]
    
    print("🧹 开始安全清理...")
    
    # 清理Python缓存
    for pattern in cache_patterns:
        for file_path in glob.glob(f"**/{pattern}", recursive=True):
            try:
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    print(f"✅ 删除文件夹: {file_path}")
                else:
                    os.remove(file_path)
                    print(f"✅ 删除文件: {file_path}")
            except Exception as e:
                print(f"⚠️ 无法删除: {file_path} - {e}")
    
    # 清理Streamlit缓存
    streamlit_cache = os.path.expanduser("~/.streamlit")
    if os.path.exists(streamlit_cache):
        try:
            shutil.rmtree(streamlit_cache)
            print("✅ 清理Streamlit缓存")
        except:
            pass
    
    print("🎉 清理完成！你的代码和数据都完好无损")

if __name__ == "__main__":
    safe_cleanup()
