import os
import subprocess
import sys
import shutil

def build_windows_app():
    print("Starting Windows Node Agent Build Process...")
    
    # Check if pyinstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
    # Check if pystray is installed
    try:
        import pystray
    except ImportError:
        print("Installing pystray...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pystray", "pillow"])

    # Clean previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist/AverraNodeWindows'):
        shutil.rmtree('dist/AverraNodeWindows')
        
    # Build with PyInstaller
    print("Running PyInstaller...")
    
    # We need to collect uvicorn and starlette/fastapi hidden imports just like Mac
    hidden_imports = [
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'uvicorn.lifespan.off',
        'fastapi',
        'starlette',
        'anyio'
    ]
    
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--windowed", # Don't open a console window
        "--name=AverraNodeWindows",
        "--icon=NONE", # We could provide an .ico file here
    ]
    
    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])
        
    cmd.append("AverraNodeWindows.py")
    
    subprocess.check_call(cmd)
    
    print("Build complete! The executable is located at dist/AverraNodeWindows/AverraNodeWindows.exe")
    print("In a real environment, you would use NSIS or InnoSetup to wrap this directory into an installer.")

if __name__ == "__main__":
    build_windows_app()
