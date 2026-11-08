# Installing the app on a Mac

The download is not signed with an Apple developer identity yet, so the first launch takes one
extra step. Every launch after that is a double-click. (中文：[安装说明](zh/install.md))

## 1. Download and copy

Open the [releases page](https://github.com/lydiablllue/jade-toad/releases), download
`JadeToad-<version>.dmg`, double-click it and drag **Jade Toad** onto the **Applications**
folder beside it. The disk image also holds a short note with these same steps.

## 2. The first launch

**macOS 15 (Sequoia) and newer**

1. Double-click Jade Toad in Applications. macOS says *"Jade Toad" Not Opened — Apple could not
   verify "Jade Toad" is free of malware*. Click **Done** (not *Move to Trash*).
2. Open **System Settings → Privacy & Security** and scroll to the bottom. A line says *"Jade
   Toad" was blocked to protect your Mac*. Click **Open Anyway** and confirm with your password
   or Touch ID.
3. One more dialog asks again. Click **Open**.

**macOS 14 (Sonoma) and earlier**

1. In Applications, right-click (or Control-click) Jade Toad and choose **Open**.
2. The dialog now has an **Open** button. Click it.

If the dialog says the app is *damaged* instead, the download was interrupted: delete it and
download the disk image again.

## 3. What happens next

The app asks where your folder is. Choose **Make one** and pick an empty folder (anywhere you
keep documents; iCloud Drive is fine on a Mac). Your browser opens on the setup: six screens,
starting with where to drop last month's statements — **[how long the first time takes](../README.md#get-started)**.
Every later launch opens the same folder straight away.

## Why the extra step

macOS asks it of any app that has not been through Apple's notarisation, which needs a paid
developer account. The roadmap's next version is the signed download; nothing else about the
app changes with it. Until then the app is signed on the build machine only, and you can read
exactly what it does: the whole of it is in this repository, and `build/build.py` is how the
download is made.
