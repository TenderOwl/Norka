# Norka

[![Please do not theme this app](https://stopthemingmy.app/badge.svg)](https://stopthemingmy.app)
[![Build Status](https://github.com/tenderowl/Norka/workflows/CI/badge.svg)](https://github.com/tenderowl/Norka/action)
[![norka](https://snapcraft.io//norka/badge.svg)](https://snapcraft.io/norka)
[![norka](https://snapcraft.io//norka/trending.svg?name=0)](https://snapcraft.io/norka)
<a href="https://liberapay.com/tenderowl/donate"><img src="https://img.shields.io/liberapay/patrons/tenderowl.svg?logo=liberapay"></a>

<div align="center">
  <span align="center"> <img width="80" height="70" class="center" src="https://github.com/tenderowl/norka/blob/master/data/icons/com.github.tenderowl.norka.svg" alt="Icon"></span>
  <h1 align="center">Norka</h1>
  <h3 align="center">Continuous text editing for everyone</h3>
</div>

While I'm not the UX-man and it's just a hobby, I try to create visually appealing applications. And Norka is one of my trials to create a cozy text editor for GNOME and elementary OS exactly. 

Markdown for markup; No files until you need it; Your notes always saved and can be exported in a moment.

<div align="center">
  <img class="center" alt="Norka" src="data/screenshots/app_screenshot.png" />
</div>

## Features

* Markdown support
* Text search
* Autosave
* Document previews in a grid
* Reading time
* Drag-n-drop import local files
* Spell checking
* Export to files
* Export to Medium.com
* Export to Write.as
* Different color schemes for editor
* Document archiving
* And of course, you can delete them permanently

Read more on [tenderowl.com/norka](https://tenderowl.com/norka).

## Installation

### Flathub
<a href="https://flathub.org/apps/details/com.github.tenderowl.norka"><img height="50" alt="Download on Flathub" src="https://flathub.org/assets/badges/flathub-badge-en.png"/></a>

### Snap Store

<a href="https://snapcraft.io/norka">
  <img height="50" alt="Get it from the Snap Store" src="https://snapcraft.io/static/images/badges/en/snap-store-black.svg" />
</a>

### elementary OS AppCenter
<a href="https://appcenter.elementary.io/com.github.tenderowl.norka"><img src="https://appcenter.elementary.io/badge.svg?new" alt="Get it on AppCenter" /></a>

## :tada: Support
If you like Norka and you want to support its development, consider donating via Liberapay:  
<a href="https://liberapay.com/tenderowl/donate"><img alt="Donate using Liberapay" src="https://liberapay.com/assets/widgets/donate.svg"></a>


## Tech part

Text editor built for GNOME on top of [PyGObject](https://pygobject.readthedocs.io/en/latest/), Python 3 and GTK+ 3. Project under development so it will be massively changing in time :)


## Building

Build time requirements:

- meson (>= 0.49)
- python3 (>= 3.6)
- intltool
- libgranite-dev
- libgtk-3-dev (>= 3.10)
- libgspell-1-dev
- libgtksourceview-4.0-dev (>= 3.24.3)
- libwebkit2gtk-4.0
- python3-gi
- python3-gi-cairo
- gir1.2-gspell-1
- gir1.2-gtksource-3.0
- gir1.2-granite-1.0
- gir1.2-webkit2-4.0


Run meson build to configure the build environment. Change to the build directory and run `ninja` to build:

```
meson build --prefix=/usr
ninja -C build
```

To install, use `ninja install`, then execute with `com.github.tenderowl.norka`:

```
sudo ninja -C build install
com.github.tenderowl.norka
```


## Afterword

That's all. If you want to see any features or push any changes - just submit a PR or create an issue.

Brought to you by Tender Owl :owl:

