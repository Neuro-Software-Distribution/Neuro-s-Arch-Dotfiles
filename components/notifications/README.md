# NeurOS notification renderer

`preview.c` draws the popup with GTK 3, Cairo and Pango. Its `--render` and
`--preview` modes do not receive notifications or own the notification D-Bus
name. The separate `--listen` mode connects to Astal or starts an Astal daemon;
it refuses to replace a running non-Astal notification server.

Build the preview (GTK 3, gtk-layer-shell, AstalNotifd and their development
files, pkgconf, and a C compiler are required):

```sh
bash scripts/build-notification-preview /tmp/neuros-notification-preview
/tmp/neuros-notification-preview --preview
```

The preview appears for eight seconds and can be dismissed by clicking it. To
render an image without starting a graphical window:

```sh
/tmp/neuros-notification-preview --render /tmp/neuros-notification.png \
  --app 'SCREENSHOT' --title 'Screenshot saved' \
  --body 'Saved to ~/Pictures/Screenshots & copied' --image /path/to/image.png
```

The palette can be supplied with `--accent`, `--secondary`, `--foreground`,
and `--background`. Invalid image paths are ignored and the card stays usable.
The C listener follows the active palette through the generated
`cyberarch/notification.palette` file. It shows up to four
popups; left click invokes the default or sole action, middle click opens the
action menu, and right click dismisses. Multiple actions without a default open
the menu on left click. The existing read and dismiss shortcuts work too.
Notifications carrying a standard `value` hint display a progress indicator.
Critical notifications without an application-specified timeout stay visible
until dismissed and use a red frame.

## Enable and disable

For a new install, the installer selects native notifications after a successful
build. The NeurOS shell attempts activation when it starts. Existing installations
can run the installer again, or install the dependencies and enable them directly:

```sh
bash ~/.config/hypr/themes/cyberpunk/scripts/notifications enable
bash ~/.config/hypr/themes/cyberpunk/scripts/notifications disable
bash ~/.config/hypr/themes/cyberpunk/scripts/notifications status
```

Enabling directly first restarts the NeurOS shell with a preflight build. It then stops
the user-managed Dunst service if it owns notifications, waits for Astal, and
starts the C renderer. The choice is remembered across shell restarts and
future installer runs. Disabling is also remembered. Other
notification servers are not stopped. The existing NeurOS popup takes over if
the renderer exits, and disabling returns to that popup. Dunst can take over
again when the NeurOS notification service is no longer running; disabling the
C popup does not immediately stop the shell or start Dunst.

If activation fails, check `~/.local/state/cyberarch/notification-startup.log`
for automatic startup and `notification-renderer.log` in the same directory
for renderer errors. These paths follow `XDG_STATE_HOME` when set. If the build
fails, install `gtk3`, `gtk-layer-shell`, `pkgconf`, a compiler, and
`libastal-notifd-git`, then rerun setup. The existing notification service is
left available when the C renderer cannot be built.

The isolated tests exercise notification delivery, replacement, application
actions, keyboard dismissal, palette updates, service ownership changes and
the Dunst handoff. The user confirmed seeing the C-rendered test notifications
on the live desktop, including after the renderer update. Clean installation,
real multi-monitor behavior, screen-reader interaction, and long-running session
stability still need validation.
