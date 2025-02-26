import cv2
import numpy as np
import base64
import os
import threading
import pygame
from cryptography.fernet import Fernet
from tkinter import (
    Tk,
    filedialog,
    Button,
    Label,
    Entry,
    messagebox,
    Canvas,
    Frame,
    ttk,
)
from PIL import Image, ImageTk

# Initialize pygame mixer for sound effects
pygame.mixer.init()
click_sound = pygame.mixer.Sound("click.wav")  # Ensure this file exists


# Function to generate encryption key based on user password
def generate_key(password):
    return base64.urlsafe_b64encode(password.ljust(32).encode()[:32])


# Function to encrypt a message using the generated key
def encrypt_message(message, key):
    cipher = Fernet(key)
    return cipher.encrypt(message.encode())


# Function to decrypt an encrypted message using the key
def decrypt_message(encrypted_message, key):
    cipher = Fernet(key)
    return cipher.decrypt(encrypted_message).decode()


# Function to encode message into an image
def encode_message(image_path, message, password):
    progress_bar["value"] = 10
    threading.Thread(
        target=process_encoding, args=(image_path, message, password)
    ).start()


def process_encoding(image_path, message, password):
    img = cv2.imread(image_path)
    key = generate_key(password)
    encrypted_msg = encrypt_message(message, key)
    binary_msg = "".join(format(byte, "08b") for byte in encrypted_msg)

    if len(binary_msg) > img.size:
        messagebox.showerror("Error", "Message too large for image")
        progress_bar["value"] = 0
        return

    data_index = 0
    for row in img:
        for pixel in row:
            for channel in range(3):
                if data_index < len(binary_msg):
                    pixel[channel] = pixel[channel] & 0xFE | int(binary_msg[data_index])
                    data_index += 1

    cv2.imwrite("encryptedImage.png", img)
    messagebox.showinfo("Success", "Message Hidden Successfully!")
    os.system("start encryptedImage.png")
    progress_bar["value"] = 100


# Function to decode message from an image
def decode_message(image_path, password):
    progress_bar["value"] = 10
    threading.Thread(target=process_decoding, args=(image_path, password)).start()


def process_decoding(image_path, password):
    img = cv2.imread(image_path)
    key = generate_key(password)
    binary_data = ""

    for row in img:
        for pixel in row:
            for channel in range(3):
                binary_data += str(pixel[channel] & 1)

    byte_data = [binary_data[i : i + 8] for i in range(0, len(binary_data), 8)]
    byte_array = bytearray(int(byte, 2) for byte in byte_data)

    try:
        message = decrypt_message(bytes(byte_array), key)
        messagebox.showinfo("Decryption Successful", f"Decrypted Message: {message}")
    except Exception:
        messagebox.showerror(
            "Error", "Decryption failed! Incorrect password or no hidden message."
        )

    progress_bar["value"] = 100


# Function to open file dialog and select an image
def open_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp")]
    )
    if file_path:
        global selected_image
        selected_image = file_path
        img = Image.open(file_path)
        img.thumbnail((300, 300))
        img = ImageTk.PhotoImage(img)
        panel.config(image=img)
        panel.image = img


# Function to toggle encryption and decryption mode
def toggle():
    global is_encryption_mode
    is_encryption_mode = not is_encryption_mode
    click_sound.play()
    if is_encryption_mode:
        toggle_button.config(text="Encryption", bg="#1ABC9C")
        show_panel("Encryption")
    else:
        toggle_button.config(text="Decryption", bg="#E74C3C")
        show_panel("Decryption")


# Function to show selected panel (Encryption or Decryption)
def show_panel(panel_name):
    encryption_frame.pack_forget()
    decryption_frame.pack_forget()
    if panel_name == "Encryption":
        encryption_frame.pack(pady=20)
    else:
        decryption_frame.pack(pady=20)


# Create main application window
root = Tk()
root.title("Cyberpunk Steganography Tool - Developed by Vatsalya Patel")
root.geometry("800x850")
root.configure(bg="#121212")

# Header with application title and developer details
header = Canvas(root, width=800, height=120, bg="#2980B9", highlightthickness=0)
header.pack()
header.create_text(
    400,
    30,
    text="Cyberpunk Image Steganography Tool",
    font=("Arial", 20, "bold"),
    fill="white",
)
header.create_text(
    400, 60, text="Developed by Vatsalya Patel", font=("Arial", 14), fill="white"
)
header.create_text(
    400,
    85,
    text="Email: lnvpatel@gmail.com | Contact: +91 7310442221",
    font=("Arial", 12),
    fill="white",
)

# Toggle button UI
is_encryption_mode = True
toggle_button = Button(
    root,
    text="Encryption",
    command=toggle,
    bg="#1ABC9C",
    fg="white",
    font=("Arial", 14, "bold"),
)
toggle_button.pack(pady=10)

# Image display panel
panel = Label(root, bg="#121212")
panel.pack()

# Encryption panel setup
encryption_frame = Frame(root, bg="#121212")
Button(
    encryption_frame,
    text="Select Image",
    command=open_file,
    bg="#1ABC9C",
    fg="white",
    font=("Arial", 14, "bold"),
).pack(pady=10)
Label(
    encryption_frame,
    text="Enter Secret Message:",
    bg="#121212",
    fg="white",
    font=("Arial", 12),
).pack()
msg_entry = Entry(encryption_frame, width=60)
msg_entry.pack(pady=5)
Label(
    encryption_frame,
    text="Enter Passcode:",
    bg="#121212",
    fg="white",
    font=("Arial", 12),
).pack()
pass_entry = Entry(encryption_frame, width=60, show="*")
pass_entry.pack(pady=5)
Button(
    encryption_frame,
    text="Encrypt & Hide Message",
    command=lambda: encode_message(selected_image, msg_entry.get(), pass_entry.get()),
    bg="#E74C3C",
    fg="white",
    font=("Arial", 14, "bold"),
).pack(pady=15)

# Decryption panel setup
decryption_frame = Frame(root, bg="#121212")
Button(
    decryption_frame,
    text="Select Image",
    command=open_file,
    bg="#1ABC9C",
    fg="white",
    font=("Arial", 14, "bold"),
).pack(pady=10)
Label(
    decryption_frame,
    text="Enter Passcode:",
    bg="#121212",
    fg="white",
    font=("Arial", 12),
).pack()
dec_pass_entry = Entry(decryption_frame, width=60, show="*")
dec_pass_entry.pack(pady=5)
Button(
    decryption_frame,
    text="Decrypt & Show Message",
    command=lambda: decode_message(selected_image, dec_pass_entry.get()),
    bg="#E74C3C",
    fg="white",
    font=("Arial", 14, "bold"),
).pack(pady=15)

# Progress bar setup
progress_bar = ttk.Progressbar(root, length=400, mode="determinate")
progress_bar.pack(pady=10)

show_panel("Encryption")
root.mainloop()
