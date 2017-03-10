import sublime
import sublime_plugin
import socket
import time
import threading
# Variables
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.SOL_TCP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('127.0.0.1', 7777))
sock_thread = threading.Thread()
sock_thread.daemon = True
UseDelay = False
Settings = sublime.load_settings("MahouCaretDisplayServer.sublime-settings")
print("MCDS init done.\nServer runs at 127.0.0.1:7777.")
# Event listener
class SublimeTextEventsListener(sublime_plugin.EventListener):
    def on_window_command(self, window, name, args):
        global UseDelay
        if Settings.get('debug_mode'):
            print("on_window_command = " + name)
        if (name == 'toggle_side_bar'):
            UseDelay = True
        StartSockThread((self, None, window, name, args))
    def on_text_command(self, window, name, args):
        global UseDelay
        if Settings.get('debug_mode'):
            print("on_text_command = " + name)
        if (name == 'move_to'):
            UseDelay = True
        StartSockThread((self, None, window, name, args))
    def on_activated(self, view):
        if Settings.get('debug_mode'):
            print("view.id = " + str(view.id()))
        StartSockThread((self, view))
# Menu commands
class toggle_mcd_serverCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        Settings.set('server_enabled', not Settings.get('server_enabled'))
        sublime.save_settings('MahouCaretDisplayServer.sublime-settings')
        print("ServerEnabled set to: " + str(Settings.get('server_enabled')))

class toggle_debug_modeCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        Settings.set('debug_mode', not Settings.get('debug_mode'))
        sublime.save_settings('MahouCaretDisplayServer.sublime-settings')
        print("Debug mode set to: " + str(Settings.get('debug_mode')))
# Main functions
def StartSockThread(ags=(None,)):
    global sock_thread
    sock_thread = threading.Thread(target=UpdateServer, args=ags)
    sock_thread.start()

def UpdateServer(self, view = None, window = None, name = None, args = None):
    global Settings
    Settings = sublime.load_settings("MahouCaretDisplayServer.sublime-settings")
    if Settings.get('server_enabled'):
        if view is None and window is not None:
            if type(window) is sublime.View:
                view = window
            else:
                view = window.active_view()
        if UseDelay:
            time.sleep(Settings.get("special_delay"))
        topRow = view.rowcol(view.visible_region().a)[0]
        caret_pos = view.rowcol(view.sel()[0].begin())
        sdbWidth = abs(view.window_to_layout(view.viewport_position())[0]) - 48  
        if (view.id() == 4):
            sdbWidth += 27
        if Settings.get('debug_mode'):
            print("\tUpdating server with values:\nLine->" + str(caret_pos[0] - topRow) + '|' + 
                  "Caret on Character->" + str(caret_pos[1]) + '|' +
                  "Line Height(Font)->" + str(view.line_height()) + '|' + 
                  "Character Width->" + str(view.em_width()) + '|' +
                  "View ID->" + str(view.id()) + '|' +
                  "Sidebar Width->" + str(sdbWidth) )
        sock.listen(1)
        conn, addr = sock.accept()
        if Settings.get('debug_mode'):
            print('\t\tConnected to:', addr, 'sending data...')
        data = bytes("L->" + str(caret_pos[0] - topRow) + '|' + 
                     "C->" + str(caret_pos[1]) + '|' +
                     "LH->" + str(view.line_height()) + '|' + 
                     "CW->" + str(view.em_width()) + '|' +
                     "VID->" + str(view.id()) + '|' +
                     "SBW->" + str(sdbWidth), 'utf-8')
        conn.send(data)
        if Settings.get('debug_mode'):
            print('\t\tSend ok.')
