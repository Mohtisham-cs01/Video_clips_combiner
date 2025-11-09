import tkinter as tk
from tkinter import filedialog, Listbox, END, messagebox
import os

try:
    from moviepy import VideoFileClip, concatenate_videoclips
except ImportError:
    messagebox.showerror("Error", "MoviePy is not installed. Please install it using: pip install moviepy")
    exit()

class DraggableListbox(Listbox):
    """ A listbox with drag and drop reordering of items. """
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.bind('<Button-1>', self.on_start)
        self.bind('<B1-Motion>', self.on_drag)
        self.bind('<ButtonRelease-1>', self.on_drop)
        self.selection_index = None

    def on_start(self, event):
        self.selection_index = self.nearest(event.y)

    def on_drag(self, event):
        if self.selection_index is None:
            return
        i = self.nearest(event.y)
        if i != self.selection_index:
            self.move_item(self.selection_index, i)
            self.selection_index = i

    def on_drop(self, event):
        self.selection_index = None

    def move_item(self, from_index, to_index):
        item = self.get(from_index)
        self.delete(from_index)
        self.insert(to_index, item)
        
        # Also move the corresponding path in the parent's clip_paths list
        self.master.clip_paths.insert(to_index, self.master.clip_paths.pop(from_index))


class VideoCombiner(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Video Combiner")
        self.geometry("600x400")

        self.clip_paths = []

        # --- UI Elements ---
        self.btn_add = tk.Button(self, text="Add Clips", command=self.add_clips)
        self.btn_add.pack(pady=10)

        self.btn_remove = tk.Button(self, text="Remove Selected", command=self.remove_selected_clips)
        self.btn_remove.pack(pady=5)

        self.listbox = DraggableListbox(self, selectmode=tk.EXTENDED)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.btn_combine = tk.Button(self, text="Combine Videos", command=self.combine_videos)
        self.btn_combine.pack(pady=10)

    def add_clips(self):
        files = filedialog.askopenfilenames(
            title="Select Video Clips",
            filetypes=(("Video files", "*.mp4 *.avi *.mov"), ("All files", "*.*"))
        )
        if files:
            # Sort files by title
            sorted_files = sorted(list(files), key=lambda f: os.path.basename(f))
            
            for file in sorted_files:
                self.clip_paths.append(file)
                self.listbox.insert(END, os.path.basename(file))

    def combine_videos(self):
        if not self.clip_paths:
            messagebox.showwarning("No clips", "Please add video clips to combine.")
            return

        output_path = filedialog.asksaveasfilename(
            title="Save Combined Video As...",
            defaultextension=".mp4",
            filetypes=(("MP4 files", "*.mp4"), ("All files", "*.*"))
        )

        if not output_path:
            return

        try:
            print("Combining videos...")
            clips = [VideoFileClip(path) for path in self.clip_paths]
            final_clip = concatenate_videoclips(clips, method="compose")
            final_clip.write_videofile(output_path)
            
            for clip in clips:
                clip.close()

            messagebox.showinfo("Success", f"Videos combined successfully and saved to:\n{output_path}")
            print("Done.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during video combination:\n{e}")

    def remove_selected_clips(self):
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("No selection", "Please select clips to remove.")
            return

        # Remove from listbox and clip_paths in reverse order to avoid index issues
        for index in sorted(selected_indices, reverse=True):
            self.listbox.delete(index)
            del self.clip_paths[index]

    def on_closing(self):
        self.destroy()

if __name__ == "__main__":
    app = VideoCombiner()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()