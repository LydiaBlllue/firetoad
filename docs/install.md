# Installing the app on a Mac

The download is signed with a Developer ID and notarised by Apple, so it opens with a
double-click. (中文：[安装说明](zh/install.md))

## 1. Download and copy

Open the [releases page](https://github.com/lydiablllue/firetoad/releases), download
`FIRE-Toad-<version>.dmg`, double-click it and drag **FIRE Toad** onto the **Applications**
folder beside it. The disk image also holds a short note with these same steps.

## 2. The first launch

Double-click FIRE Toad in Applications. macOS asks once: *"FIRE Toad" is an app downloaded from
the Internet. Are you sure you want to open it?* Click **Open**. Every launch after that is a
plain double-click. No network is needed: Apple's approval is stapled to the app itself.

If the dialog says the app is *damaged*, the download was interrupted: delete it and download
the disk image again. If macOS says it *could not verify* the app, you have a download from
before 1.0.4, which was not signed: download the current one.

## 3. What happens next

The app asks where your folder is. Choose **Make one** and pick an empty folder (anywhere you
keep documents; iCloud Drive is fine on a Mac). Your browser opens on the setup: six screens,
starting with where to drop last month's statements — **[how long the first time takes](../README.md#get-started)**.
Every later launch opens the same folder straight away.

## What the signature means

Apple checked the download for known malware and recorded who made it; it did not review what
the app does. You can read that yourself: the whole of it is in this repository, and
`build/build.py` is how the download is made.
