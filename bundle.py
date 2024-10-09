import os
import subprocess
import sys

group = 'Secineralyr'
group_copyright = '2024 Secineralyr/Dream'
package_name = 'Cotonestrum'
description = 'dm emoji moderation tool'
version = '0.0.2'

output_dir = './bin'
entry_point = os.path.join('src', 'main.py')
icon_filename = 'src/assets/icon_windows.ico'

icon_path = os.path.join(os.path.dirname(__file__), icon_filename)
file_version = f'{version}.0'

cp = subprocess.run(
    [
        'flet',
        'pack',
        f'--icon={icon_path}',
        f'--name={package_name}',
        f'--distpath={output_dir}',
        f'--product-name={package_name}',
        f'--file-description={description}',
        f'--product-version={version}',
        f'--file-version={file_version}',
        f'--company-name={group}',
        f'--copyright={group_copyright}',
        '-y',
        entry_point,
    ],
    encoding='utf8',
)

if cp.returncode != 0:
    print('ls failed.', file=sys.stderr)
    sys.exit(1)
