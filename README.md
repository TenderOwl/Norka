# Norka

[![Build Status](https://travis-ci.com/TenderOwl/Norka.svg?branch=master)](https://travis-ci.com/TenderOwl/Norka)
[![Please do not theme this app](https://stopthemingmy.app/badge.svg)](https://stopthemingmy.app) 

<p align="center">
<a href="https://appcenter.elementary.io/com.github.tenderowl.norka"><img src="https://appcenter.elementary.io/badge.svg" alt="Get it on AppCenter"></a>
<br/>
<a href="https://flathub.org/apps/details/com.github.tenderowl.norka" class="text-center"><img alt="Download on Flathub" src="https://flathub.org/assets/badges/flathub-badge-en.png" width="240"></a>
</p>

## Preface

While I'm not the UX-man and it's just a hobby, I try to create visually appealing applications. And Norka is one of my trials to create a cozy text editor for GNOME and Elementary OS exactly. 

Markdown for markup, no files, your data always saved and can be exported in a moment.

![Norka](data/screenshots/app_screenshot.png)

# Features

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

## Tech part

Text editor built for GNOME on top of [PyGObject](https://pygobject.readthedocs.io/en/latest/), Python 3 and GTK+ 3. Project under development so it will be massively changing in time :)


## Building

Build time requirements:

- gtk3 >= 3.20
- gtkspell3-3.0
- granite >= 5.4
- python3 >= 3.6
- python-sqlite
- python-gobject
- meson >= 0.49
- ninja

## Installing

Use meson and ninja to build and install Norka through terminal commands:

```bash
meson build
ninja -C build install
```

### AppCenter / Flathub

<p align="center">
<a href="https://appcenter.elementary.io/com.github.tenderowl.norka"><img src="https://appcenter.elementary.io/badge.svg" alt="Get it on AppCenter"></a>
<br/>
<a href="https://flathub.org/apps/details/com.github.tenderowl.norka" class="text-center"><img alt="Download on Flathub" src="https://flathub.org/assets/badges/flathub-badge-en.png" width="240"></a>
</p>


# Afterword

That's all. If you want to see any features or push any changes - just submit a PR or create an issue.

See ya!

