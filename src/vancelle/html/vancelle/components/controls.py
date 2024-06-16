def _ion_icon(icon, text=None, enable_text=True):
    """
    <span class="icon"><ion-icon name="{{ icon }}"></ion-icon></span>
    if text and enable_text<span>{{ text }}</span>endif
    """


def _control_post(url, icon, text, title, enable_text=False, classes=None, tabindex=0):
    """
    <form action="{{ url }}" method="post" class="control" title="{{ title }}">
      <button type="submit" hx-post="{{ url }}" class="{{ html_classes('button', 'is-small', classes) }}" tabindex="{{ tabindex }}">
        {{- _ion_icon(icon=icon, text=text, enable_text=enable_text) -}}
      </button>
    </form>
    """


def _control_link(url, icon, text, title, enable_text=False, classes=None):
    """
    <div class="control" title="{{ title }}">
      <a href="{{ url }}" class="{{ html_classes('button', 'is-small', classes) }}">
        {{- _ion_icon(icon=icon, text=text, enable_text=enable_text) -}}
      </a>
    </div>
    """


def _control_static(icon, text, title, enable_text=False, classes=None):
    """
    <div class="control" title="{{ title }}">
      <span class="{{ html_classes('button', 'is-small', 'is-static', classes) }}">
        {{- _ion_icon(icon=icon, text=text, enable_text=enable_text) -}}
      </span>
    </div>
    """


def _control_static_text(text, title, enable_text=False, classes=None):
    """
    <div class="control" title="{{ title }}">
      <span class="{{ html_classes('button', 'is-small', 'is-static', classes) }}">
        <span class="icon">
          {{- text -}}
        </span>
      </span>
    </div>
    """
