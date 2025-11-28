import tkinter as tk
from tkinter import filedialog, Listbox, END, messagebox
import os

try:
    # from moviepy import VideoFileClip, concatenate_videoclips , CompositeVideoClip , ColorClip 
    from moviepy import *
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

        # --- Transition Options ---
        self.frame_options = tk.Frame(self)
        self.frame_options.pack(pady=5)

        self.var_transitions = tk.BooleanVar(value=False)
        self.chk_transitions = tk.Checkbutton(self.frame_options, text="Enable Crossfade Transitions", variable=self.var_transitions)
        self.chk_transitions.pack(side=tk.LEFT, padx=5)

        tk.Label(self.frame_options, text="Duration (s):").pack(side=tk.LEFT, padx=5)
        self.var_duration = tk.DoubleVar(value=1.0)
        self.spin_duration = tk.Spinbox(self.frame_options, from_=0.1, to=5.0, increment=0.1, textvariable=self.var_duration, width=5)
        self.spin_duration.pack(side=tk.LEFT)

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
            
            if not clips:
                return

            # Determine target resolution (max width/height)
            max_width = max(clip.w for clip in clips)
            max_height = max(clip.h for clip in clips)
            target_size = (max_width, max_height)

            # Resize clips to target size
            resized_clips = []
            for clip in clips:
                if clip.w != max_width or clip.h != max_height:
                    # Resize while maintaining aspect ratio and padding
                    # This is a simplified resize, for professional results we might want more complex logic
                    # But for speed/simplicity, we'll just resize to fit or fill.
                    # Let's use a safe approach: resize to fit within box, then pad.
                    
                    # Calculate scaling factor
                    scale_factor = min(max_width / clip.w, max_height / clip.h)
                    new_w = int(clip.w * scale_factor)
                    new_h = int(clip.h * scale_factor)
                    
                    # Resize
                    clip_resized = clip.resized(new_size=(new_w, new_h))
                    
                    # Pad if necessary
                    if new_w < max_width or new_h < max_height:
                        clip_final = CompositeVideoClip([
                            ColorClip(size=target_size, color=(0,0,0), duration=clip.duration),
                            clip_resized.with_position("center")
                        ], size=target_size)
                    else:
                        clip_final = clip_resized
                    
                    resized_clips.append(clip_final)
                else:
                    resized_clips.append(clip)
            
            clips = resized_clips # Update clips list with resized versions

            if self.var_transitions.get() and len(clips) > 1:
                # Apply Crossfade Transitions
                transition_duration = self.var_duration.get()
                
                # We need to overlap clips. 
                # Clip 1 plays, then Clip 2 starts 'transition_duration' before Clip 1 ends.
                
                final_clips = []
                # The first clip is just itself, but we need to handle the start time for subsequent clips
                
                # Using CompositeVideoClip for transitions is more flexible but can be memory intensive.
                # A more standard way in moviepy for simple crossfade is `concatenate_videoclips(..., method="compose", padding=-duration)` 
                # but explicit crossfadein/out is often smoother.
                
                # Let's use the list of clips with crossfadein applied to all but the first
                clips_with_transition = [clips[0]]
                for i in range(1, len(clips)):
                    # Apply crossfade in to the current clip
                    # And overlap it with the previous one
                    clip = clips[i].with_effects([vfx.CrossFadeIn(transition_duration)])
                    clips_with_transition.append(clip)
                
                # Concatenate with padding (negative padding creates overlap)
                final_clip = concatenate_videoclips(clips_with_transition, method="compose", padding=-transition_duration)
                
            else:
                # Simple Concatenation
                final_clip = concatenate_videoclips(clips, method="compose")

            # Write output with optimization
            # preset='ultrafast' significantly speeds up encoding
            # threads=4 ensures multi-core usage
            final_clip.write_videofile(
                output_path, 
                codec='libx264', 
                audio_codec='aac', 
                preset='ultrafast', 
                threads=4,
                fps=24 # Enforce a standard fps if not set, or use clips[0].fps
            )
            
            for clip in clips:
                try:
                    clip.close()
                except:
                    pass

            messagebox.showinfo("Success", f"Videos combined successfully and saved to:\n{output_path}")
            print("Done.")

        except Exception as e:
            import traceback
            traceback.print_exc()
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
