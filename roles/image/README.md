This directory contains all the roles for creating and provisioning
the [Arch Linux][arch] image.

- `fetch` - download the Arch Linux tarball
- `create` - create image file, partitions, filesystems
- `resize` - grow root partition and filesystem to end of image
- `mount` - mount image
- `install` - install contents of Arch Linux tarball
- `cleanup` - make sure filesystems are unmounted and loop device is
  unconfigured

[arch]: https://www.archlinux.org/
