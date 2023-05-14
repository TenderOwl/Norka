# export.py
#
# MIT License
#
# Copyright (c) 2020 Andrey Maksimov <meamka@ya.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import os

import markdown2
from gi.repository import Gtk, WebKit, GObject
from htmldocx import HtmlToDocx

from norka.models.document import Document


class Exporter:

    @staticmethod
    def write_to_file(path: str, text: str) -> None:
        with open(path, "w+", encoding="utf-8") as output:
            output.write(text)

    @staticmethod
    def export_markdown(path: str, document: Document) -> str:
        Exporter.write_to_file(path, document.content)
        return path

    @staticmethod
    def export_html(path: str, document: Document) -> str:
        html = Exporter.render_html(document.content, document.title)
        Exporter.write_to_file(path, html)
        return path

    @staticmethod
    def export_html_preview(path: str, text: str, dark_mode=False) -> str:
        html = Exporter.render_html(text, '', dark_mode=dark_mode)
        return html
        # Exporter.write_to_file(path, html)
        # return path

    @staticmethod
    def export_plaintext(path: str, document: Document) -> str:
        # markdown = markdown2.markdown()
        plaintext = document.content
        Exporter.write_to_file(path, plaintext)
        return path

    @staticmethod
    def export_pdf(path: str, document: Document) -> str:
        print('export pdf to ', path)

        html = Exporter.render_html(document.content, document.title)
        print('html rendered')

        pdf_exporter = PDFExporter(path, html)
        pdf_exporter.print()

        return path

    @staticmethod
    def export_docx(path: str, document: Document) -> str:
        html = Exporter.render_html(document.content, document.title)
        html_parser = HtmlToDocx()
        docx = html_parser.parse_html_string(html)
        docx.save(path)
        return path

    @staticmethod
    def render_html(text: str, title: str = None, dark_mode=False) -> str:
        dark_class = "class='dark'" if dark_mode else ""
        data = markdown2.markdown(text, extras=['cuddled-lists', 'fenced-code-blocks', 'smarty-pants'
                                                                                       'strike', 'tables', 'footnotes',
                                                'task_list', 'toc'])
        html = f"<!doctype html><html lang=en><head><meta charset=utf-8><title>{title or ''}</title>" + \
               """<style>
               *,:after,:before{-webkit-box-sizing:border-box;box-sizing:border-box}:after,:before{text-decoration:inherit;vertical-align:inherit}html{cursor:default;line-height:1.5;-moz-tab-size:4;-o-tab-size:4;tab-size:4;-webkit-tap-highlight-color:transparent;-ms-text-size-adjust:100%;-webkit-text-size-adjust:100%;word-break:break-word}body{margin:0}h1{font-size:2em;margin:.67em 0}dl dl,dl ol,dl ul,ol dl,ol ol,ol ul,ul dl,ul ol,ul ul{margin:0}nav ol,nav ul{list-style:none;padding:0}pre{font-family:monospace,monospace;font-size:1em}abbr[title]{text-decoration:underline;-webkit-text-decoration:underline dotted;text-decoration:underline dotted}b,strong{font-weight:bolder}code,kbd,samp{font-family:monospace,monospace;font-size:1em}small{font-size:80%}audio,canvas,iframe,img,svg,video{vertical-align:middle}audio,video{display:inline-block}audio:not([controls]){display:none;height:0}iframe,img{border-style:none}svg:not([fill]){fill:currentColor}svg:not(:root){overflow:hidden}table{border-collapse:collapse}button,input,select{margin:0}button{overflow:visible;text-transform:none}[type=button],[type=reset],[type=submit],button{-webkit-appearance:button}fieldset{border:1px solid #a0a0a0;padding:.35em .75em .625em}input{overflow:visible}legend{color:inherit;display:table;max-width:100%;white-space:normal}progress{display:inline-block;vertical-align:baseline}select{text-transform:none}textarea{margin:0}[type=checkbox],[type=radio]{padding:0}[type=search]{-webkit-appearance:textfield;outline-offset:-2px}::-webkit-inner-spin-button,::-webkit-outer-spin-button{height:auto}::-webkit-input-placeholder{color:inherit;opacity:.54}::-webkit-search-decoration{-webkit-appearance:none}::-webkit-file-upload-button{-webkit-appearance:button;font:inherit}::-moz-focus-inner{border-style:none;padding:0}:-moz-focusring{outline:1px dotted ButtonText}:-moz-ui-invalid{box-shadow:none}details,dialog{display:block}dialog{background-color:#fff;border:solid;color:#000;height:-moz-fit-content;height:-webkit-fit-content;height:fit-content;left:0;margin:auto;padding:1em;position:absolute;right:0;width:-moz-fit-content;width:-webkit-fit-content;width:fit-content}dialog:not([open]){display:none}summary{display:list-item}canvas{display:inline-block}template{display:none}[tabindex],a,area,button,input,label,select,summary,textarea{-ms-touch-action:manipulation;touch-action:manipulation}[hidden]{display:none}[aria-busy=true]{cursor:progress}[aria-controls]{cursor:pointer}[aria-disabled=true],[disabled]{cursor:not-allowed}[aria-hidden=false][hidden]{display:initial}[aria-hidden=false][hidden]:not(:focus){clip:rect(0,0,0,0);position:absolute}/*! Marx v3.0.6 - The classless CSS reset (perfect for Communists) | MIT License | https://github.com/mblode/marx */article,aside,details,footer,header,main,section,summary{margin:0 auto 16px;width:100%}main{display:block;margin:0 auto;max-width:768px;padding:0 16px 16px}footer{border-top:1px solid rgba(0,0,0,.12);padding:16px 0;text-align:center}footer p{margin-bottom:0}hr{border:0;border-top:1px solid rgba(0,0,0,.12);display:block;margin-top:16px;margin-bottom:16px;width:100%;-webkit-box-sizing:content-box;box-sizing:content-box;height:0;overflow:visible}img{height:auto;max-width:100%;vertical-align:baseline}@media screen and (max-width:400px){article,aside,section{clear:both;display:block;max-width:100%}img{margin-right:16px}}embed,iframe,video{border:0}body{color:rgba(0,0,0,.8);font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica Neue,Arial,sans-serif,Apple Color Emoji,Segoe UI Emoji,Segoe UI Symbol;font-size:16px;line-height:1.5}p{margin:0 0 16px}h1,h2,h3,h4,h5,h6{color:inherit;font-family:inherit;line-height:1.2;font-weight:500}h1{font-size:40px}h1,h2{margin:20px 0 16px}h2{font-size:32px}h3{font-size:28px}h3,h4{margin:16px 0 4px}h4{font-size:24px}h5{font-size:20px}h5,h6{margin:16px 0 4px}h6{font-size:16px}small{color:rgba(0,0,0,.54);vertical-align:bottom}pre{background:#f7f7f9;display:block;margin:16px 0;padding:16px;white-space:pre-wrap;overflow-wrap:break-word}code,pre{color:rgba(0,0,0,.8);font-family:Menlo,Monaco,Consolas,Courier New,monospace;font-size:16px}code{line-height:inherit;margin:0;padding:0;vertical-align:baseline;word-break:break-all;word-wrap:break-word}a{color:#007bff;text-decoration:none;background-color:rgba(0,0,0,0)}a:focus,a:hover{color:#0062cc;text-decoration:underline}dl{margin-bottom:16px}dd{margin-left:40px}ol,ul{margin-bottom:8px;padding-left:40px;vertical-align:baseline}blockquote{border-left:2px solid rgba(0,0,0,.8);font-style:italic;margin:16px 0;padding-left:16px}blockquote,figcaption{font-family:Georgia,Times,Times New Roman,serif}u{text-decoration:underline}s{text-decoration:line-through}sup{vertical-align:super}sub,sup{font-size:14px}sub{vertical-align:sub}mark{background:#ffeb3b}input[type=date],input[type=datetime-local],input[type=datetime],input[type=email],input[type=month],input[type=number],input[type=password],input[type=search],input[type=tel],input[type=text],input[type=time],input[type=url],input[type=week],select,textarea{background:#fff;background-clip:padding-box;border:1px solid rgba(0,0,0,.12);border-radius:4px;color:rgba(0,0,0,.8);display:block;width:100%;font-size:1rem;padding:8px 16px;line-height:1.5;-webkit-transition:border-color .15s ease-in-out,-webkit-box-shadow .15s ease-in-out;transition:border-color .15s ease-in-out,-webkit-box-shadow .15s ease-in-out;transition:border-color .15s ease-in-out,box-shadow .15s ease-in-out;transition:border-color .15s ease-in-out,box-shadow .15s ease-in-out,-webkit-box-shadow .15s ease-in-out;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica Neue,Arial,sans-serif,Apple Color Emoji,Segoe UI Emoji,Segoe UI Symbol}input[type=color]{background:#fff;border:1px solid rgba(0,0,0,.12);border-radius:4px;display:inline-block;vertical-align:middle}input:not([type]){-webkit-appearance:none;background:#fff;background-clip:padding-box;border:1px solid rgba(0,0,0,.12);border-radius:4px;color:rgba(0,0,0,.8);display:block;width:100%;padding:8px 16px;line-height:1.5;-webkit-transition:border-color .15s ease-in-out,-webkit-box-shadow .15s ease-in-out;transition:border-color .15s ease-in-out,-webkit-box-shadow .15s ease-in-out;transition:border-color .15s ease-in-out,box-shadow .15s ease-in-out;transition:border-color .15s ease-in-out,box-shadow .15s ease-in-out,-webkit-box-shadow .15s ease-in-out;text-align:left}input[type=color]:focus,input[type=date]:focus,input[type=datetime-local]:focus,input[type=datetime]:focus,input[type=email]:focus,input[type=month]:focus,input[type=number]:focus,input[type=password]:focus,input[type=search]:focus,input[type=tel]:focus,input[type=text]:focus,input[type=time]:focus,input[type=url]:focus,input[type=week]:focus,select:focus,textarea:focus{background-color:#fff;border-color:#80bdff;outline:0;-webkit-box-shadow:0 0 0 .2rem rgba(0,123,255,.25);box-shadow:0 0 0 .2rem rgba(0,123,255,.25)}input:not([type]):focus{background-color:#fff;border-color:#80bdff;outline:0;-webkit-box-shadow:0 0 0 .2rem rgba(0,123,255,.25);box-shadow:0 0 0 .2rem rgba(0,123,255,.25)}input[type=checkbox]:focus,input[type=file]:focus,input[type=radio]:focus{outline:1px thin rgba(0,0,0,.12)}input[type=color][disabled],input[type=date][disabled],input[type=datetime-local][disabled],input[type=datetime][disabled],input[type=email][disabled],input[type=month][disabled],input[type=number][disabled],input[type=password][disabled],input[type=search][disabled],input[type=tel][disabled],input[type=text][disabled],input[type=time][disabled],input[type=url][disabled],input[type=week][disabled],select[disabled],textarea[disabled]{background-color:rgba(0,0,0,.12);color:rgba(0,0,0,.54);cursor:not-allowed;opacity:1}input:not([type])[disabled]{background-color:rgba(0,0,0,.12);color:rgba(0,0,0,.54);cursor:not-allowed;opacity:1}input[readonly],select[readonly],textarea[readonly]{border-color:rgba(0,0,0,.12);color:rgba(0,0,0,.54)}input:focus:invalid,select:focus:invalid,textarea:focus:invalid{border-color:#ea1c0d;color:#f44336}input[type=checkbox]:focus:invalid:focus,input[type=file]:focus:invalid:focus,input[type=radio]:focus:invalid:focus{outline-color:#f44336}select{border:1px solid rgba(0,0,0,.12);vertical-align:sub}select:not([size]):not([multiple]){height:-webkit-calc(2.25rem + 2px);height:calc(2.25rem + 2px)}select[multiple]{height:auto}label{display:inline-block;line-height:2}fieldset{border:0;margin:0;padding:8px 0}legend{border-bottom:1px solid rgba(0,0,0,.12);color:rgba(0,0,0,.8);display:block;margin-bottom:8px;padding:8px 0;width:100%}textarea{overflow:auto;resize:vertical}input[type=checkbox],input[type=radio]{-webkit-box-sizing:border-box;box-sizing:border-box;padding:0;display:inline}button,input[type=button],input[type=reset],input[type=submit]{background-color:#007bff;border:#007bff;border-radius:4px;color:#fff;padding:8px 16px;display:inline-block;font-weight:400;text-align:center;white-space:nowrap;vertical-align:middle;-webkit-user-select:none;-moz-user-select:none;-ms-user-select:none;user-select:none;border:1px solid rgba(0,0,0,0);font-size:1rem;line-height:1.5;-webkit-transition:color .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,-webkit-box-shadow .15s ease-in-out;transition:color .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,-webkit-box-shadow .15s ease-in-out;transition:color .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out;transition:color .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out,-webkit-box-shadow .15s ease-in-out}button::-moz-focus-inner,input[type=button]::-moz-focus-inner,input[type=reset]::-moz-focus-inner,input[type=submit]::-moz-focus-inner{padding:0}button:hover,input[type=button]:hover,input[type=reset]:hover,input[type=submit]:hover{background-color:#0069d9;border-color:#0062cc;color:#fff}button:not(:disabled):active,input[type=button]:not(:disabled):active,input[type=reset]:not(:disabled):active,input[type=submit]:not(:disabled):active{background-color:#0062cc;border-color:#005cbf;color:#fff}button:focus,input[type=button]:focus,input[type=reset]:focus,input[type=submit]:focus{outline:0;-webkit-box-shadow:0 0 0 .2rem rgba(0,123,255,.5);box-shadow:0 0 0 .2rem rgba(0,123,255,.5)}button:disabled,input[type=button]:disabled,input[type=reset]:disabled,input[type=submit]:disabled{opacity:.65;cursor:not-allowed;background-color:#007bff;border-color:#007bff;color:#fff}table{border-top:1px solid rgba(0,0,0,.12);margin-bottom:16px}caption{padding:8px 0}thead th{border:0;border-bottom:2px solid rgba(0,0,0,.12);text-align:left}tr{margin-bottom:8px}td,th{border-bottom:1px solid rgba(0,0,0,.12);padding:16px;vertical-align:inherit}tfoot tr{text-align:left}tfoot td{color:rgba(0,0,0,.54);font-size:8px;font-style:italic;padding:16px 4px}
               :any-link {pointer-events: none !important;}
               body.dark { background: black; filter: invert(1) hue-rotate(180deg); }
               </style>
               </head>""" + \
               f"<body {dark_class}><main>" \
               + data + """</main></body></html>"""
        return html


class PDFExporter(GObject.GObject):
    __gtype_name__ = 'PDFExporter'
    __gsignals__ = {
        'finished': (GObject.SignalFlags.ACTION, None, (str,)),
    }
    web_view: WebKit.WebView

    def __init__(self, path: str, document: Document):
        GObject.GObject.__init__(self)
        self.path = path
        self.dir = os.path.dirname(path)
        self.basename = os.path.splitext(os.path.basename(path))[0]
        self.html = Exporter.render_html(document.content, document.title)
        self.web_view = WebKit.WebView()

    def on_load_changed(self, webview: WebKit.WebView, event: WebKit.LoadEvent):
        # When html is fully loaded then setup PrintOperation and print to PDF.
        print('PDFPrinter event: ', event)
        if event == WebKit.LoadEvent.FINISHED:
            print_settings = Gtk.PrintSettings()
            print_settings.set(Gtk.PRINT_SETTINGS_OUTPUT_BASENAME, self.basename)
            print_settings.set(Gtk.PRINT_SETTINGS_OUTPUT_DIR, self.dir)
            print_settings.set(Gtk.PRINT_SETTINGS_OUTPUT_FILE_FORMAT, "pdf")
            print_settings.set_quality(Gtk.PrintQuality.HIGH)
            print_settings.set_printer("Print to File")
            print('PDFPrinter preparing')

            operation: WebKit.PrintOperation = WebKit.PrintOperation.new(self.web_view)
            operation.set_print_settings(print_settings)
            operation.connect('finished', lambda op: self.emit('finished', self.path))
            operation.print_()
            print('PDFPrinter creating PDF')

    def print(self):
        self.web_view.connect('load-changed', self.on_load_changed)
        print('webview created')
        self.web_view.load_html(self.html)
        print('webview loading text')


class Printer(GObject.GObject):
    __gtype_name__ = 'Printer'
    __gsignals__ = {
        'finished': (GObject.SignalFlags.ACTION, None, ()),
    }
    web_view: WebKit.WebView
    document: Document

    def __init__(self, document: Document):
        GObject.GObject.__init__(self)
        self.document = document
        self.html = Exporter.render_html(document.content, document.title)
        self.web_view = WebKit.WebView()

    def on_load_changed(self, webview: WebKit.WebView, event: WebKit.LoadEvent):
        # When html is fully loaded then setup PrintOperation and print to PDF.
        if event == WebKit.LoadEvent.FINISHED:
            operation: WebKit.PrintOperation = WebKit.PrintOperation.new(self.web_view)
            operation.connect('finished', lambda op: self.emit('finished'))
            settings: Gtk.PrintSettings = Gtk.PrintSettings.new()
            settings.set(Gtk.PRINT_SETTINGS_OUTPUT_BASENAME, self.document.title)
            operation.set_print_settings(settings)
            if operation.run_dialog() == WebKit.PrintOperationResponse.CANCEL:
                self.emit('finished')

    def print(self):
        self.web_view.connect('load-changed', self.on_load_changed)
        print('webview created')
        self.web_view.load_html(self.html)
        print('webview loading text')

# class PlaintextRenderer(mistune.HTMLRenderer):
#
#     @staticmethod
#     def get_block(text):
#         block_type = text[0]
#         p = text.find(':')
#         if p <= 0:
#             return '', '', ''
#         length = int(text[1:p])
#         t = text[p + 1:p + 1 + length]
#         return text[p + 1 + length:], block_type, t
#
#     def block_code(self, code: str, info=None):
#         return f"```\n{code}\n```\n"
#
#     def emphasis(self, text: str):
#         return text
#
#     def strong(self, text: str):
#         return text
#
#     def text(self, text: str):
#         return text
#
#     def newline(self):
#         return "\n"
#
#     def linebreak(self):
#         return "\n"
#
#     def link(self, link, text: str = None, title=None):
#         return f"{link}"
#
#     def heading(self, text: str, level):
#         return f"{text}\n"
#
#     def paragraph(self, text: str):
#         return f"\n{text}\n"
#
#     def list_item(self, text: str, level):
#         return f"{' ' * (level - 1)} - {text}"
#
#     def list(self, text: str, ordered, level, start=None):
#         return f"{text}\n"
#
#     def strikethrough(self, text: str):
#         return text
#
#     def block_quote(self, text: str):
#         r = ""
#         for line in text.splitlines():
#             r += f"> {line}"
#         return r
#
#     def codespan(self, text):
#         return f"`{text}`"
#
#     def image(self, src, alt="", title=None):
#         return src
#
#     def inline_html(self, html):
#         return html
#
#     def table(self, header, body):
#         hrows = []
#         while header:
#             header, _type, t = PlaintextRenderer.get_block(header)
#             if _type == 'r':
#                 flags = {}
#                 cols = []
#                 while t:
#                     t, type2, t2 = PlaintextRenderer.get_block(t)
#                     if type2 == 'f':
#                         fl, v = t2.split('=')
#                         flags[fl] = v
#                     elif type2 == 'c':
#                         cols.append(_type('', (object,), {'flags': flags, 'text': t2})())
#                 hrows.append(cols)
#         brows = []
#         while body:
#             body, _type, t = PlaintextRenderer.get_block(body)
#             if _type == 'r':
#                 flags = {}
#                 cols = []
#                 while t:
#                     t, type2, t2 = PlaintextRenderer.get_block(t)
#                     if type2 == 'f':
#                         fl, v = t2.split('=')
#                         flags[fl] = v
#                     elif type2 == 'c':
#                         cols.append(_type('', (object,), {'flags': flags, 'text': t2})())
#                 brows.append(cols)
#         colscount = 0
#         colmax = [0] * 100
#         align = [''] * 100
#         for row in hrows + brows:
#             colscount = max(len(row), colscount)
#             i = 0
#             for col in row:
#                 colmax[i] = max(len(col.text), colmax[i])
#                 if 'align' in col.flags:
#                     align[i] = col.flags['align'][0]
#                 i += 1
#         r = ''
#         for row in hrows:
#             i = 0
#             for col in row:
#                 if i > 0:
#                     r += ' | '
#                 r += col.text.ljust(colmax[i])
#                 i += 1
#             r += '\n'
#         for i in range(colscount):
#             if i > 0:
#                 r += ' | '
#             if align[i] == 'c':
#                 r += ':' + '-'.ljust(colmax[i] - 2, '-') + ':'
#             elif align[i] == 'l':
#                 r += ':' + '-'.ljust(colmax[i] - 1, '-')
#             elif align[i] == 'r':
#                 r += '-'.ljust(colmax[i] - 1, '-') + ':'
#             else:
#                 r += '-'.ljust(colmax[i], '-')
#         r += '\n'
#         for row in brows:
#             i = 0
#             for col in row:
#                 if i > 0:
#                     r += ' | '
#                 r += col.text.ljust(colmax[i])
#                 i += 1
#             r += '\n'
#         return r
#
#     def table_row(self, content):
#         return 'r' + str(len(content)) + ':' + content
#
#     def table_cell(self, content, **flags):
#         content = content.replace('\n', ' ')
#         r = ''
#         for fl in flags:
#             v = flags[fl]
#             if isinstance(v, bool):
#                 v = v and 1 or 0
#             v = str(v) and str(v) or ''
#             r += 'f' + str(len(fl) + 1 + len(v)) + ':' + fl + '=' + v
#         return r + 'c' + str(len(content)) + ':' + content
#
#     def footnote_ref(self, key, index):
#         return '[^' + str(index) + ']'
#
#     def footnote_item(self, key, text):
#         r = '[^' + str(key) + ']:\n'
#         for line in text.splitlines():
#             r += '  ' + line.strip() + '\n'
#         return r
#
#     def footnotes(self, text):
#         return text
