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

    sudo ansible-playbook playbook.yml \
      -e image_path=/tmp/kiosk.img \
      -e kiosk_url=http://myportal.example.com/

And then write the image to your SD card:

    sudo dd if=/tmp/kiosk.img of=/dev/mmcblk0 bs=4M

And then stick in in your Pi and boot.

