project('saturn', 'c', version: '0.1', default_options: ['warning_level=3'])

gtkdep = dependency('gtk+-3.0')

py_installation = import('python').find_installation('python3')

# Install the Python script to the bin directory
py_installation.install_sources('src/main.py',
  subdir: get_option('bindir'),
  install_tag: 'runtime')

# Run PyInstaller to create standalone executable
pyinstaller_cmd = [
  py_installation.path(), '-m', 'PyInstaller',
  '--onefile',
  '--name=saturn',
  '--distpath=dist'
]

pyinstaller_cmd += ['../src/main.py']

run_pyinstaller = custom_target('run_pyinstaller',
  input: ['src/main.py'],
  output: 'saturn',
  command: pyinstaller_cmd,
  build_by_default: true,
  install: true,
  install_dir: get_option('bindir')
)
