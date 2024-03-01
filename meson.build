project('norka',
          version: '1.1.0',
    meson_version: '>= 0.62.0',
  default_options: [ 'warning_level=2', 'werror=false', ],
)

author = 'tenderowl'
domain = 'com.github'
gitrepo = 'https://github.com/'+author+'/'+meson.project_name()
website = 'https://tenderowl.com'
appid = '.'.join([domain, author, meson.project_name()])

i18n = import('i18n')
pymod = import('python')
gnome = import('gnome')

python = pymod.find_installation('python3')

# Dependencies
dependency('glib-2.0', version: '>= 2.70')
dependency('gio-2.0', version: '>= 2.70')
dependency('gtk4', version :'>=4.12')
dependency('libadwaita-1', version :'>=1.4')
dependency('gtksourceview-5')
dependency('webkitgtk-6.0', version: '>= 2.42.0')

prefix = get_option('prefix')
bindir = get_option('bindir')
datadir = get_option('datadir')
pkgdatadir = join_paths(prefix, datadir, meson.project_name())
pythondir = join_paths(prefix, python.get_install_dir())
localedir = join_paths(prefix, get_option('localedir'))

conf = configuration_data()
conf.set('PACKAGE_URL', 'https://tenderowl.com/norka/')
conf.set('DATA_DIR', get_option('datadir'))
conf.set('LOCALE_DIR', localedir)
conf.set('PYTHON_DIR', pythondir)
conf.set('PROJECT_NAME', meson.project_name())
conf.set('VERSION', meson.project_version())
conf.set('PYTHON', python.full_path())
conf.set('PKGDATA_DIR', pkgdatadir)
conf.set('appid', appid)

subdir('bin')
subdir('data')
subdir('po')

install_subdir(
  meson.project_name(),
  install_dir: pythondir
)

meson.add_install_script('build-aux/meson/postinstall.py')
