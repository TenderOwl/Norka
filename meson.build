project('norka',
          version: '2.0.0',
    meson_version: '>= 1.5.0',
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
dependency('glib-2.0', version: '>= 2.76')
dependency('gio-2.0', version: '>= 2.76')
dependency('gobject-introspection-1.0', version: '>=1.66.0')
dependency('gtk4', version: '>=4.16')
dependency('libadwaita-1', version: '>=1.7')
dependency('gtksourceview-5', version: '>= 5.6')

prefix = get_option('prefix')
bindir = get_option('bindir')
datadir = get_option('datadir')
pkgdatadir = join_paths(prefix, datadir, meson.project_name())
pythondir = join_paths(prefix, python.get_install_dir())
localedir = join_paths(prefix, get_option('localedir'))

if get_option('profile') == 'development'
  profile = 'Devel'
  vcs_tag = run_command(
    ['git', 'rev-parse', '--short', 'HEAD'],
    check: false
  ).stdout().strip()
  if vcs_tag == ''
    version_suffix = '-devel'
  else
    version_suffix = '-@0@'.format (vcs_tag)
  endif
else
  profile = ''
  version_suffix = ''
endif


conf = configuration_data()
conf.set('PACKAGE_URL', 'https://tenderowl.com/norka/')
conf.set('DATA_DIR', get_option('datadir'))
conf.set('LOCALE_DIR', localedir)
conf.set('PYTHON_DIR', pythondir)
conf.set('PROJECT_NAME', meson.project_name())
conf.set('VERSION', meson.project_version())
conf.set('PROFILE', profile)
conf.set('PYTHON', python.full_path())
conf.set('PKGDATA_DIR', pkgdatadir)
conf.set('APP_ID', appid)

subdir('bin')
subdir('data')
subdir('po')

install_subdir(
  meson.project_name(),
  install_dir: pythondir
)

meson.add_install_script('build-aux/meson/postinstall.py')
