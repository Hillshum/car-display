import time
import threading
import tkinter as tk


class CarInfo:
  def __init__(self):
    self.get_info()


  def get_info(self):
    self.time = time.ctime()

  def update_loop(self):
    while True:
      self.get_info()
      time.sleep(5)

  
class Display:
  def __init__(self, parent, carInfo):
    self.carInfo = carInfo
    self.time = ''
    self.label = tk.Label(parent, background="gray", text='')
    self.label.pack()
    self.label.after(1000, self.refresh_label)

  def refresh_label(self):
    self.label.configure(text=self.carInfo.time)

    self.label.after(1000, self.refresh_label)



if __name__ == '__main__':
  root = tk.Tk()
  root.geometry("848x480")
  root.configure(background="gray")
  carInfo = CarInfo()
  display = Display(root, carInfo)
  update_thread = threading.Thread(target=carInfo.update_loop, daemon=True)
  update_thread.start()
  root.mainloop()
