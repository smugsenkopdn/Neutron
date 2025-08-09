from bs4 import BeautifulSoup
import uuid

"""

Neutron passes HTML elements beetween JavaScript and Python using a custom ID system "NeutronID".
The NeutronID is located in an elements classlist, and is generated when display() is first called.
Using this system Neutron can share HTML elements that do not have a regular HTML id,
for example HTML elements returned by getElementsByTagName().
Every NeutronID is an UUID.

"""

def createNeutronId(tag):
    NeutronID = f"NeutronID_{uuid.uuid1()}"

    element_classes = tag.get('class')
    if element_classes is not None:
        tag['class'] = NeutronID + " " + " ".join(element_classes)
    else:
         tag['class'] = NeutronID

    return NeutronID


# Web componets #

# TODO: Add event Attributes
HTMLelementAttributes = ['value', 'accept', 'action', 'align', 'allow', 'alt', 'autocapitalize', 'autocomplete',
                         'autofocus', 'autoplay', 'background', 'bgcolor', 'border', 'buffered', 'capture', 'challenge',
                         'charset', 'checked', 'cite', 'id', 'className', 'code', 'codebase', 'color', 'cols', 'colspan',
                         'content', 'contenteditable', 'contextmenu', 'controls', 'coords', 'crossorigin', 'csp ',
                         'data', 'datetime', 'decoding', 'default', 'defer', 'dir', 'dirname', 'disabled', 'download',
                         'draggable', 'enctype', 'enterkeyhint', 'for_', 'form', 'formaction', 'formenctype',
                         'formmethod', 'formnovalidate', 'formtarget', 'headers', 'height', 'hidden', 'high', 'href',
                         'hreflang', 'http_equiv', 'icon', 'importance', 'integrity', 'intrinsicsize ', 'inputmode',
                         'ismap', 'itemprop', 'keytype', 'kind', 'label', 'lang', 'language ', 'loading ', 'list',
                         'loop', 'low', 'manifest', 'max', 'maxlength', 'minlength', 'media', 'method', 'min',
                         'multiple', 'muted', 'name', 'novalidate', 'open', 'optimum', 'pattern', 'ping', 'placeholder',
                         'poster', 'preload', 'radiogroup', 'readonly', 'referrerpolicy', 'rel', 'required', 'reversed',
                         'rows', 'rowspan', 'sandbox', 'scope', 'scoped', 'selected', 'shape', 'size', 'sizes', 'slot',
                         'span', 'spellcheck', 'src', 'srcdoc', 'srclang', 'srcset', 'start', 'step', 'style',
                         'summary', 'tabindex', 'target', 'title', 'translate', 'type', 'usemap', 'width', 'wrap',
                         'onblur', 'onchange', 'oncontextmenu', 'onfocus', 'oninput', 'oninvalid', 'onreset', 'onsearch',
                         'onselect', 'onsubmit', 'onkeydown', 'onkeypress', 'onkeyup', 'onclick', 'ondblclick', 'onmousedown',
                         'onmousemove', 'onmouseout', 'onmouseover', 'onmouseup', 'onwheel', 'ondrag', 'ondragend',
                         'ondragenter', 'ondragleave', 'ondragover', 'ondragstart', 'ondrop', 'onscroll', 'oncopy', 'oncut',
                         'onpaste', 'onabort', 'oncanplay', 'oncanplaythrough', 'oncuechange', 'ondurationchange', 'onemptied', 'onended',
                         'onerror', 'onloadeddata', 'onloadedmetadata', 'onloadstart', 'onpause', 'onplay', 'onplaying', 'onprogress',
                         'onratechange', 'onseeked', 'onseeking', 'onstalled', 'onsuspend', 'ontimeupdate', 'onvolumechange',
                         'onwaiting', 'ontoggle',]

class ClassList():
    def __init__(self, elem, list:list):
        self.elem = elem
        self.list = list
    def __str__(self):
        return str(self.list)
    def add(self, value):
        if not (value in self.list):
            self.list.append(value)
            self.save_list()
    def remove(self, value):
        if value in self.list:
            self.list.remove(value)
            self.save_list()
    def replace(self, old, new):
        if old in self.list:
            self.list.remove(old)
            self.list.append(new)
            self.save_list()
            return True
        else: return False
    def toggle(self, value, force:bool=False):
        if value in self.list:
            self.list.remove(value)
            self.save_list()
            return False
        elif force: return False
        else:
            self.list.append(value)
            self.save_list()
            return True
    def save_list(self):
        self.elem.classList = self.list

class HTMLelement:
    def __init__(self, window, NeutronID, element_soup, domAttatched):
        self.window = window
        self.element_soup = element_soup # element_soup is None if element is aquired while window is running
        self.NeutronID = NeutronID
        self.domAttatched = domAttatched;

        if "NeutronID_" not in self.NeutronID:
            raise ValueError("NeutronID is invalid")

    def __str__(self):
        # element_soup will be set to None if class is called on runtime
        if self.window.running and self.domAttatched:
            return str(self.window.run_javascript(f""" '' + document.getElementsByClassName("{self.NeutronID}")[0].outerHTML;"""))
        else:
            return str(self.element_soup)


    def addEventListener(self, eventHandler, NeutronEvent):
        if self.window.running and self.domAttatched:
            self.window.run_javascript(
                f""" '' + document.getElementsByClassName("{self.NeutronID}")[0].addEventListener("{eventHandler}", {NeutronEvent});""");
        else:
            eventHandler = "on" + eventHandler
            soup = BeautifulSoup(self.window.html, features="html.parser")
            # Create a new attribute for the event (i.e onclick)
            soup.find_all(class_=self.NeutronID)[0][eventHandler] = NeutronEvent

            self.window.html = str(soup)

    def appendChild(self, html_element):
        if self.window.running and self.domAttatched:
            soup = BeautifulSoup(str(html_element), features="html.parser")
            bodyContent = soup.find_all()

            for element in bodyContent:
                createNeutronId(element)

            self.window.run_javascript(f"""document.getElementsByClassName("{self.NeutronID}")[0].innerHTML += '{str(soup)}';""")
            return html_element
        else:
            self.element_soup.append(BeautifulSoup(str(html_element), 'html.parser'))

    def append(self, html):
        if self.window.running and self.domAttatched:
            soup = BeautifulSoup(html, features="html.parser")
            bodyContent = soup.find_all()

            for element in bodyContent:
                createNeutronId(element)

            self.window.run_javascript(f"""document.getElementsByClassName("{self.NeutronID}")[0].innerHTML += '{str(soup)}';""")
        else:
            self.element_soup.append(BeautifulSoup(html, 'html.parser'))

    # TODO
    def remove(self):
        if not self.window.running or not self.domAttatched:
             raise RuntimeError(""""remove" can only be called while the window is running and element is present on DOM!""")

        self.window.run_javascript(f"""document.getElementsByClassName("{self.NeutronID}")[0].remove();""")

     # Does not work with global event handlers!
    def getAttribute(self, attribute):
        if self.window.running and self.domAttatched:
            return str(self.window.run_javascript(f""" '' + document.getElementsByClassName("{self.NeutronID}")[0].{attribute};"""))
        else:
            return self.element_soup.attrs

    # Does not work with global event handlers!
    def setAttribute(self, attribute, value):
        if self.window.running and self.domAttatched:
            self.window.run_javascript(
                f""" '' + document.getElementsByClassName("{self.NeutronID}")[0].setAttribute("{attribute}", "{value}");""")
        else:
            self.element_soup[attribute] = value

    def removeAttribute(self, attribute):
        if self.window.running and self.domAttatched:
            self.window.run_javascript(
                f""" '' + document.getElementsByClassName("{self.NeutronID}")[0].removeAttribute("{attribute}");"""
            )
        else:
            del self.element_soup[attribute]

    @property
    def classList(self):
        """
        Returns a `list` but with JavaScript methods `add`, `remove`, `replace`, and `toggle`.\n
        If you want to modify the `classList` in a different way, modify the internal `classList.list`,\n
        but then you must call `classList.save_list()` to finalize your mutation.
        """
        if self.window.running and self.domAttatched:
            classList = str(self.window.run_javascript(f"""document.getElementsByClassName("{self.NeutronID}")[0].classList;""")).split(' ')
            classList.remove(self.NeutronID) # hide the NeutronID
            return ClassList(self, classList)
        else:
            classList = self.element_soup['class']
            classList.remove(self.NeutronID) # hide the NeutronID
            return ClassList(self, classList)
    @classList.setter
    def classList(self, value:list|ClassList):
        if self.window.running and self.domAttatched:
            classList = str(self.NeutronID) # sneak in the NeutronID
            for c in value:
                classList = f"{classList} {str(c)}"
            self.window.run_javascript(f"""document.getElementsByClassName("{self.NeutronID}")[0].setAttribute("class", "{classList}");""")
        else:
            classList = [str(self.NeutronID)] # sneak in the NeutronID
            classList.extend(value)
            self.element_soup['class'] = classList

    def innerHTML_get(self):
        if self.window.running and self.domAttatched:
            return str(self.window.run_javascript(f""" '' + document.getElementsByClassName("{self.NeutronID}")[0].innerHTML;"""))
        else:
            return self.element_soup.decode_contents()

    def innerHTML_set(self, value):
        if self.window.running and self.domAttatched:
            self.window.run_javascript(f"""document.getElementsByClassName("{self.NeutronID}")[0].innerHTML = "{value}";""")
        else:
            self.element_soup.clear()
            self.element_soup.append(BeautifulSoup(value, 'html.parser'))

    innerHTML = property(innerHTML_get, innerHTML_set)

    for attribute in HTMLelementAttributes:
        exec(
            f"{attribute} = property(lambda self: self.getAttribute('{attribute}'), lambda self, val: self.setAttribute('{attribute}', val))")
