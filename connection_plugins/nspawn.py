from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import pipes
import subprocess
import traceback
import shlex

from ansible import constants as C
from ansible.errors import AnsibleError
from ansible.plugins.connection import ConnectionBase
from ansible.module_utils.basic import is_executable
from ansible.utils.unicode import to_bytes
from ansible.utils.vars import combine_vars
from ansible.utils.boolean import boolean

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()

BUFSIZE = 65536


class Connection(ConnectionBase):
    ''' Local nspawn based connections '''

    transport = 'nspawn'
    has_pipelining = True
    become_methods = frozenset(C.BECOME_METHODS)

    def __init__(self, play_context, new_stdin, *args, **kwargs):
        super(Connection, self).__init__(play_context, new_stdin,
                *args, **kwargs)

        self.chroot = self._play_context.remote_addr

        if not os.path.isdir(self.chroot):
            raise AnsibleError("%s is not a directory" % self.chroot)

        chrootsh = os.path.join(self.chroot, 'bin/sh')
        if not is_executable(chrootsh):
            raise AnsibleError("%s does not look like a chrootable dir (/bin/sh missing)" % self.chroot)

    def set_host_overrides(self, host):
        self._host = host

        host_vars = combine_vars(host.get_group_vars(), host.get_vars())
        self._nspawn_cmd = host_vars.get('nspawn_command', 'systemd-nspawn')
        self._nspawn_args = shlex.split(host_vars.get('nspawn_extra_args', ''))
        self._nspawn_sudo = boolean(host_vars.get('nspawn_sudo', 'false'))

    def _connect(self):
        if os.geteuid() != 0 and not self._nspawn_sudo:
            raise AnsibleError("nspawn connection requires running as root")

    def _buffered_exec_command(self, cmd, stdin=subprocess.PIPE):
        executable = (
                C.DEFAULT_EXECUTABLE.split()[0]
                if C.DEFAULT_EXECUTABLE
                else '/bin/sh')

        local_cmd = ([self._nspawn_cmd, '-q', '-D', self.chroot ]
                + self._nspawn_args + ['--', executable, '-c', cmd])

        if self._nspawn_sudo:
            local_cmd = ['sudo', '-E', '-n', '--'] + local_cmd

        display.vvv("EXEC %s" % (local_cmd), host=self.chroot)
        local_cmd = map(to_bytes, local_cmd)
        p = subprocess.Popen(local_cmd, shell=False, stdin=stdin,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return p

    def exec_command(self, cmd, in_data=None, sudoable=False):
        ''' run a command on the chroot '''
        super(Connection, self).exec_command(cmd, in_data=in_data, sudoable=sudoable)

        p = self._buffered_exec_command(cmd)
        stdout, stderr = p.communicate(in_data)
        return (p.returncode, stdout, stderr)

    def _prefix_login_path(self, remote_path):
        ''' Transform all relative paths into absolute paths that
        start at `/`. '''
        if not remote_path.startswith(os.path.sep):
            remote_path = os.path.join(os.path.sep, remote_path)
        return os.path.normpath(remote_path)

    def put_file(self, in_path, out_path):
        ''' transfer a file from local to chroot '''
        super(Connection, self).put_file(in_path, out_path)
        display.vvv("PUT %s TO %s" % (in_path, out_path), host=self.chroot)

        out_path = pipes.quote(self._prefix_login_path(out_path))
        try:
            with open(in_path, 'rb') as in_file:
                try:
                    p = self._buffered_exec_command('dd of=%s bs=%s' % (out_path, BUFSIZE), stdin=in_file)
                except OSError:
                    raise AnsibleError("chroot connection requires dd command in the chroot")
                try:
                    stdout, stderr = p.communicate()
                except:
                    traceback.print_exc()
                    raise AnsibleError("failed to transfer file %s to %s" % (in_path, out_path))
                if p.returncode != 0:
                    raise AnsibleError("failed to transfer file %s to %s:\n%s\n%s" % (in_path, out_path, stdout, stderr))
        except IOError:
            raise AnsibleError("file or module does not exist at: %s" % in_path)

    def fetch_file(self, in_path, out_path):
        ''' fetch a file from chroot to local '''
        super(Connection, self).fetch_file(in_path, out_path)
        display.vvv("FETCH %s TO %s" % (in_path, out_path), host=self.chroot)

        in_path = pipes.quote(self._prefix_login_path(in_path))
        try:
            p = self._buffered_exec_command('dd if=%s bs=%s' % (in_path, BUFSIZE))
        except OSError:
            raise AnsibleError("chroot connection requires dd command in the chroot")

        with open(out_path, 'wb+') as out_file:
            try:
                chunk = p.stdout.read(BUFSIZE)
                while chunk:
                    out_file.write(chunk)
                    chunk = p.stdout.read(BUFSIZE)
            except:
                traceback.print_exc()
                raise AnsibleError("failed to transfer file %s to %s" % (in_path, out_path))
            stdout, stderr = p.communicate()
            if p.returncode != 0:
                raise AnsibleError("failed to transfer file %s to %s:\n%s\n%s" % (in_path, out_path, stdout, stderr))

    def close(self):
        ''' terminate the connection; nothing to do here '''
        super(Connection, self).close()
        self._connected = False
