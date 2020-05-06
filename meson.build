project('com.github.tenderowl.norka',
  version: '0.1.0',
  meson_version: '>= 0.50.0'
)

i18n = import('i18n')
python = import('python3')

# Dependencies
dependency('gtk+-3.0', version: '>= 3.22')
dependency('granite', version: '>= 4.0')


subdir('data')
# subdir('src')
subdir('po')

meson.add_install_script('build-aux/meson/postinstall.py')