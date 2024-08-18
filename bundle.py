import PyInstaller.__main__
import os

package_name = 'test'
output_dir = './bin'
entry_point = os.path.join('src', 'main.py')

# TODO - アイコンを設定する
PyInstaller.__main__.run([
    f'--name={package_name}',
    f'--distpath={output_dir}',
    '--onefile',
    '--windowed',
    entry_point,
])
