# =================================================================
# =                  Author: Brad Heffernan                       =
# =================================================================

import os
import shutil
import psutil
# import time
import subprocess
import threading  # noqa
import gi
# import configparser
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gtk  # noqa

sudo_username = os.getlogin()
home = "/home/" + str(sudo_username)

pacman = "/etc/pacman.conf"
oblogout_conf = "/etc/oblogout.conf"
# oblogout_conf = home + "/oblogout.conf"
gtk3_settings = home + "/.config/gtk-3.0/settings.ini"
gtk2_settings = home + "/.gtkrc-2.0"
grub_theme_conf = "/boot/grub/themes/Vimix/theme.txt"
xfce_config = home + "/.config/xfce4/xfconf/xfce-perchannel-xml/xsettings.xml"
slimlock_conf = "/etc/slim.conf"
termite_config = home + "/.config/termite/config"
neofetch_config = home + "/.config/neofetch/config.conf"
lightdm_conf = "/etc/lightdm/lightdm.conf"
bd = ".att_backups"
config = home + "/.config/arcolinux-tweak-tool/settings.ini"
desktop = ""


i3wm_config = home + "/.config/i3/config"
awesome_config = home + "/.config/awesome/rc.lua"

arepo_test = "[arcolinux_repo_testing]\n\
SigLevel = Required DatabaseOptional\n\
Include = /etc/pacman.d/arcolinux-mirrorlist"

arepo = "[arcolinux_repo]\n\
SigLevel = Required DatabaseOptional\n\
Include = /etc/pacman.d/arcolinux-mirrorlist"

a3drepo = "[arcolinux_repo_3party]\n\
SigLevel = Required DatabaseOptional\n\
Include = /etc/pacman.d/arcolinux-mirrorlist"

axlrepo = "[arcolinux_repo_xlarge]\n\
SigLevel = Required DatabaseOptional\n\
Include = /etc/pacman.d/arcolinux-mirrorlist"

hefftor_repo = "[hefftor-repo]\n\
SigLevel = Optional TrustedOnly\n\
Include = /etc/pacman.d/arcolinux-mirrorlist-bradheff"

bobo_repo = "[bobo-repo]\n\
SigLevel = Optional TrustedOnly\n\
Include = /etc/pacman.d/arcolinux-mirrorlist-bobo"
# =====================================================
#               NOTIFICATIONS
# =====================================================


def show_in_app_notification(self, message):
    if self.timeout_id is not None:
        GLib.source_remove(self.timeout_id)
        self.timeout_id = None

    self.notification_label.set_markup("<span foreground=\"white\">" +
                                       message + "</span>")
    self.notification_revealer.set_reveal_child(True)
    self.timeout_id = GLib.timeout_add(3000, timeOut, self)


def timeOut(self):
    close_in_app_notification(self)


def close_in_app_notification(self):
    self.notification_revealer.set_reveal_child(False)
    GLib.source_remove(self.timeout_id)
    self.timeout_id = None

# =====================================================
#               PERMISSIONS
# =====================================================


def permissions(dst):
    try:
        original_umask = os.umask(0)
        calls = subprocess.run(["sh", "-c", "cat /etc/passwd | grep " +
                                sudo_username],
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
        id = calls.stdout.decode().split(":")[3].strip()
        os.chown(dst, int(id), int(id))
    finally:
        os.umask(original_umask)

# =====================================================
#               COPY FUNCTION
# =====================================================


def copy_func(src, dst, isdir=False):
    if isdir:
        subprocess.run(["cp", "-Rp", src, dst], shell=False)
    else:
        subprocess.run(["cp", "-p", src, dst], shell=False)
    permissions(dst)

# =====================================================
#               SOURCE
# =====================================================


def source_shell(self):
    process = subprocess.run(["sh", "-c", "echo \"$SHELL\""],
                             stdout=subprocess.PIPE)

    output = process.stdout.decode().strip()
    print(output)
    if output == "/bin/bash":
        subprocess.run(["bash", "-c", "su - " + sudo_username +
                        " -c \"source " + home + "/.bashrc\""],
                       stdout=subprocess.PIPE)
    elif output == "/bin/zsh":
        subprocess.run(["zsh", "-c", "su - " + sudo_username +
                        " -c \"source " + home + "/.zshrc\""],
                       stdout=subprocess.PIPE)

# =====================================================
#               MESSAGEBOX
# =====================================================


def MessageBox(self, title, message):
    md2 = Gtk.MessageDialog(parent=self,
                            flags=0,
                            message_type=Gtk.MessageType.INFO,
                            buttons=Gtk.ButtonsType.OK,
                            text=title)
    md2.format_secondary_markup(message)
    md2.run()
    md2.destroy()

# =====================================================
#               CONVERT COLOR
# =====================================================


def rgb_to_hex(rgb):
    if "rgb" in rgb:
        rgb = rgb.replace("rgb(", "").replace(")", "")
        vals = rgb.split(",")
        return "#{0:02x}{1:02x}{2:02x}".format(clamp(int(vals[0])),
                                               clamp(int(vals[1])),
                                               clamp(int(vals[2])))
    return rgb


def clamp(x):
    return max(0, min(x, 255))


# =====================================================
#               GLOBAL FUNCTIONS
# =====================================================


def _get_position(lists, value):
    data = [string for string in lists if value in string]
    position = lists.index(data[0])
    return position


def _get_variable(lists, value):
    data = [string for string in lists if value in string]

    if len(data) >= 1:

        data1 = [string for string in data if "#" in string]

        for i in data1:
            if i[:4].find('#') != -1:
                data.remove(i)
    if data:
        data_clean = [data[0].strip('\n').replace(" ", "")][0].split("=")
    return data_clean

# Check  value exists


def check_value(list, value):
    data = [string for string in list if value in string]
    if len(data) >= 1:
        data1 = [string for string in data if "#" in string]
        for i in data1:
            if i[:4].find('#') != -1:
                data.remove(i)
    return data


def check_backups(now):
    if not os.path.exists(home + "/" + bd + "/Backup-" +
                          now.strftime("%Y-%m-%d %H")):
        os.makedirs(home + "/" + bd + "/Backup-" +
                    now.strftime("%Y-%m-%d %H"), 0o777)
        permissions(home + "/" + bd + "/Backup-" + now.strftime("%Y-%m-%d %H"))

# =====================================================
#               Check if File Exists
# =====================================================


def file_check(file):
    if os.path.isfile(file):
        return True

    return False

# =====================================================
#               GTK3 CONF
# =====================================================


def gtk_check_value(my_list, value):
    data = [string for string in my_list if value in string]
    if len(data) >= 1:
        data1 = [string for string in data if "#" in string]
        for i in data1:
            if i[:4].find('#') != -1:
                data.remove(i)
    return data


def gtk_get_position(my_list, value):
    data = [string for string in my_list if value in string]
    position = my_list.index(data[0])
    return position


# =====================================================
#               OBLOGOUT CONF
# =====================================================
# Get shortcuts index


def get_shortcuts(conflist):
    sortcuts = _get_variable(conflist, "shortcuts")
    shortcuts_index = _get_position(conflist, sortcuts[0])
    return int(shortcuts_index)

# Get commands index


def get_commands(conflist):
    commands = _get_variable(conflist, "commands")
    commands_index = _get_position(conflist, commands[0])
    return int(commands_index)

# =====================================================
#               LIGHTDM CONF
# =====================================================


def check_lightdm_value(list, value):
    data = [string for string in list if value in string]
    # if len(data) >= 1:
    #     data1 = [string for string in data if "#" in string]

    return data

# =====================================================
#               HBLOCK CONF
# =====================================================


def hblock_get_state(self):
    lines = int(subprocess.check_output('wc -l /etc/hosts',
                                        shell=True).strip().split()[0])
    if os.path.exists("/usr/local/bin/hblock") and lines > 100:
        return True

    self.firstrun = False
    return False


def do_pulse(data, self):
    self.progress.pulse()
    return True


def set_hblock(self, toggle, state):
    GLib.idle_add(toggle.set_sensitive, False)
    GLib.idle_add(self.label7.set_text, "Run..")
    GLib.idle_add(self.progress.set_fraction, 0.2)

    timeout_id = None
    timeout_id = GLib.timeout_add(100, do_pulse, None, self)

    try:

        install = 'pacman -S arcolinux-hblock-git --needed --noconfirm'
        enable = "/usr/local/bin/hblock"

        if state:
            if os.path.exists("/usr/local/bin/hblock"):
                GLib.idle_add(self.label7.set_text, "Database update...")
                subprocess.call([enable],
                                shell=False,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
            else:
                GLib.idle_add(self.label7.set_text, "Install Hblock......")
                subprocess.call(install.split(" "),
                                shell=False,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
                GLib.idle_add(self.label7.set_text, "Database update...")
                subprocess.call([enable],
                                shell=False,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)

        else:
            GLib.idle_add(self.label7.set_text, "Remove update...")
            subprocess.run(["sh", "-c",
                            "HBLOCK_SOURCES=\'\' /usr/local/bin/hblock"],
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)

        GLib.idle_add(self.label7.set_text, "Complete")
        GLib.source_remove(timeout_id)
        timeout_id = None
        GLib.idle_add(self.progress.set_fraction, 0)

        GLib.idle_add(toggle.set_sensitive, True)
        if state:
            GLib.idle_add(self.label7.set_text, "HBlock Active")
        else:
            GLib.idle_add(self.label7.set_text, "HBlock Inactive")

    except Exception as e:
        MessageBox(self, "ERROR!!", str(e))
        print(e)


# =====================================================
#               GRUB CONF
# =====================================================


def get_grub_wallpapers():
    if os.path.isdir("/boot/grub/themes/Vimix"):
        lists = os.listdir("/boot/grub/themes/Vimix")

        rems = ['select_e.png', 'terminal_box_se.png', 'select_c.png',
                'terminal_box_c.png', 'terminal_box_s.png',
                'select_w.png', 'terminal_box_nw.png',
                'terminal_box_w.png', 'terminal_box_ne.png',
                'terminal_box_sw.png', 'terminal_box_n.png',
                'terminal_box_e.png']

        ext = ['.png', '.jpeg', '.jpg']

        new_list = [x for x in lists if x not in rems for y in ext if y in x]

        new_list.sort()
        return new_list


def set_grub_wallpaper(self, image):
    if os.path.isfile(grub_theme_conf):
        if not os.path.isfile(grub_theme_conf + ".bak"):
            shutil.copy(grub_theme_conf, grub_theme_conf + ".bak")
        try:
            with open(grub_theme_conf, "r") as f:
                lists = f.readlines()
                f.close()

            val = _get_position(lists, "desktop-image: ")
            lists[val] = "desktop-image: \"" + os.path.basename(image) + "\"" + "\n"

            with open(grub_theme_conf, "w") as f:
                f.writelines(lists)
                f.close()

            show_in_app_notification(self, "Settings Saved Successfully")
            # MessageBox(self, "Success!!", "Settings Saved Successfully")
        except:  # noqa
            pass


# =====================================================
#               NEOFETCH CONF
# =====================================================


def neofetch_set_value(lists, pos, text, state):
    if state:
        if text in lists[pos]:
            if "#" in lists[pos]:
                lists[pos] = lists[pos].replace("#", "")
    else:
        if text in lists[pos]:
            if "#" not in lists[pos]:
                lists[pos] = "#" + lists[pos]

    return lists


def neofetch_set_backend_value(lists, pos, text, value):
    if text in lists[pos] and "#" not in lists[pos]:
        lists[pos] = text + value + "\"\n"

# ====================================================================
#                       CUSTOM FUNCTION
# ====================================================================


def get_desktop(self):
    base_dir = os.path.dirname(os.path.realpath(__file__))

    desktop = subprocess.run(["sh", base_dir + "/find_DE.sh", sudo_username],
                             shell=False,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
    dsk = desktop.stdout.decode().strip().split("\n")

    # return dsk[len(dsk)-1].lstrip().rstrip()
    self.desktop = dsk[-1].lstrip().rstrip()
    # print("Desktop: " + self.desktop)


def copytree(self, src, dst, symlinks=False, ignore=None):  # noqa

    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.exists(d):
            try:
                shutil.rmtree(d)
            except Exception as e:
                print(e)
                os.unlink(d)
        if os.path.isdir(s):
            try:
                shutil.copytree(s, d, symlinks, ignore)
            except Exception as e:
                print(e)
                print("ERROR2")
                self.ecode = 1
        else:
            try:
                shutil.copy2(s, d)
            except:  # noqa
                print("ERROR3")
                self.ecode = 1

# =====================================================
#               CHECK RUNNING PROCESS
# =====================================================


def checkIfProcessRunning(processName):
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name', 'create_time'])
            if processName == pinfo['pid']:
                return True
        except (psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess):
            pass
    return False
