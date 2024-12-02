from __future__ import annotations

import os
import tkinter as tk
import psutil
import winreg

from typing import Callable
from tkinter import ttk
from tkinter.messagebox import showerror, showwarning

     
     
def menu_create(
     root: tk.Tk,
     columns: tuple[str],
     functions: dict[str, Callable]
) -> tk.Menu:
     menu = tk.Menu(root)
     for column in columns:
          menu.add_cascade(label=column, command=functions.get(column))
     return menu
     
     
     
class TaskManagerWindow:
     
     def __init__(self, main_object: Main) -> None:
          self.main = main_object 
          self.task_manager_window()
          
          
     def task_manager_window(self) -> None:
          menu = menu_create(
               root=self.main,
               columns=('Back', 'Kill process'),
               functions={
                    'Back': self.main.back,
                    'Kill process': self.select_task_method
               }
          )
          self.main.config(menu=menu)
          
          process = psutil.process_iter()
          data = [
               (prc.name(), prc.status(), prc.pid) for prc in process
          ]
          
          scroll = ttk.Scrollbar(self.main)
          scroll.pack(side='right', fill='y')
          
          self.main.tree = ttk.Treeview(
               self.main, 
               columns=('name', 'status', 'id'), 
               show='headings',
               yscrollcommand=scroll.set
          )
          self.main.tree.pack(fill='both', expand=1)
          scroll.configure(command=self.main.tree.yview)
          
          self.main.tree.heading('name', text='Name')
          self.main.tree.heading('status', text='Status')
          self.main.tree.heading('id', text='ID')
          
          for d in data:
               self.main.tree.insert('', 'end', values=d)
     
     def select_task_method(self) -> None:
          selection = self.main.tree.selection()
          if not selection:
               return showwarning('Warning', 'You have not selected a column.')

          _, _, pid = self.main.tree.item(selection[0])['values']
          
          self.kill_process(pid)
          self.main.tree.delete(selection)
          
          
     @staticmethod
     def kill_process(pid: int) -> None | str:
          try:
               psutil.Process(pid).kill()
          except Exception as ex:
               return showerror('Windows Error', ex)  
     
     
     
class AutoloadWindow:
     
     def __init__(self, main_object: Main) -> None:
          self.main = main_object
          self.sub = r'Software\Microsoft\Windows\CurrentVersion\Run'
          self.autoload_window()
          
     
     def add(self) -> None:
          return None
     
          
     def delete(self) -> None | str:
          selection = self.main.tree.selection()
          if not selection:
               return showwarning('Warning', 'You have not selected a column.')
          
          name, _ = self.main.tree.item(selection[0])['values']
          try:
               with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.sub, 0, winreg.KEY_SET_VALUE) as registy:
                    winreg.DeleteValue(registy, name)
          except (FileNotFoundError, PermissionError) as ex:
               return showerror('Windows error', ex)
          self.main.tree.delete(selection)
          
          
     def rename(self) -> None | str:
          for widget in self.main.winfo_children():
               if '.!entry' == str(widget):
                    return None
               
          selection = self.main.tree.selection()
          if not selection:
               return showwarning('Warning', 'You have not selected a column.')
          
          def rename_in_winreg() -> None:
               if not self.entry_text.get():
                    return showwarning('Warning', 'You have not entered a new name.')
          
               name, _ = self.main.tree.item(selection[0])['values']
               try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.sub, 0, winreg.KEY_SET_VALUE) as registy:
                         winreg.SetValueEx(registy, name, 0, winreg.REG_SZ, self.entry_text.get())
                         
               except (FileNotFoundError, PermissionError) as ex:
                    return showerror('Windows error', ex)
               return self.main.replace_autoload_window()
          
          def kill_entry_and_button(event) -> None:
               self.entry_text.destroy()
               self.entry_button.destroy()
               
          self.entry_text = tk.Entry(
               self.main,
               fg='black',
               width=45
          )
          self.entry_button = ttk.Button(
               self.main,
               text='Rename',
               command=rename_in_winreg
          )
          self.entry_text.pack(anchor='sw', side='left')
          self.entry_button.pack(anchor='sw', side='left')
          self.entry_text.bind('<Escape>', kill_entry_and_button)
          
          
     def autoload_window(self) -> None | str:
          autostart_apps = []
          try:
               with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.sub) as reg_key:
                    for i in range(winreg.QueryInfoKey(reg_key)[1]):
                         name, value, _ = winreg.EnumValue(reg_key, i)
                         autostart_apps.append((name, value))
                         
          except (FileNotFoundError, PermissionError) as ex:
               return showerror('Windows Error', ex)
          
          menu = menu_create(
               root=self.main,
               columns=('Back', 'Delete key', 'Rename key', 'Add'),
               functions={
                    'Back': self.main.back,
                    'Delete key': self.delete,
                    'Rename key': self.rename,
                    'Add': self.add
               }
          )
          self.main.config(menu=menu)
          
          scroll_y = ttk.Scrollbar(self.main)
          scroll_x = ttk.Scrollbar(self.main, orient='horizontal')
          
          scroll_y.pack(side='right', fill='y')
          scroll_x.pack(side='bottom', fill='x')
          
          self.main.tree = ttk.Treeview(
               self.main, 
               columns=('name', 'value'), 
               show='headings',
               yscrollcommand=scroll_y.set,
               xscrollcommand=scroll_x.set
          )
          self.main.tree.pack(fill='both', expand=1)
          scroll_y.config(command=self.main.tree.yview)
          scroll_x.config(command=self.main.tree.xview)
          
          self.main.tree.heading('name', text='Name')
          self.main.tree.heading('value', text='Value')
          
          for d in autostart_apps:
               self.main.tree.insert('', 'end', values=d)

          

class WinlogonWindow:
     
     def __init__(self, main_object: Main) -> None:
          self.main = main_object
          self.sub = r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon'
          self.winlogon_window()
          
     
     def rename(self) -> None:
          for widget in self.main.winfo_children():
               if '.!entry' == str(widget):
                    return None
               
          selection = self.main.tree.selection()
          if not selection:
               return showwarning('Warning', 'First you need to select a column')

          name, value = self.main.tree.item(selection[0])['values']
          def rename_winlogon_value() -> None:
               if not self.rename_entry.get():
                    return showerror('Error', 'Empty string!')
               
               try:
                    with winreg.OpenKeyEx(winreg.HKEY_LOCAL_MACHINE, self.sub, 0, winreg.KEY_WRITE) as registry:
                         winreg.SetValueEx(registry, name, 0, winreg.REG_SZ, self.rename_entry.get())
               
               except (FileNotFoundError, PermissionError) as ex:
                    return showerror('Windows error', ex)
               return self.main.replace_winlogon_window()
          
          
          def kill_entry_and_button(event) -> None:
               self.rename_entry.destroy()
               self.rename_button.destroy()
               
          self.rename_entry = tk.Entry(
               self.main,
               fg='black',
               width=45
          )
          self.rename_button = ttk.Button(
               self.main,
               text='Rename',
               command=rename_winlogon_value
          )
          self.rename_entry.insert(0, value)
          self.rename_entry.pack(anchor='sw', side='left')
          self.rename_button.pack(anchor='sw', side='left')
          self.rename_entry.bind('<Escape>', kill_entry_and_button)
          
          
     def winlogon_window(self) -> None:
          winlogon_apps = []
          try:
               with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.sub) as registry:
                    for i in range(winreg.QueryInfoKey(registry)[1]):
                         name, value, _ = winreg.EnumValue(registry, i)
                         winlogon_apps.append((name, value))
                         
          except (FileNotFoundError, PermissionError) as ex:
               return showerror('Windows Error', ex)

          menu = menu_create(
               root=self.main,
               columns=('Back', 'Rename key'),
               functions={
                    'Back': self.main.back,
                    'Rename key': self.rename
               }
          )
          self.main.config(menu=menu)
          scroll_y = ttk.Scrollbar(self.main)
          scroll_x = ttk.Scrollbar(self.main, orient='horizontal')
          
          scroll_y.pack(side='right', fill='y')
          scroll_x.pack(side='bottom', fill='x')
          
          self.main.tree = ttk.Treeview(
               self.main,
               columns=('name', 'value'),
               show='headings',
               yscrollcommand=scroll_y.set,
               xscrollcommand=scroll_x.set
          )
          self.main.tree.pack(fill='both', expand=1)
          scroll_y.config(command=self.main.tree.yview)
          scroll_x.config(command=self.main.tree.xview)
          
          self.main.tree.heading('name', text='Name')
          self.main.tree.heading('value', text='Value')
          
          for d in winlogon_apps:
               self.main.tree.insert('', 'end', values=d)
          
          
     
class Main(tk.Tk):
     
     def __init__(self) -> None:
          super().__init__()
          
          self.title('Unlocker')
          self.geometry('600x400')
          self.main_window()
          
          
     def main_window(self) -> None:
          self.label = ttk.Label(
               self,
               text='shayzi3 Ink',
               font=('Times New Roman', 15)
          ).place(anchor='center', x=300, y=120)

          self.button_task = ttk.Button(
               self,
               text='Task Manager',
               padding=15,
               width=20,
               command=self.replace_task_window
          ).place(anchor='center', x=200, y=170)
          
          self.button_autoload = ttk.Button(
               self,
               text='Autoload',
               padding=15,
               width=20,
               command=self.replace_autoload_window
          ).place(anchor='center', x=400, y=170)
          
          self.button_winlogon = ttk.Button(
               self,
               text='Winlogon',
               padding=15,
               width=20,
               command=self.replace_winlogon_window
          ).place(anchor='center', x=300, y=235)
          
          self.button_reboot = ttk.Button(
               self,
               text='Rebot',
               command=self.reboot
          ).pack(side='left', anchor='sw')
          
          self.button_shutdown = ttk.Button(
               self,
               text='Shutdown',
               command=self.shutdown
          ).pack(side='left', anchor='sw')
          
          
          
     def replace_task_window(self) -> None:
          for widget in self.winfo_children():
               widget.destroy()
          TaskManagerWindow(main_object=self)
          
          
     def replace_autoload_window(self) -> None:
          for widget in self.winfo_children():
               widget.destroy()
          AutoloadWindow(main_object=self)
          
          
     def replace_winlogon_window(self) -> None:
          for widget in self.winfo_children():
               widget.destroy()
          WinlogonWindow(main_object=self)
          
          
     def back(self) -> None:
          for widget in self.winfo_children():
               widget.destroy()
          self.main_window()
          
          
     def reboot(self) -> None:
          os.system('shutdown -r -t 00')
     
     
     def shutdown(self) -> None:
          os.system('shutdown -s -t 00')
    
    
if __name__ == '__main__': 
     Main().mainloop()
