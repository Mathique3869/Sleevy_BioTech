from pynput import keyboard

count = 0
stopped = False

def on_press(key):
    global count
    count += 1
def on_release(key):
    global stopped
    if key == keyboard.Key.esc and not stopped:
        print("Arrêt de l'écoute du clavier.")
        stopped = True
        return count

# Collect events until released
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()