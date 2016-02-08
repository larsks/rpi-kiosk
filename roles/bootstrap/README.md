Ansible requires a Python 2.x interpreter.  This play uses the [raw][]
module to ensure that one is installed, and sets the
`ansible_python_interpreter` variable to point at the installed
binary.

[raw]: http://docs.ansible.com/ansible/raw_module.html
