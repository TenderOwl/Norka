message('Compiling resources')

blueprints = custom_target('blueprints',
  input: files(
    'ui/documents_grid_context_menu.blp',
    'ui/shortcuts.blp',
    'ui/format_shortcuts_window.blp',
    'ui/headerbar.blp',
    'ui/main_window.blp',
    'ui/preferences_window.blp',
    'ui/preview_window.blp',
    'ui/stats.blp',
  ),
  output: '.',
  command: [find_program('blueprint-compiler'), 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)

gnome.compile_resources(appid,
  appid + '.gresource.xml',
  dependencies: blueprints,
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

desktop_conf = configuration_data()
desktop_conf.set('project_name', meson.project_name())
desktop_conf.set('icon', appid)

desktop_file = i18n.merge_file(
  input: configure_file(
    input: appid + '.desktop.in.in',
    output: appid + '.desktop.in',
    configuration: desktop_conf
  ),
  output: appid + '.desktop',
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
  input: appid + '.appdata.xml.in',
  output: appid  + '.appdata.xml',
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

install_data(appid + '.gschema.xml',
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
color_schemes = ['norka-dark', 'norka-sepia', 'norka']

foreach i : color_schemes
    install_data(
        join_paths('schemes', i + '.xml'),
       install_dir: join_paths(get_option('datadir'), 'gtksourceview-4', 'styles')
    )
endforeach


message('Installing custom fonts')
install_subdir(
    join_paths('fonts', 'IBMPlexMono'),
    install_dir :join_paths('share','fonts')
)

install_subdir(
    join_paths('fonts', 'iA Writer Duospace'),
    install_dir : join_paths('share','fonts')
)
