#!/usr/bin/env python3

import re
import os, os.path
import socket

import pprint


hostname = socket.gethostname()
CFG_SEARCH_PATH = ['/etc/X11/xorg.conf', \
                   '/etc/xorg.conf', \
                   '/usr/etc/X11/xorg.conf.' + hostname, \
                   '/usr/etc/X11/xorg.conf', \
                   '/usr/lib/X11/xorg.conf.' + hostname, \
                   '/usr/lib/X11/xorg.conf', \
                   '/etc/X11/xorg.conf.d/', \
                   '/usr/etc/X11/xorg.conf.d/', \
                   '/usr/share/X11/xorg.conf.d/']


def accessible(fs_path): 
    ''' Check file/directory accessibility. For file check read bit presense.
        For directory read and execute bits presense.

    '''
    if os.path.isfile(fs_path):
        return os.access(fs_path, os.R_OK)
    elif os.path.isdir(fs_path):
        return os.access(fs_path, os.R_OK | os.X_OK)
    else:
        return False

def do_env_xorgconfig(xconfig_path):
    ''' Adopt XORGCONFIG environment variable to XOrg config search path. '''
    env_search_path = list()

    if xconfig_path:
        fs_path = xconfig_path.split('/')
    
        # Check for '..' and remove it
        try:
            while fs_path:
                fs_path.remove('..')
        except ValueError:
            pass

        for d in ('/etc/X11/', '/usr/etc/X11/'):
            cfg_path = os.path.join(d, *fs_path)

            if os.path.isdir(cfg_path):
                cfg_path = os.path.join(cfg_path, 'xorg.conf')

            env_search_path.append(cfg_path)

    return env_search_path

def expand_conf_dir(config_dir):
    ''' Search all *.conf files in directory config_dir. '''
    cf_list = list()

    if accessible(config_dir):
        for i in sorted(os.listdir(config_dir)):
            if re.search('.*\.conf$', i):
                cf = os.path.join(config_dir, i)
                if os.path.isfile(cf):
                    cf_list.append(os.fspath(cf))

    return cf_list

def build_cf_list():
    ''' Build list of XOrg config files present in system. '''
    cfg_list = CFG_SEARCH_PATH[:]

    if 'XORGCONFIG' in os.environ: 
        cfg_list = do_env_xorgconfig(os.environ['XORGCONFIG']) + cfg_list

    i = 0
    while i < len(cfg_list):
        if os.path.isdir(cfg_list[i]):
            cfg_list = cfg_list[:i] + expand_conf_dir(cfg_list[i]) + cfg_list[i+1:]

        # Check file accessibility and duplicates
        if not accessible(cfg_list[i]) or (cfg_list[i] in cfg_list[:i]):
            del cfg_list[i]
        else:
            i += 1

    return cfg_list


if __name__ == '__main__':
    pprint.pprint(build_cf_list())
