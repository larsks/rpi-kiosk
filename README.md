This repository contains an Ansible playbook that will provision a
Raspberry Pi disk image with [ArchLinux][alarm], and configure it to 
boot directly into a web browser pointed at the site of your choice.

These playbooks require the [nspawn connection driver][nspawn] for
Ansible.

[nspawn]: https://github.com/ansible/ansible/pull/14334
[alarm]: http://archlinuxarm.org/

## Configuration

You will need to set the following variables, for which there are no
defaults:

- `wifi_ssid` -- the name of an open wireless network to which the kiosk
  will connect.  There are other `wifi_*` configuration variables; see
  `roles/kiosk/templates/wpa_supplicant.conf` for details.

- `ssh_public_key` -- a verbatim public ssh key, or a URL pointing to
  a public ssh key.  See the [authorized_key module][] documentation.

[authorized_key module]: http://docs.ansible.com/ansible/authorized_key_module.html

## Example

The playbooks must be run as `root` due to their use of
`systemd-nspawn`:

    sudo ansible-playbook playbook.yml \
      -e image_path=/tmp/kiosk.img \
      -e kiosk_url=http://myportal.example.com/ \
      -e ssh_public_key=http://github.com/myname.keys \
      -e wifi_ssid=myhouse

And then write the image to your SD card:

    sudo dd if=/tmp/kiosk.img of=/dev/mmcblk0 bs=4M

And then stick in in your Pi and boot.

