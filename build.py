import PyInstaller.__main__
import os
import shutil

def build_app():
    print("🚀 Iniciando proceso de compilación para TTS Narrador Pro...")

    # Limpiar compilaciones previas
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')

    # Argumentos de PyInstaller
    # Usamos el archivo .spec que ya tiene toda la configuración avanzada
    args = [
        'main.spec',
        '--noconfirm',
        '--clean'
    ]

    # Ejecutar PyInstaller
    PyInstaller.__main__.run(args)

    print("\n✅ Compilación finalizada.")
    print("📂 El ejecutable se encuentra en: dist/TTS_Narrador_Pro/TTS_Narrador_Pro.exe")

if __name__ == "__main__":
    build_app()
