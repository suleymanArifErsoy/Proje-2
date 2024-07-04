import tkinter as tk
from tkinter import simpledialog
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import numpy as np
import random 

# Sezar Şifreleme Fonksiyonu
def caesar_cipher(text, shift):
    result = ""
    for i in range(len(text)):
        char = text[i]
        if char.isupper():
            result += chr((ord(char) + shift - 65) % 26 + 65)
        elif char.islower():
            result += chr((ord(char) + shift - 97) % 26 + 97)
        else:
            result += char
    return result

# Sezar Şifre Çözme Fonksiyonu
def caesar_decipher(text, shift):
    return caesar_cipher(text, -shift)

# LSB Steganografi ile metin gizleme fonksiyonu
def metin_gomme(image, text,seed=42):
    
    img = np.array(image)
    # Metni binary formata dönüştür
    binary_text = ''.join(format(ord(char), '08b') for char in text)
    
    # Stop marker ekle
    stop_marker = '1111111111111111'
    binary_text += stop_marker
    data_len = len(binary_text)
    
    # Görsel boyutları
    height, width, _ = img.shape
    
    # Piksel koordinatlarını oluştur
    pixel_indices = [(i, j, k) for i in range(height) for j in range(width) for k in range(3)]
    
    # Rastgele karıştırmak için seed belirleyin (opsiyonel)
    if seed is not None:
        random.seed(seed)
    
    # Piksel indekslerini rastgele karıştır
    random.shuffle(pixel_indices)
    
    # Binary metni rastgele piksellere yerleştir
    data_index = 0
    for i, j, k in pixel_indices:
        if data_index < data_len:
            img[i][j][k] = int(format(img[i][j][k], "08b")[:-1] + binary_text[data_index], 2)
            data_index += 1
        if data_index >= data_len:
            break
    
    # Yeni görüntüyü döndür
    new_image = Image.fromarray(img)
    return new_image

# LSB Steganografi ile metni açığa çıkarma fonksiyonu
def extract_text(image,seed=42):
    img = np.array(image)
    binary_text = ""
    stop_marker = '1111111111111111'
    stop_marker_len = len(stop_marker)
    
    # Görsel boyutları
    height, width, _ = img.shape
    
    # Piksel koordinatlarını oluştur
    pixel_indices = [(i, j, k) for i in range(height) for j in range(width) for k in range(3)]
    
    # Rastgele karıştırmak için seed belirleyin (opsiyonel)
    if seed is not None:
        random.seed(seed)
    
    # Piksel indekslerini rastgele karıştır
    random.shuffle(pixel_indices)
    
    # Rastgele piksellerden metni çıkar
    for i, j, k in pixel_indices:
        binary_text += format(img[i][j][k], "08b")[-1]
        if binary_text[-stop_marker_len:] == stop_marker:
            binary_text = binary_text[:-stop_marker_len]
            text = ''.join([chr(int(binary_text[i:i+8], 2)) for i in range(0, len(binary_text), 8)])
            return text
    
    return ""

# PSNR hesaplama fonksiyonu
def psnr(original_image, stego_image):
    original = np.array(original_image).astype(np.float64)
    stego = np.array(stego_image).astype(np.float64)
    mse = np.mean((original - stego) ** 2)
    if mse == 0:
        return 100
    max_pixel = 255.0
    psnr_value = 20 * np.log10(max_pixel / np.sqrt(mse))
    return psnr_value

class SteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Steganography App")
        self.root.geometry("800x600")
        
        self.filename = ""
        self.image_label = None
        
        self.create_widgets()
        
    def create_widgets(self):
        self.file_button = tk.Button(self.root, text="Dosya Seç", command=self.load_file)
        self.file_button.pack()
        
        self.filename_label = tk.Label(self.root, text="Seçilen dosya yok")
        self.filename_label.pack()
        
        self.image_canvas = tk.Canvas(self.root, width=600, height=400)
        self.image_canvas.pack()
        
        self.embed_button = tk.Button(self.root, text="Metini Gizle", command=self.prompt_for_text)
        self.embed_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.extract_button = tk.Button(self.root, text="Şifreyi Çöz", command=self.extract_text)
        self.extract_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.psnr_button = tk.Button(self.root, text="PSNR Hesapla", command=self.calculate_psnr)
        self.psnr_button.pack(side=tk.LEFT, padx=5, pady=5)
        
    def load_file(self):
        self.filename = filedialog.askopenfilename(initialdir="/", title="Select file",
                                                   filetypes=(("jpeg files", "*.jpg"), ("png files", "*.png")))
        if self.filename:
            self.filename_label.config(text=self.filename)
            self.image = Image.open(self.filename)
            self.display_image(self.image)
            
    def display_image(self, img):
        img = img.resize((600, 400), Image.LANCZOS)
        img = ImageTk.PhotoImage(img)
        if self.image_label:
            self.image_canvas.delete(self.image_label)
        self.image_label = self.image_canvas.create_image(0, 0, anchor=tk.NW, image=img)
        self.image_canvas.image = img

    def prompt_for_text(self):
        if not self.filename:
            messagebox.showerror("Hata", "Lütfen bir resim dosyası seçin ")
            return
        text = simpledialog.askstring("Input", "Girilecek metin:")
        if text:
            self.embed_text(text)
    
    def embed_text(self, text):
        shift = 3  # Sezar şifreleme için kaydırma değeri
        encrypted_text = caesar_cipher(text, shift)
        self.stego_image = metin_gomme(self.image, encrypted_text)
        self.display_image(self.stego_image)
        
        save_filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
        if save_filename:
            self.stego_image.save(save_filename)
            messagebox.showinfo("Başarili", f"Gizlenen resim şu isimle kaydedildi : {save_filename}")
    
    def extract_text(self):
        if not self.filename:
            messagebox.showerror("Hata", "Lütfen bir resim seçiniz")
            return
        
        try:
            encrypted_text = extract_text(self.image)
            shift = 3  # Sezar şifreleme için kullanılan kaydırma değeri
            original_text = caesar_decipher(encrypted_text, shift)
            messagebox.showinfo("Şifreyi Çöz", f"Orjinal Metin : {original_text}")
        except Exception as e:
            messagebox.showerror("Hata", f"Bir Hata oluştu : {str(e)}")
        
    def calculate_psnr(self):
        if not hasattr(self, 'stego_image'):
            messagebox.showerror("Hata", "Lütfen önce veriyi gizleyin")
            return
        psnr_value = psnr(self.image, self.stego_image)
        messagebox.showinfo("PSNR Değeri", f"PSNR: {psnr_value} dB")
        

if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()
