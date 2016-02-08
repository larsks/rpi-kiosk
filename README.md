This repository contains an Ansible playbook that will provision a
Raspberry Pi disk image with [ArchLinux][alarm], and configure it to 
boot directly into a web browser pointed at the site of your choice.

These playbooks require the [nspawn connection driver][nspawn] for
Ansible.

[nspawn]: https://github.com/ansible/ansible/pull/14334
[alarm]: http://archlinuxarm.org/

## Example

The playbooks must be run as `root` due to their use of
`systemd-nspawn`:

    sudo ansible-playbook playbook.yml -e image_path=/tmp/kiosk.img
