gnome = import('gnome')

message('Compiling resources')

gnome.compile_resources(
  meson.project_name(),
  meson.project_name() + '.gresource.xml',
  gresource_bundle: true,
  source_dir: '.',
  install_dir: pkgdatadir,
  install: true,
)

desktop_conf = configuration_data()
desktop_conf.set('project_name', meson.project_name())
desktop_conf.set('icon', meson.project_name())

desktop_file = i18n.merge_file(
  input: configure_file(
    input: 'com.github.tenderowl.norka.desktop.in.in',
    output: '@BASENAME@',
    configuration: desktop_conf
  ),
  output: '@0@.desktop'.format(meson.project_name()),
  type: 'desktop',
  po_dir: '../po',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'applications')
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils,
    args: [desktop_file]
  )
endif

appstream_file = i18n.merge_file(
  input: 'com.github.tenderowl.norka.appdata.xml.in',
  output: '@0@.appdata.xml'.format(meson.project_name()),
  po_dir: '../po',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'metainfo')
)

appstream_util = find_program('appstream-util', required: false)
if appstream_util.found()
  test('Validate appstream file', appstream_util,
    args: ['validate', appstream_file]
  )
endif

install_data('com.github.tenderowl.norka.gschema.xml',
  install_dir: join_paths(get_option('datadir'), 'glib-2.0/schemas')
)

compile_schemas = find_program('glib-compile-schemas', required: false)
if compile_schemas.found()
  test('Validate schema file', compile_schemas,
    args: ['--strict', '--dry-run', meson.current_source_dir()]
  )
endif

message('Making a list of icons')
subdir('icons')

message('Installing style schemes')

install_data(
    join_paths('schemes', 'norka.xml'),
    install_dir: join_paths(get_option('datadir'), 'gtksourceview-4', 'styles')
)

install_data(
    join_paths('schemes', 'norka-sepia.xml'),
    install_dir: join_paths(get_option('datadir'), 'gtksourceview-4', 'styles')
)

install_data(
    join_paths('schemes', 'norka-dark.xml'),
    install_dir: join_paths(get_option('datadir'), 'gtksourceview-4', 'styles')
)
