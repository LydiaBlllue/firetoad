# Installing the app on a Mac

The download is signed with a Developer ID and notarised by Apple, so it opens with a
double-click. (中文：[安装说明](zh/install.md))

## 1. Download and open

Open the [releases page](https://github.com/lydiablllue/firetoad/releases), download
`FIRE-Toad-<version>.dmg` and double-click it. In the window that opens, **double-click FIRE
Toad**. There is nothing to drag. The disk image also holds a short note with these same steps.

macOS asks once: *"FIRE Toad" is an app downloaded from the Internet. Are you sure you want to
open it?* Click **Open**. FIRE Toad then copies itself into **Applications** (into the
Applications folder in your home folder, on an account that is not an administrator), opens
from there and ejects the disk image. It takes a few seconds; your browser opens by itself.
No network is needed: Apple's approval is stapled to the app itself.

## 2. Next time

Open FIRE Toad from Applications or Launchpad. A newer version installs the same way and
replaces the old one.

If the dialog says the app is *damaged*, the download was interrupted: delete it and download
the disk image again. If macOS says it *could not verify* the app, you have a download from
before 1.0.4, which was not signed: download the current one.

## 3. What happens next

The first time, the app asks about your folder. Click **Create my folder**: it is made for
you in Documents, as *FIRE Toad* (*FIRE Toad 2* if that name is taken by something else), and
a notification says where. If you already have one, click **Open my folder** instead. Your
browser opens on the setup: six screens,
starting with where to drop last month's statements — **[how long the first time takes](../README.md#get-started)**.
Every later launch opens the same folder straight away.

## What the signature means

Apple checked the download for known malware and recorded who made it; it did not review what
the app does. You can read that yourself: the whole of it is in this repository, and
`build/build.py` is how the download is made.
