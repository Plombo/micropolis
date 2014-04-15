import gtk
import pangocairo

gtk_major_version = gtk.gtk_version[0]

# convenience function for GTK 2/3 compatibility
def show_layout(ctx, layout):
    if gtk_major_version == 3:
        pangocairo.show_layout(ctx, layout)
    else:
        ctx.show_layout(layout)

def event_get_pointer(event):
    pointer = event.window.get_pointer()
    return pointer[1:] if gtk_major_version == 3 else pointer

def layout_set_text(layout, text):
    if gtk_major_version == 3:
        return layout.set_text(text, -1)
    else:
        return layout.set_text(text)

if gtk_major_version == 3:
    expose_event = 'draw'
else:
    expose_event = 'expose_event'

