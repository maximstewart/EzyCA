# Python imports
import threading, subprocess, os

# Gtk imports

# Application imports


class Utils:
    """Empty docstring for Utils"""

    def fill_data_block(self, target, data):
        for entry in data:
            text = ''

            if hasattr(entry, "get_children"):
                entry = entry.get_children()[0]

            if hasattr(entry, "get_text"):
                text = entry.get_text().strip()

            if text != '' and text != 'Below, add domain names each on a new line...':
                target.append(text)

    def getClipboardData(self):
        proc    = subprocess.Popen(['xclip','-selection', 'clipboard', '-o'], stdout=subprocess.PIPE)
        retcode = proc.wait()
        data    = proc.stdout.read()
        return data.decode("utf-8").strip()

    def setClipboardData(self, data):
        proc = subprocess.Popen(['xclip','-selection','clipboard'], stdin=subprocess.PIPE)
        proc.stdin.write(data)
        proc.stdin.close()
        retcode = proc.wait()
