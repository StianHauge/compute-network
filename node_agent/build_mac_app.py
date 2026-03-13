import PyInstaller.__main__
import os

if __name__ == "__main__":
    app_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(app_dir, "mac_app.py")
    
    print("Building stand-alone macOS Application for Averra Node...")
    
    PyInstaller.__main__.run([
        main_script,
        '--name=AverraNode',
        '--windowed', # This is critical for macOS UI apps (prevent terminal from opening)
        '--noconfirm',
        '--clean',
        '--log-level=WARN',
        '--collect-all=uvicorn',
        '--collect-all=fastapi',
        '--collect-all=starlette',
        '--collect-all=anyio',
        '--collect-all=pydantic'
    ])
    print("Build complete! Check the /dist folder for AverraNode.app")
