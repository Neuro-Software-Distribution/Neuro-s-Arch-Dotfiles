/* NeurOS notification card renderer. --listen is for isolated integration tests;
 * it can acquire the notification service and must not be run casually. */
#include <gtk/gtk.h>
#include <gtk-layer-shell.h>
#include <astal-notifd.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

#define CARD_WIDTH 420
#define PAD 20
#define IMAGE_SIZE 66

typedef struct {
    const char *app, *title, *body, *image;
    GdkRGBA accent, secondary, foreground, background;
    int height, progress;
} Card;

static PangoLayout *layout(cairo_t *cr, const char *text, const char *font,
                           int width, int max_lines)
{
    PangoLayout *p = pango_cairo_create_layout(cr);
    PangoFontDescription *desc = pango_font_description_from_string(font);
    pango_layout_set_font_description(p, desc);
    pango_font_description_free(desc);
    pango_layout_set_text(p, text ? text : "", -1);
    pango_layout_set_width(p, width * PANGO_SCALE);
    pango_layout_set_wrap(p, PANGO_WRAP_WORD_CHAR);
    pango_layout_set_ellipsize(p, PANGO_ELLIPSIZE_END);
    pango_layout_set_height(p, -max_lines);
    return p;
}

static void color(cairo_t *cr, const GdkRGBA *c, double opacity)
{
    cairo_set_source_rgba(cr, c->red, c->green, c->blue, c->alpha * opacity);
}

static void silhouette(cairo_t *cr, int width, int height)
{
    cairo_new_path(cr);
    cairo_move_to(cr, 1, 1);
    cairo_line_to(cr, width - 19, 1);
    cairo_line_to(cr, width - 1, 19);
    cairo_line_to(cr, width - 1, height - 1);
    cairo_line_to(cr, 19, height - 1);
    cairo_line_to(cr, 1, height - 19);
    cairo_close_path(cr);
}

static GdkPixbuf *load_image(const char *path)
{
    if (!path || !*path) return NULL;
    GError *error = NULL;
    GdkPixbuf *image = gdk_pixbuf_new_from_file_at_scale(path, IMAGE_SIZE, IMAGE_SIZE, TRUE, &error);
    if (error) { g_error_free(error); return NULL; }
    return image;
}

static void draw_text(cairo_t *cr, PangoLayout *p, double x, double y,
                      const GdkRGBA *c, double opacity)
{
    cairo_move_to(cr, x, y);
    color(cr, c, opacity);
    pango_cairo_show_layout(cr, p);
}

static int draw_card(cairo_t *cr, Card *card)
{
    GdkPixbuf *image = load_image(card->image);
    int text_x = image ? PAD + IMAGE_SIZE + 16 : PAD;
    int text_width = CARD_WIDTH - text_x - PAD - 4;
    const char *app_label = card->app;
    if (!app_label || !*app_label || g_ascii_strcasecmp(app_label, "notify-send") == 0)
        app_label = "Intercom";
    PangoLayout *app = layout(cr, app_label, "Rajdhani Bold 9", text_width - 72, 1);
    PangoLayout *title = layout(cr, card->title, "Rajdhani Bold 13", text_width, 2);
    PangoLayout *body = layout(cr, card->body, "Rajdhani Medium 11", text_width, 3);
    int title_h, body_h;
    pango_layout_get_pixel_size(title, NULL, &title_h);
    pango_layout_get_pixel_size(body, NULL, &body_h);
    int content_h = 27 + title_h + (body_h ? 4 + body_h : 0);
    card->height = MAX(104, PAD + MAX(content_h, image ? IMAGE_SIZE : 0) + 19);
    if (card->progress >= 0) card->height += 12;

    cairo_save(cr);
    cairo_set_operator(cr, CAIRO_OPERATOR_CLEAR); cairo_paint(cr);
    cairo_set_operator(cr, CAIRO_OPERATOR_OVER);
    silhouette(cr, CARD_WIDTH, card->height);
    color(cr, &card->background, 0.98); cairo_fill_preserve(cr);
    color(cr, &card->accent, 0.88); cairo_set_line_width(cr, 1.5); cairo_stroke(cr);

    /* Two short inset rails echo the message and weather panel geometry. */
    color(cr, &card->accent, 0.32); cairo_set_line_width(cr, 1);
    cairo_move_to(cr, 12, 12); cairo_line_to(cr, 39, 12);
    cairo_move_to(cr, CARD_WIDTH - 39, card->height - 10);
    cairo_line_to(cr, CARD_WIDTH - 12, card->height - 10); cairo_stroke(cr);
    color(cr, &card->accent, 0.95);
    cairo_move_to(cr, text_x, PAD + 9); cairo_line_to(cr, text_x + 7, PAD + 2);
    cairo_line_to(cr, text_x + 7, PAD + 9); cairo_close_path(cr); cairo_fill(cr);
    PangoLayout *brand = layout(cr, "NeurOS //", "Rajdhani Bold 9", 64, 1);
    draw_text(cr, brand, text_x + 12, PAD - 1, &card->secondary, 1);
    draw_text(cr, app, text_x + 75, PAD - 1, &card->secondary, 0.8);
    draw_text(cr, title, text_x, PAD + 24, &card->foreground, 1);
    if (body_h) draw_text(cr, body, text_x, PAD + 28 + title_h, &card->foreground, 0.82);
    if (card->progress >= 0) {
        color(cr, &card->accent, 0.25);
        cairo_rectangle(cr, text_x, card->height - 15, text_width, 3); cairo_fill(cr);
        color(cr, &card->secondary, 0.95);
        cairo_rectangle(cr, text_x, card->height - 15, text_width * card->progress / 100.0, 3); cairo_fill(cr);
    }

    if (image) {
        int iw = gdk_pixbuf_get_width(image), ih = gdk_pixbuf_get_height(image);
        double ix = PAD + (IMAGE_SIZE - iw) / 2.0, iy = PAD + (IMAGE_SIZE - ih) / 2.0;
        color(cr, &card->accent, 0.45); cairo_set_line_width(cr, 1);
        cairo_rectangle(cr, PAD - 0.5, PAD - 0.5, IMAGE_SIZE + 1, IMAGE_SIZE + 1); cairo_stroke(cr);
        gdk_cairo_set_source_pixbuf(cr, image, ix, iy); cairo_paint(cr);
        g_object_unref(image);
    }
    g_object_unref(brand); g_object_unref(app); g_object_unref(title); g_object_unref(body);
    cairo_restore(cr);
    return card->height;
}

static gboolean on_draw(GtkWidget *widget, cairo_t *cr, gpointer data)
{
    (void)widget;
    draw_card(cr, data);
    return FALSE;
}

static void shape_input(GtkWidget *widget, gpointer data)
{
    Card *card = data;
    GdkWindow *window = gtk_widget_get_window(widget);
    if (!window) return;
    cairo_region_t *region = cairo_region_create();
    for (int y = 0; y < card->height; y++) {
        int left = y >= card->height - 19 ? y - (card->height - 19) : 0;
        int right = y < 19 ? 19 - y : 0;
        cairo_rectangle_int_t row = { left, y, CARD_WIDTH - left - right, 1 };
        cairo_region_union_rectangle(region, &row);
    }
    gdk_window_input_shape_combine_region(window, region, 0, 0);
    cairo_region_destroy(region);
}

static gboolean close_window(gpointer data)
{
    gtk_widget_destroy(GTK_WIDGET(data));
    return G_SOURCE_REMOVE;
}

static gboolean on_click(GtkWidget *widget, GdkEventButton *event, gpointer data)
{
    (void)event; (void)data;
    gtk_widget_destroy(widget);
    return TRUE;
}

typedef struct {
    Card card;
    GtkWidget *window;
    AstalNotifdNotification *notification;
    gchar *image, *body;
    guint id, timer;
    gboolean critical;
} LiveCard;

static GList *live_cards;
static Card live_palette;
static GFile *palette_target;
static GDBusConnection *readiness_bus;
static gchar *readiness_token;
static guint renderer_owner, readiness_poll_source, readiness_timeout_source;
static gboolean readiness_pending, renderer_ready;
static void renderer_name_acquired(GDBusConnection *bus, const gchar *name, gpointer data);
static void renderer_name_lost(GDBusConnection *bus, const gchar *name, gpointer data);
static gboolean readiness_poll(gpointer data);
static gboolean readiness_timeout(gpointer data);

static gboolean load_palette(Card *card, const char *path)
{
    if (!path) return FALSE;
    GKeyFile *file = g_key_file_new();
    if (!g_key_file_load_from_file(file, path, G_KEY_FILE_NONE, NULL)) { g_key_file_unref(file); return FALSE; }
    gchar *accent = g_key_file_get_string(file, "palette", "accent", NULL);
    gchar *secondary = g_key_file_get_string(file, "palette", "secondary", NULL);
    gchar *foreground = g_key_file_get_string(file, "palette", "foreground", NULL);
    gchar *background = g_key_file_get_string(file, "palette", "background", NULL);
    Card next = *card;
    gboolean valid = accent && secondary && foreground && background &&
        gdk_rgba_parse(&next.accent, accent) && gdk_rgba_parse(&next.secondary, secondary) &&
        gdk_rgba_parse(&next.foreground, foreground) && gdk_rgba_parse(&next.background, background);
    if (valid) *card = next;
    g_free(accent); g_free(secondary); g_free(foreground); g_free(background);
    g_key_file_unref(file);
    return valid;
}

static void palette_changed(GFileMonitor *monitor, GFile *file, GFile *other,
                            GFileMonitorEvent event, gpointer data)
{
    (void)monitor; (void)data;
    if (event != G_FILE_MONITOR_EVENT_CHANGES_DONE_HINT && event != G_FILE_MONITOR_EVENT_CREATED &&
        event != G_FILE_MONITOR_EVENT_MOVED_IN && event != G_FILE_MONITOR_EVENT_RENAMED) return;
    if (!g_file_equal(file, palette_target) && (!other || !g_file_equal(other, palette_target))) return;
    gchar *path = g_file_get_path(palette_target);
    gboolean valid = load_palette(&live_palette, path);
    g_free(path);
    if (!valid) return;
    for (GList *it = live_cards; it; it = it->next) {
        LiveCard *item = it->data;
        if (!item->critical) item->card.accent = live_palette.accent;
        item->card.secondary = live_palette.secondary;
        item->card.foreground = live_palette.foreground; item->card.background = live_palette.background;
        gtk_widget_queue_draw(item->window);
    }
    g_message("Notification palette updated");
}

static void reposition_cards(void)
{
    int top = 64;
    for (GList *it = live_cards; it; it = it->next) {
        LiveCard *item = it->data;
        gtk_layer_set_margin(GTK_WINDOW(item->window), GTK_LAYER_SHELL_EDGE_TOP, top);
        top += item->card.height + 8;
    }
}

static void live_destroy(GtkWidget *widget, gpointer data)
{
    (void)widget;
    LiveCard *item = data;
    live_cards = g_list_remove(live_cards, item);
    if (item->timer) g_source_remove(item->timer);
    g_clear_object(&item->notification);
    g_free(item->image);
    g_free(item->body);
    g_free(item);
    reposition_cards();
}

static gboolean live_timeout(gpointer data)
{
    LiveCard *item = data;
    item->timer = 0;
    gtk_widget_destroy(item->window);
    return G_SOURCE_REMOVE;
}

static void choose_action(GtkMenuItem *menu_item, gpointer data)
{
    (void)data;
    AstalNotifdAction *action = g_object_get_data(G_OBJECT(menu_item), "notification-action");
    AstalNotifdNotification *notification = g_object_get_data(G_OBJECT(menu_item), "notification");
    GtkWidget *window = g_object_get_data(G_OBJECT(menu_item), "notification-window");
    if (action) astal_notifd_action_invoke(action);
    if (notification && !astal_notifd_notification_get_resident(notification)) astal_notifd_notification_dismiss(notification);
    if (window) gtk_widget_destroy(window);
}

static void show_actions(LiveCard *item, GdkEventButton *event)
{
    GtkWidget *menu = gtk_menu_new();
    for (GList *it = astal_notifd_notification_get_actions(item->notification); it; it = it->next) {
        AstalNotifdAction *action = it->data;
        const char *label = astal_notifd_action_get_label(action);
        GtkWidget *entry = gtk_menu_item_new_with_label(label && *label ? label : astal_notifd_action_get_id(action));
        g_object_set_data_full(G_OBJECT(entry), "notification-action", g_object_ref(action), g_object_unref);
        /* Keep the notification alive while the menu is open. */
        g_object_set_data_full(G_OBJECT(entry), "notification", g_object_ref(item->notification), g_object_unref);
        g_object_set_data_full(G_OBJECT(entry), "notification-window", g_object_ref(item->window), g_object_unref);
        g_signal_connect(entry, "activate", G_CALLBACK(choose_action), NULL);
        gtk_menu_shell_append(GTK_MENU_SHELL(menu), entry);
    }
    g_signal_connect_swapped(menu, "selection-done", G_CALLBACK(gtk_widget_destroy), menu);
    gtk_widget_show_all(menu);
    if (event) gtk_menu_popup_at_pointer(GTK_MENU(menu), (GdkEvent *)event);
    else gtk_menu_popup_at_widget(GTK_MENU(menu), item->window, GDK_GRAVITY_SOUTH_EAST, GDK_GRAVITY_NORTH_EAST, NULL);
}

static void activate_live(LiveCard *item, GdkEventButton *event)
{
    GList *actions = astal_notifd_notification_get_actions(item->notification);
    AstalNotifdAction *selected = NULL;
    for (GList *it = actions; it; it = it->next) {
        AstalNotifdAction *action = it->data;
        if (g_strcmp0(astal_notifd_action_get_id(action), "default") == 0) { selected = action; break; }
    }
    if (!selected && actions && !actions->next) selected = actions->data;
    if (!selected && actions) { show_actions(item, event); return; }
    GtkWidget *window = g_object_ref(item->window);
    AstalNotifdNotification *notification = g_object_ref(item->notification);
    if (selected) {
        astal_notifd_action_invoke(selected);
        if (!astal_notifd_notification_get_resident(notification)) astal_notifd_notification_dismiss(notification);
    }
    else astal_notifd_notification_dismiss(notification);
    gtk_widget_destroy(window);
    g_object_unref(notification); g_object_unref(window);
}

static void dismiss_live(LiveCard *item)
{
    GtkWidget *window = g_object_ref(item->window);
    AstalNotifdNotification *notification = g_object_ref(item->notification);
    astal_notifd_notification_dismiss(notification);
    gtk_widget_destroy(window);
    g_object_unref(notification); g_object_unref(window);
}

static gboolean live_click(GtkWidget *widget, GdkEventButton *event, gpointer data)
{
    (void)widget;
    LiveCard *item = data;
    if (event->button == 1) {
        activate_live(item, event);
    } else if (event->button == 2 && astal_notifd_notification_get_actions(item->notification)) {
        show_actions(item, event);
    } else if (event->button == 3) {
        dismiss_live(item);
    } else return FALSE;
    return TRUE;
}

static void renderer_method(GDBusConnection *connection, const gchar *sender, const gchar *path,
                            const gchar *interface, const gchar *method, GVariant *params,
                            GDBusMethodInvocation *invocation, gpointer data)
{
    (void)connection; (void)sender; (void)path; (void)interface; (void)params; (void)data;
    gboolean handled = renderer_ready && live_cards != NULL;
    if (handled) {
        LiveCard *item = live_cards->data;
        if (g_strcmp0(method, "Read") == 0) activate_live(item, NULL);
        else if (g_strcmp0(method, "Dismiss") == 0) dismiss_live(item);
        else handled = FALSE;
    }
    g_dbus_method_invocation_return_value(invocation, g_variant_new("(b)", handled));
}

static const GDBusInterfaceVTable renderer_vtable = { .method_call = renderer_method };
static const char renderer_xml[] =
    "<node><interface name='io.neuros.NotificationRenderer'>"
    "<method name='Read'><arg type='b' direction='out'/></method>"
    "<method name='Dismiss'><arg type='b' direction='out'/></method>"
    "</interface></node>";

static void close_id(guint id)
{
    for (GList *it = live_cards; it; it = it->next) {
        LiveCard *item = it->data;
        if (item->id == id) { gtk_widget_destroy(item->window); return; }
    }
}

static void received(AstalNotifdNotifd *service, guint id, gboolean replaced, gpointer data)
{
    (void)replaced; (void)data;
    close_id(id);
    AstalNotifdNotification *n = astal_notifd_notifd_get_notification(service, id);
    if (!n) return;
    if (g_strcmp0(astal_notifd_notification_get_app_name(n), "NeurOS internal readiness") == 0 &&
        g_strcmp0(astal_notifd_notification_get_summary(n), readiness_token) == 0) {
        astal_notifd_notification_dismiss(n);
        g_object_unref(n);
        if (!renderer_owner) renderer_owner = g_bus_own_name(G_BUS_TYPE_SESSION, "io.neuros.NotificationRenderer",
            G_BUS_NAME_OWNER_FLAGS_DO_NOT_QUEUE, NULL, renderer_name_acquired, renderer_name_lost, NULL, NULL);
        return;
    }
    if (!renderer_ready || astal_notifd_notifd_get_dont_disturb(service)) { g_object_unref(n); return; }
    while (g_list_length(live_cards) >= 4) {
        LiveCard *oldest = g_list_last(live_cards)->data;
        gtk_widget_destroy(oldest->window);
    }
    LiveCard *item = g_new0(LiveCard, 1);
    item->id = id; item->notification = n; item->card = live_palette;
    item->critical = astal_notifd_notification_get_urgency(n) == ASTAL_NOTIFD_URGENCY_CRITICAL;
    if (item->critical) gdk_rgba_parse(&item->card.accent, "#ff4a55");
    GVariant *progress = astal_notifd_notification_get_hint(n, "value");
    if (progress) {
        if (g_variant_is_of_type(progress, G_VARIANT_TYPE_INT32))
            item->card.progress = CLAMP(g_variant_get_int32(progress), 0, 100);
        else if (g_variant_is_of_type(progress, G_VARIANT_TYPE_UINT32))
            item->card.progress = (int)MIN(g_variant_get_uint32(progress), 100u);
        g_variant_unref(progress);
    }
    item->card.app = astal_notifd_notification_get_app_name(n);
    item->card.title = astal_notifd_notification_get_summary(n);
    const char *body_text = astal_notifd_notification_get_body(n);
    GError *markup_error = NULL;
    if (!body_text || !pango_parse_markup(body_text, -1, 0, NULL, &item->body, NULL, &markup_error)) {
        g_clear_error(&markup_error);
        item->body = g_strdup(body_text ? body_text : "");
    }
    item->card.body = item->body;
    item->image = astal_notifd_notification_get_image(n);
    if (item->image && g_str_has_prefix(item->image, "file://")) {
        gchar *path = g_filename_from_uri(item->image, NULL, NULL);
        g_free(item->image); item->image = path;
    }
    if (!item->image || !*item->image) {
        g_free(item->image);
        const char *icon = astal_notifd_notification_get_app_icon(n);
        item->image = icon && g_path_is_absolute(icon) ? g_strdup(icon) : NULL;
        if (icon && *icon && !item->image) {
            GtkIconInfo *info = gtk_icon_theme_lookup_icon(gtk_icon_theme_get_default(), icon, IMAGE_SIZE, 0);
            if (info) {
                item->image = g_strdup(gtk_icon_info_get_filename(info));
                g_object_unref(info);
            }
        }
    }
    item->card.image = item->image;
    cairo_surface_t *measure = cairo_image_surface_create(CAIRO_FORMAT_ARGB32, CARD_WIDTH, 512);
    cairo_t *cr = cairo_create(measure); draw_card(cr, &item->card);
    cairo_destroy(cr); cairo_surface_destroy(measure);
    item->window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_layer_init_for_window(GTK_WINDOW(item->window));
    gtk_layer_set_layer(GTK_WINDOW(item->window), GTK_LAYER_SHELL_LAYER_OVERLAY);
    gtk_layer_set_anchor(GTK_WINDOW(item->window), GTK_LAYER_SHELL_EDGE_TOP, TRUE);
    gtk_layer_set_anchor(GTK_WINDOW(item->window), GTK_LAYER_SHELL_EDGE_RIGHT, TRUE);
    gtk_layer_set_margin(GTK_WINDOW(item->window), GTK_LAYER_SHELL_EDGE_RIGHT, 24);
    gtk_widget_set_app_paintable(item->window, TRUE);
    GdkVisual *visual = gdk_screen_get_rgba_visual(gtk_widget_get_screen(item->window));
    if (visual) gtk_widget_set_visual(item->window, visual);
    GtkWidget *area = gtk_drawing_area_new();
    gtk_widget_set_size_request(area, CARD_WIDTH, item->card.height);
    AtkObject *accessible = gtk_widget_get_accessible(area);
    atk_object_set_role(accessible, ATK_ROLE_NOTIFICATION);
    atk_object_set_name(accessible, item->card.title ? item->card.title : "Notification");
    atk_object_set_description(accessible, item->card.body ? item->card.body : "");
    gtk_container_add(GTK_CONTAINER(item->window), area);
    gtk_widget_add_events(item->window, GDK_BUTTON_PRESS_MASK);
    g_signal_connect(area, "draw", G_CALLBACK(on_draw), &item->card);
    g_signal_connect(item->window, "button-press-event", G_CALLBACK(live_click), item);
    g_signal_connect(item->window, "destroy", G_CALLBACK(live_destroy), item);
    g_signal_connect(item->window, "realize", G_CALLBACK(shape_input), &item->card);
    live_cards = g_list_prepend(live_cards, item);
    reposition_cards();
    gint timeout_ms = astal_notifd_notification_get_expire_timeout(n);
    if (timeout_ms < 0) timeout_ms = item->critical ? 0 : 8000;
    if (timeout_ms > 0) item->timer = g_timeout_add((guint)timeout_ms, live_timeout, item);
    gtk_widget_show_all(item->window);
    if (item->card.progress >= 0) g_message("Notification popup displayed: %u (progress %d)", id, item->card.progress);
    else g_message("Notification popup displayed: %u", id);
}

static void resolved(AstalNotifdNotifd *service, guint id, int reason, gpointer data)
{
    (void)service; (void)reason; (void)data;
    close_id(id);
    g_message("Notification resolved: %u", id);
}

/* Astal's proxy cannot reliably recover if initialized against Dunst. Never
 * activate another server during this check, and refuse an unknown owner. */
static gboolean compatible_notification_owner(void)
{
    GError *error = NULL;
    GDBusConnection *bus = g_bus_get_sync(G_BUS_TYPE_SESSION, NULL, &error);
    if (!bus) { g_printerr("Cannot connect to session bus: %s\n", error->message); g_clear_error(&error); return FALSE; }
    GVariant *result = g_dbus_connection_call_sync(bus, "org.freedesktop.DBus", "/org/freedesktop/DBus",
        "org.freedesktop.DBus", "NameHasOwner", g_variant_new("(s)", "org.freedesktop.Notifications"),
        G_VARIANT_TYPE("(b)"), G_DBUS_CALL_FLAGS_NO_AUTO_START, 2000, NULL, &error);
    if (!result) { g_printerr("Cannot inspect notification service: %s\n", error->message); g_clear_error(&error); g_object_unref(bus); return FALSE; }
    gboolean owned;
    g_variant_get(result, "(b)", &owned); g_variant_unref(result);
    if (!owned) { g_object_unref(bus); return TRUE; }
    result = g_dbus_connection_call_sync(bus, "org.freedesktop.Notifications", "/org/freedesktop/Notifications",
        "org.freedesktop.Notifications", "GetServerInformation", NULL, G_VARIANT_TYPE("(ssss)"),
        G_DBUS_CALL_FLAGS_NO_AUTO_START, 2000, NULL, &error);
    if (!result) { g_printerr("Cannot identify notification service: %s\n", error->message); g_clear_error(&error); g_object_unref(bus); return FALSE; }
    const char *name, *vendor, *version, *spec;
    g_variant_get(result, "(&s&s&s&s)", &name, &vendor, &version, &spec);
    gboolean compatible = g_strcmp0(name, "notifd") == 0 && g_strcmp0(vendor, "astal") == 0;
    if (!compatible) g_printerr("Another notification server owns the service (%s); leaving it running.\n", name);
    g_variant_unref(result); g_object_unref(bus);
    return compatible;
}

static void renderer_name_acquired(GDBusConnection *bus, const gchar *name, gpointer data)
{
    (void)bus; (void)name; (void)data;
    renderer_ready = TRUE;
    if (readiness_timeout_source) { g_source_remove(readiness_timeout_source); readiness_timeout_source = 0; }
    g_message("NeurOS notification renderer ready");
}

static void renderer_name_lost(GDBusConnection *bus, const gchar *name, gpointer data)
{
    (void)bus; (void)name; (void)data;
    g_printerr("Another NeurOS notification renderer is running, or the session bus is unavailable.\n");
    gtk_main_quit();
}

static void probe_sent(GObject *object, GAsyncResult *result, gpointer data)
{
    (void)data;
    GError *error = NULL;
    GVariant *reply = g_dbus_connection_call_finish(G_DBUS_CONNECTION(object), result, &error);
    if (reply) g_variant_unref(reply);
    else { g_clear_error(&error); readiness_pending = FALSE; }
}

static void probe_server(GObject *object, GAsyncResult *result, gpointer data)
{
    (void)data;
    GError *error = NULL;
    GVariant *reply = g_dbus_connection_call_finish(G_DBUS_CONNECTION(object), result, &error);
    if (!reply) { g_clear_error(&error); readiness_pending = FALSE; return; }
    const char *name, *vendor, *version, *spec;
    g_variant_get(reply, "(&s&s&s&s)", &name, &vendor, &version, &spec);
    gboolean astal = g_strcmp0(name, "notifd") == 0 && g_strcmp0(vendor, "astal") == 0;
    g_variant_unref(reply);
    if (!astal) { readiness_pending = FALSE; return; }
    GVariant *actions = g_variant_new_strv(NULL, 0);
    GVariant *hints = g_variant_new_array(G_VARIANT_TYPE("{sv}"), NULL, 0);
    g_dbus_connection_call(readiness_bus, "org.freedesktop.Notifications", "/org/freedesktop/Notifications",
        "org.freedesktop.Notifications", "Notify",
        g_variant_new("(susss@as@a{sv}i)", "NeurOS internal readiness", 0, "", readiness_token, "", actions, hints, 1000),
        G_VARIANT_TYPE("(u)"), G_DBUS_CALL_FLAGS_NO_AUTO_START, 1000, NULL, probe_sent, NULL);
}

static gboolean readiness_poll(gpointer data)
{
    (void)data;
    if (renderer_ready) { readiness_poll_source = 0; return G_SOURCE_REMOVE; }
    if (!readiness_pending) {
        readiness_pending = TRUE;
        g_dbus_connection_call(readiness_bus, "org.freedesktop.Notifications", "/org/freedesktop/Notifications",
            "org.freedesktop.Notifications", "GetServerInformation", NULL, G_VARIANT_TYPE("(ssss)"),
            G_DBUS_CALL_FLAGS_NO_AUTO_START, 1000, NULL, probe_server, NULL);
    }
    return G_SOURCE_CONTINUE;
}

static gboolean readiness_timeout(gpointer data)
{
    (void)data;
    readiness_timeout_source = 0;
    if (!renderer_ready) { g_printerr("Notification renderer could not verify the Astal connection.\n"); gtk_main_quit(); }
    return G_SOURCE_REMOVE;
}

static void notification_owner_vanished(GDBusConnection *bus, const gchar *name, gpointer data)
{
    (void)bus; (void)name; (void)data;
    if (!renderer_ready) return;
    renderer_ready = FALSE;
    if (renderer_owner) { g_bus_unown_name(renderer_owner); renderer_owner = 0; }
    readiness_pending = FALSE;
    if (!readiness_poll_source) readiness_poll_source = g_timeout_add(100, readiness_poll, NULL);
    if (readiness_timeout_source) g_source_remove(readiness_timeout_source);
    readiness_timeout_source = g_timeout_add_seconds(8, readiness_timeout, NULL);
}

int main(int argc, char **argv)
{
    char *output = NULL, *app = NULL, *title = NULL, *body = NULL, *image = NULL;
    char *accent = NULL, *secondary = NULL, *foreground = NULL, *background = NULL, *palette_file = NULL;
    gboolean preview = FALSE, listen = FALSE;
    int progress = -1;
    GOptionEntry entries[] = {
        {"render", 0, 0, G_OPTION_ARG_FILENAME, &output, "Render a PNG without a display", "FILE"},
        {"preview", 0, 0, G_OPTION_ARG_NONE, &preview, "Show a temporary Wayland preview", NULL},
        {"listen", 0, 0, G_OPTION_ARG_NONE, &listen, "Listen for notifications on an isolated Astal session", NULL},
        {"app", 0, 0, G_OPTION_ARG_STRING, &app, "Application name", "TEXT"},
        {"title", 0, 0, G_OPTION_ARG_STRING, &title, "Notification title", "TEXT"},
        {"body", 0, 0, G_OPTION_ARG_STRING, &body, "Notification body", "TEXT"},
        {"image", 0, 0, G_OPTION_ARG_FILENAME, &image, "Image preview path", "FILE"},
        {"progress", 0, 0, G_OPTION_ARG_INT, &progress, "Progress percentage", "0-100"},
        {"accent", 0, 0, G_OPTION_ARG_STRING, &accent, "Primary color", "COLOR"},
        {"secondary", 0, 0, G_OPTION_ARG_STRING, &secondary, "Secondary color", "COLOR"},
        {"foreground", 0, 0, G_OPTION_ARG_STRING, &foreground, "Text color", "COLOR"},
        {"background", 0, 0, G_OPTION_ARG_STRING, &background, "Background color", "COLOR"},
        {"palette-file", 0, 0, G_OPTION_ARG_FILENAME, &palette_file, "Palette file to load and monitor", "FILE"},
        {NULL}
    };
    GOptionContext *options = g_option_context_new("--render FILE | --preview");
    g_option_context_add_main_entries(options, entries, NULL);
    GError *error = NULL;
    if (!g_option_context_parse(options, &argc, &argv, &error)) {
        g_printerr("%s\n", error->message); g_error_free(error); g_option_context_free(options); return 2;
    }
    g_option_context_free(options);
    if ((!!output + !!preview + !!listen) != 1 || argc != 1) {
        g_printerr("Choose exactly one of --render FILE, --preview, or --listen.\n"); return 2;
    }
    if (progress < -1 || progress > 100) { g_printerr("Progress must be between 0 and 100.\n"); return 2; }
    Card card = { .app = app ? app : "SYSTEM", .title = title ? title : "Screenshot saved",
                  .body = body ? body : "Saved to ~/Pictures/Screenshots & copied", .image = image, .progress = progress };
    if (!gdk_rgba_parse(&card.accent, accent ? accent : "#c170ff") ||
        !gdk_rgba_parse(&card.secondary, secondary ? secondary : "#00eb74") ||
        !gdk_rgba_parse(&card.foreground, foreground ? foreground : "#e1e8fa") ||
        !gdk_rgba_parse(&card.background, background ? background : "#070912")) {
        g_printerr("Invalid palette color.\n"); return 2;
    }
    if (palette_file && !load_palette(&card, palette_file)) {
        g_printerr("Cannot load palette file.\n"); return 2;
    }
    cairo_surface_t *surface = cairo_image_surface_create(CAIRO_FORMAT_ARGB32, CARD_WIDTH, 512);
    cairo_t *cr = cairo_create(surface);
    int height = draw_card(cr, &card);
    cairo_destroy(cr);
    if (output) {
        cairo_surface_t *cropped = cairo_image_surface_create(CAIRO_FORMAT_ARGB32, CARD_WIDTH, height);
        cr = cairo_create(cropped);
        cairo_set_operator(cr, CAIRO_OPERATOR_SOURCE); cairo_set_source_surface(cr, surface, 0, 0); cairo_paint(cr);
        cairo_destroy(cr);
        cairo_status_t status = cairo_surface_write_to_png(cropped, output);
        cairo_surface_destroy(cropped); cairo_surface_destroy(surface);
        if (status != CAIRO_STATUS_SUCCESS) { g_printerr("%s\n", cairo_status_to_string(status)); return 1; }
        return 0;
    }
    cairo_surface_destroy(surface);
    if (!gtk_init_check(&argc, &argv)) { g_printerr("Cannot open a graphical display.\n"); return 1; }
    if (!gtk_layer_is_supported()) { g_printerr("Wayland layer shell is unavailable.\n"); return 1; }
    if (listen) {
        if (!compatible_notification_owner()) return 1;
        live_palette = card;
        GFileMonitor *monitor = NULL;
        gchar *default_palette = NULL;
        if (!palette_file) {
            default_palette = g_build_filename(g_get_user_config_dir(), "cyberarch", "notification.palette", NULL);
            palette_file = default_palette;
            load_palette(&live_palette, palette_file);
        }
        palette_target = g_file_new_for_path(palette_file);
        GFile *parent = g_file_get_parent(palette_target);
        if (parent) monitor = g_file_monitor_directory(parent, G_FILE_MONITOR_WATCH_MOVES, NULL, NULL);
        if (monitor) g_signal_connect(monitor, "changed", G_CALLBACK(palette_changed), NULL);
        g_clear_object(&parent);
        AstalNotifdNotifd *service = astal_notifd_get_default();
        if (!service) { g_printerr("Cannot initialize Astal notification service.\n"); return 1; }
        g_signal_connect(service, "notified", G_CALLBACK(received), NULL);
        g_signal_connect(service, "resolved", G_CALLBACK(resolved), NULL);
        readiness_bus = g_bus_get_sync(G_BUS_TYPE_SESSION, NULL, NULL);
        if (!readiness_bus) { g_printerr("Cannot connect to session bus.\n"); return 1; }
        GError *interface_error = NULL;
        GDBusNodeInfo *node = g_dbus_node_info_new_for_xml(renderer_xml, &interface_error);
        guint registration = node ? g_dbus_connection_register_object(readiness_bus, "/io/neuros/NotificationRenderer",
            node->interfaces[0], &renderer_vtable, NULL, NULL, &interface_error) : 0;
        if (!registration) {
            g_printerr("Cannot register notification controls: %s\n", interface_error ? interface_error->message : "unknown error");
            g_clear_error(&interface_error); if (node) g_dbus_node_info_unref(node); return 1;
        }
        readiness_token = g_uuid_string_random();
        guint watch = g_bus_watch_name(G_BUS_TYPE_SESSION, "org.freedesktop.Notifications",
                                       G_BUS_NAME_WATCHER_FLAGS_NONE, NULL, notification_owner_vanished, NULL, NULL);
        readiness_poll_source = g_timeout_add(100, readiness_poll, NULL);
        readiness_timeout_source = g_timeout_add_seconds(8, readiness_timeout, NULL);
        gtk_main();
        g_bus_unwatch_name(watch);
        if (renderer_owner) g_bus_unown_name(renderer_owner);
        g_dbus_connection_unregister_object(readiness_bus, registration);
        g_dbus_node_info_unref(node);
        g_clear_object(&readiness_bus); g_free(readiness_token);
        g_clear_object(&monitor); g_clear_object(&palette_target); g_free(default_palette);
        g_object_unref(service);
        return renderer_ready ? 0 : 1;
    }
    GtkWidget *window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_layer_init_for_window(GTK_WINDOW(window));
    gtk_layer_set_layer(GTK_WINDOW(window), GTK_LAYER_SHELL_LAYER_OVERLAY);
    gtk_layer_set_anchor(GTK_WINDOW(window), GTK_LAYER_SHELL_EDGE_TOP, TRUE);
    gtk_layer_set_anchor(GTK_WINDOW(window), GTK_LAYER_SHELL_EDGE_RIGHT, TRUE);
    gtk_layer_set_margin(GTK_WINDOW(window), GTK_LAYER_SHELL_EDGE_TOP, 64);
    gtk_layer_set_margin(GTK_WINDOW(window), GTK_LAYER_SHELL_EDGE_RIGHT, 24);
    gtk_widget_set_app_paintable(window, TRUE);
    GdkScreen *screen = gtk_widget_get_screen(window);
    GdkVisual *visual = gdk_screen_get_rgba_visual(screen);
    if (visual) gtk_widget_set_visual(window, visual);
    GtkWidget *area = gtk_drawing_area_new();
    gtk_widget_set_size_request(area, CARD_WIDTH, height);
    gtk_container_add(GTK_CONTAINER(window), area);
    gtk_widget_add_events(window, GDK_BUTTON_PRESS_MASK);
    g_signal_connect(area, "draw", G_CALLBACK(on_draw), &card);
    g_signal_connect(window, "button-press-event", G_CALLBACK(on_click), NULL);
    g_signal_connect(window, "realize", G_CALLBACK(shape_input), &card);
    g_signal_connect(window, "destroy", G_CALLBACK(gtk_main_quit), NULL);
    gtk_widget_show_all(window);
    g_timeout_add_seconds(8, close_window, window);
    gtk_main();
    return 0;
}
