project('com.github.tenderowl.norka',
  version: '0.4.3',
  meson_version: '>= 0.49.0'
)

revision = run_command('bin/revision.sh').stdout().strip()
if revision == ''
  revision=meson.project_version()
endif

i18n = import('i18n')
python = import('python3')

message('Looking for dependencies')
python3 = python.find_python()
if not python3.found()
    error('No valid python3 binary found')
else
    message('Found python3 binary')
endif

# Dependencies
dependency('gtk+-3.0', version: '>= 3.22')
dependency('glib-2.0')
dependency('granite', version: '>= 4.0')
dependency('gtksourceview-3.0')
dependency('gtkspell3-3.0')

find_program('glib-compile-schemas', required: true)
find_program('gtk-update-icon-cache', required: false)
find_program('update-desktop-database', required: false)

gettext_package = meson.project_name()
localedir = join_paths(get_option('prefix'), get_option('localedir'))
pythondir = join_paths(get_option('prefix'), python.sysconfig_path('purelib'))
datadir = get_option('datadir')
pkgdatadir = join_paths(get_option('prefix'), datadir, meson.project_name())
podir = meson.source_root() / 'po'

conf = configuration_data()
conf.set('PACKAGE_URL', 'https://tenderowl.com/norka/')
conf.set('DATA_DIR', get_option('datadir'))
conf.set('LOCALE_DIR', localedir)
conf.set('PYTHON_DIR', pythondir)
conf.set('PROJECT_NAME', meson.project_name())
conf.set('VERSION', meson.project_version())
conf.set('REVISION', revision)
conf.set('PYTHON', python3.path())
conf.set('PKGDATA_DIR', pkgdatadir)

subdir('data')
subdir('po')

install_subdir(
  'norka',
  install_dir: pythondir
)

message('Preparing init file')
configure_file(
  input: 'norka/norka.in',
  output: meson.project_name(),
  configuration: conf,
  install_dir: get_option('bindir')
)

meson.add_install_script('build-aux/meson/postinstall.py')
