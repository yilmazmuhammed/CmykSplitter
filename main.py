import os
import time
from tkinter import filedialog
from tkinter import *

import numpy as np
from PIL import Image, ImageTk


class MyImage:
    def __init__(self, filepath, maxsize):
        self.original_filepath = filepath
        self.original = Image.open(self.original_filepath)

        im_width, im_height = self.original.size
        max_width, max_height = maxsize
        if im_width > max_width or im_height > max_height:
            print("Fotoğraf max_size'den (ekran çözünürlüğü) büyük. Fotoğraf küçültülüyor.")
            ratio = min(max_width / im_width, max_height / im_height)
            self.original = self.original.resize((int(ratio * im_width), int(ratio * im_height)))
        self.timeout = ((self.original.size[0] * self.original.size[1]) / 1000 / 600 / 100)

        self.cmyk_arrays = {}
        self.cmyk_deviations = {}
        self.reset()

        h, w = self.original.size
        self.empty_array = np.zeros((w, h))

    def reset(self):
        cmyk_image = self.convert2cmyk(self.original)
        c, m, y, k = self.split_cmyk_array(cmyk_image)
        self.cmyk_arrays = {'c': c, 'm': m, 'y': y, 'k': k}
        self.cmyk_deviations = {'c': [0, 0], 'm': [0, 0], 'y': [0, 0], 'k': [0, 0]}

    @staticmethod
    def convert2cmyk(img):
        if img.getbands() == ('R', 'G', 'B'):
            print("RGB dosyası CMYK formatına dönüştürülüyor.")
            return img.convert("CMYK")
        elif img.getbands() == ('C', 'M', 'Y', 'K'):
            return img
        else:
            return None

    @staticmethod
    def split_cmyk_array(img):
        np_img_cmyk = np.array(img)
        c = np_img_cmyk[:, :, 0].astype(int)
        m = np_img_cmyk[:, :, 1].astype(int)
        y = np_img_cmyk[:, :, 2].astype(int)
        k = np_img_cmyk[:, :, 3].astype(int)
        return c, m, y, k

    def update_cmyk_deviations(self, color, direction):
        if direction not in ['Up', 'Down', 'Left', 'Right']:
            raise Exception("Yön tuşları harici bir tuşa basıldı")
        axis = 0 if direction in ['Up', 'Down'] else 1
        if direction in ['Up', 'Left']:
            self.cmyk_deviations[color][axis] += 1
        elif direction in ['Down', 'Right']:
            self.cmyk_deviations[color][axis] -= 1

    @property
    def cmyk_image(self):
        ret = {}
        for color in self.cmyk_arrays.keys():
            ret[color] = np.copy(self.cmyk_arrays[color])
            y, x = self.cmyk_deviations[color]
            sx, fx = (x, ret[color].shape[1]) if x >= 0 else (0, x)
            ret[color] = np.concatenate([self.empty_array[:, fx:], ret[color][:, sx:fx], self.empty_array[:, :sx]],
                                        axis=1)
            sy, fy = (y, ret[color].shape[0]) if y >= 0 else (0, y)
            ret[color] = np.concatenate([self.empty_array[fy:], ret[color][sy:fy], self.empty_array[:sy]])
        cmyk = np.dstack((ret['c'], ret['m'], ret['y'], ret['k']))
        return Image.fromarray(cmyk.astype(np.uint8), mode="CMYK")


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        print("resource_path:", os.path.join(base_path, relative_path))
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class MyApp(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title("CMYK Önizleyici - Daka Etiket")
        self.geometry("450x380")
        self.iconphoto(False, PhotoImage(file=resource_path('img/daka_logo.png')))

        menu_bar = Menu(self)
        self.config(menu=menu_bar)
        file_menu = Menu(menu_bar)
        menu_bar.add_cascade(label="Dosya", menu=file_menu)
        file_menu.add_command(label="Dosya aç", command=self.open_file)
        file_menu.add_command(label="Kaydet", command=self.save_cmyk_image)
        help_menu = Menu(menu_bar)
        menu_bar.add_cascade(label="Yardım", menu=help_menu)
        help_menu.add_command(label="Nasıl kullanılır", command=self.usage_box)
        help_menu.add_command(label="Hakkında", command=self.about_box)

        self.image = None
        self.last_update = None
        self._old_geo = None
        self.screen_image = None
        self.open_file(resource_path("img/daka_bg.png"))

        self.image_tk = None
        self.image_frame = Frame(self)
        self.image_label = Label(self.image_frame)
        self.image_label.pack(fill=BOTH, expand=YES)
        self.image_frame.pack(fill=BOTH, expand=YES)
        self.image_label.bind('<Configure>', self._resize_image)

        self.selected_color = ''
        self.bind_all('<Key>', self.key_event)
        self.counter = 0

    def open_file(self, filepath=None):
        self.last_update = time.time()
        if not filepath:
            filepath = filedialog.askopenfilename(
                title="Dosya seç",
                filetypes=(("Resim dosyaları", ("*.jpg", "*.png",)), ("Bütün dosyalar", "*.*"))
            )
        if filepath:
            self.image = MyImage(filepath, maxsize=(self.winfo_screenwidth(), self.winfo_screenheight()))
            self.geometry("%sx%s" % self.image.original.size)
            self.screen_image = self.image.cmyk_image

    def about_box(self):
        top = Toplevel(self)
        top.title("Hakkında")
        top.geometry("240x180")
        top.grab_set()

        top1 = Label(top, text="\nCMYK Önizleyici\n")
        top1.config(font=('times', 14, 'bold'))
        top2 = Label(top, text="Muhammed YILMAZ\n"
                               "mhyilmaz97@gmail.com\n")
        top3 = Label(top, text="2020")
        top3.config(font=('times', 12, 'bold'))
        top4 = Label(top, text="Bu program Daka Etiket için yapılmıştır.", font=('times', 9))
        top1.pack()
        top2.pack()
        top3.pack()
        top4.pack()

    def usage_box(self):
        top = Toplevel(self)
        top.title("Yardım")
        top.geometry("350x250")
        top.grab_set()

        top1 = Label(top, text="\nKullanım\n", font=('times', 14, 'bold'))
        # top1.config(font=('times', 14, 'bold'))
        top2 = Label(
            top, justify="left", wraplengt=300,
            text="- Önce hareket ettirmek istediğiniz rengi seçiniz. "
                 "Ardından yön tuşları ile seçili rengi hareket ettiriniz.\n"
                 "\n\n"
                 "c, m, y, k: Hareket ettirilecek rengi seçer.\n"
                 "Yön tuşları: Rengi hareket ettirir.\n"
                 "r: Resmi ilk haline döndürür.\n"
                 "s: Görünen resmi cmyk formatında kaydeder.\n"
        )
        top1.pack()
        top2.pack()

    def update_image_label(self):
        if time.time() - self.last_update > self.image.timeout:
            im_width, im_height = self.screen_image.size
            self.screen_image = self.image.cmyk_image.resize((im_width, im_height))

            self.image_tk = ImageTk.PhotoImage(self.screen_image)
            self.image_label.configure(image=self.image_tk)

            self.last_update = time.time()

    def toggle_window_geometry(self):
        if self._old_geo:
            self.geometry("%sx%s" % self._old_geo)
            self._old_geo = None
        else:
            self.geometry("%sx%s" % (root.winfo_screenwidth() - 1, root.winfo_screenheight() - 1))
            self._old_geo = (root.winfo_width(), root.winfo_height())

    def save_cmyk_image(self):
        if self.image:
            l_ = self.image.original_filepath.split(".")
            filepath = ".".join(l_[:-1]) + "_cmyk." + l_[-1]
            print("Dosya kaydediliyor:", filepath)
            self.image.cmyk_image.save(filepath)

    def key_event(self, event):
        if not self.image:
            return

        if event.keysym in ['f', 'F']:
            self.toggle_window_geometry()
        elif event.keysym in ['r', 'R']:
            self.image.reset()
            self.update_image_label()
        elif event.keysym in ['s', 'S']:
            self.save_cmyk_image()
        elif event.keysym in self.image.cmyk_deviations.keys():
            self.selected_color = event.keysym
        elif self.selected_color:
            if event.keysym in ['Up', 'Down', 'Left', 'Right']:
                self.image.update_cmyk_deviations(self.selected_color, event.keysym)
                self.update_image_label()
            elif event.keysym in ['r', 'R']:
                self.image.update_cmyk_deviations(self.selected_color, event.keysym)
                self.update_image_label()
            else:
                self.selected_color = ''

    def _resize_image(self, event):
        if self.image:
            im_width, im_height = self.image.original.size
            ratio = min(event.width / im_width, event.height / im_height)
            self.screen_image = self.image.cmyk_image.resize((int(ratio * im_width), int(ratio * im_height)))

            self.image_tk = ImageTk.PhotoImage(self.screen_image)
            self.image_label.configure(image=self.image_tk)


if __name__ == '__main__':
    root = MyApp()
    root.mainloop()
