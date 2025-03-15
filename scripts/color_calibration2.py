import numpy as np
import os
import cv2
import yaml
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import copy

class ColorRange:
    def __init__(self, name, default_min, default_max):
        self.name = name
        self.min_hsv = list(default_min)
        self.max_hsv = list(default_max)
        self.ranges = []  # Will store multiple ranges for this color

    def add_current_range(self):
        """Add the current min/max HSV values as a range"""
        current_range = {
            'min': self.min_hsv.copy(),
            'max': self.max_hsv.copy()
        }
        self.ranges.append(current_range)
        
    def remove_range(self, index):
        """Remove a range at the specified index"""
        if 0 <= index < len(self.ranges):
            self.ranges.pop(index)
    
    def get_all_ranges(self):
        """Return all ranges as list of (min, max) tuples"""
        return [(r['min'], r['max']) for r in self.ranges]
    
    def to_dict(self):
        """Convert to dictionary for YAML storage"""
        return {'ranges': self.ranges}

class ColorCalibrationUI:
    def __init__(self, frame_path=""):
        self.frame_path = frame_path
        self.original_frame = None
        self.display_frame = None
        self.mask_display = None
        self.hsv_frame = None
        
        # Define default color ranges based on the original code
        self.colors = {
            'yellow': ColorRange('Yellow', (18, 50, 50), (35, 255, 255)),
            'blue': ColorRange('Blue', (100, 50, 50), (130, 255, 255)),
            'orange': ColorRange('Orange', (0, 100, 100), (15, 255, 255))
        }
        
        # Current selected color for calibration
        self.current_color = 'yellow'
        
        # Try to load existing color configurations if they exist
        self.load_existing_color_config()
        
        self.setup_ui()
        
    def load_existing_color_config(self):
        """Try to load existing color ranges from YAML file"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                  "config/params.yaml")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                
                # Check if color configurations exist
                if '/point_to_pixel' in config and 'ros__parameters' in config['/point_to_pixel']:
                    params = config['/point_to_pixel']['ros__parameters']
                    
                    for color in self.colors:
                        color_key = f"{color}_ranges"
                        if color_key in params and 'ranges' in params[color_key]:
                            self.colors[color].ranges = copy.deepcopy(params[color_key]['ranges'])
                            
                            # Set the current min/max to the first range if it exists
                            if len(self.colors[color].ranges) > 0:
                                self.colors[color].min_hsv = self.colors[color].ranges[0]['min']
                                self.colors[color].max_hsv = self.colors[color].ranges[0]['max']
                            
                print("Loaded existing color configurations")
            except Exception as e:
                print(f"Error loading color configuration: {e}")
    
    def setup_ui(self):
        self.root = tk.Tk()
        self.root.title("Color Calibration Tool")
        
        # Create main frames
        left_frame = ttk.Frame(self.root)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right_frame = ttk.Frame(self.root)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Image canvas
        self.canvas = tk.Canvas(left_frame, width=800, height=450)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Preview mask canvas
        mask_frame = ttk.LabelFrame(right_frame, text="Mask Preview")
        mask_frame.pack(fill=tk.X, padx=5, pady=5)
        self.mask_canvas = tk.Canvas(mask_frame, width=300, height=200)
        self.mask_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Color selection radiobuttons
        color_frame = ttk.LabelFrame(right_frame, text="Select Color")
        color_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.color_var = tk.StringVar(value=self.current_color)
        for color in self.colors:
            ttk.Radiobutton(
                color_frame, 
                text=self.colors[color].name,
                value=color,
                variable=self.color_var,
                command=self.on_color_changed
            ).pack(anchor=tk.W, padx=5, pady=2)
        
        # HSV sliders
        slider_frame = ttk.LabelFrame(right_frame, text="HSV Range Adjustment")
        slider_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Min HSV sliders
        min_frame = ttk.LabelFrame(slider_frame, text="Minimum HSV")
        min_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.min_h_var = tk.IntVar(value=self.colors[self.current_color].min_hsv[0])
        self.min_s_var = tk.IntVar(value=self.colors[self.current_color].min_hsv[1])
        self.min_v_var = tk.IntVar(value=self.colors[self.current_color].min_hsv[2])
        
        ttk.Label(min_frame, text="H:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Scale(min_frame, from_=0, to=179, variable=self.min_h_var, command=self.update_mask).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        ttk.Label(min_frame, textvariable=self.min_h_var).grid(row=0, column=2, padx=5, pady=2)
        
        ttk.Label(min_frame, text="S:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Scale(min_frame, from_=0, to=255, variable=self.min_s_var, command=self.update_mask).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
        ttk.Label(min_frame, textvariable=self.min_s_var).grid(row=1, column=2, padx=5, pady=2)
        
        ttk.Label(min_frame, text="V:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Scale(min_frame, from_=0, to=255, variable=self.min_v_var, command=self.update_mask).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)
        ttk.Label(min_frame, textvariable=self.min_v_var).grid(row=2, column=2, padx=5, pady=2)
        
        # Max HSV sliders
        max_frame = ttk.LabelFrame(slider_frame, text="Maximum HSV")
        max_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.max_h_var = tk.IntVar(value=self.colors[self.current_color].max_hsv[0])
        self.max_s_var = tk.IntVar(value=self.colors[self.current_color].max_hsv[1])
        self.max_v_var = tk.IntVar(value=self.colors[self.current_color].max_hsv[2])
        
        ttk.Label(max_frame, text="H:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Scale(max_frame, from_=0, to=179, variable=self.max_h_var, command=self.update_mask).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        ttk.Label(max_frame, textvariable=self.max_h_var).grid(row=0, column=2, padx=5, pady=2)
        
        ttk.Label(max_frame, text="S:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Scale(max_frame, from_=0, to=255, variable=self.max_s_var, command=self.update_mask).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
        ttk.Label(max_frame, textvariable=self.max_s_var).grid(row=1, column=2, padx=5, pady=2)
        
        ttk.Label(max_frame, text="V:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Scale(max_frame, from_=0, to=255, variable=self.max_v_var, command=self.update_mask).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)
        ttk.Label(max_frame, textvariable=self.max_v_var).grid(row=2, column=2, padx=5, pady=2)
        
        # Range management frame
        range_frame = ttk.LabelFrame(right_frame, text="Range Management")
        range_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Range list
        self.range_listbox = tk.Listbox(range_frame, height=5)
        self.range_listbox.pack(fill=tk.X, padx=5, pady=5)
        self.update_range_list()
        
        # Range buttons
        btn_frame = ttk.Frame(range_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Add Current Range", command=self.add_range).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Remove Selected", command=self.remove_range).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Use Selected", command=self.use_selected_range).pack(side=tk.LEFT, padx=2)
        
        # Save button
        control_frame = ttk.Frame(right_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=15)
        
        ttk.Button(control_frame, text="Save Color Configurations", command=self.save_configurations).pack(side=tk.RIGHT, padx=5)
    
    def on_color_changed(self):
        """Handle color selection change"""
        self.current_color = self.color_var.get()
        color_obj = self.colors[self.current_color]
        
        # Update the sliders with the current color's HSV values
        self.min_h_var.set(color_obj.min_hsv[0])
        self.min_s_var.set(color_obj.min_hsv[1])
        self.min_v_var.set(color_obj.min_hsv[2])
        self.max_h_var.set(color_obj.max_hsv[0])
        self.max_s_var.set(color_obj.max_hsv[1])
        self.max_v_var.set(color_obj.max_hsv[2])
        
        # Update the range list
        self.update_range_list()
        
        # Update the display
        self.update_mask()
    
    def add_range(self):
        """Add current HSV range to the list"""
        # Update current values from sliders
        self.colors[self.current_color].min_hsv = [
            self.min_h_var.get(),
            self.min_s_var.get(),
            self.min_v_var.get()
        ]
        self.colors[self.current_color].max_hsv = [
            self.max_h_var.get(),
            self.max_s_var.get(),
            self.max_v_var.get()
        ]
        
        # Add to ranges
        self.colors[self.current_color].add_current_range()
        
        # Update the display
        self.update_range_list()
        self.update_mask()
    
    def remove_range(self):
        """Remove selected range from the list"""
        selected = self.range_listbox.curselection()
        if selected:
            index = selected[0]
            self.colors[self.current_color].remove_range(index)
            self.update_range_list()
            self.update_mask()
    
    def use_selected_range(self):
        """Set sliders to the values from the selected range"""
        selected = self.range_listbox.curselection()
        if selected:
            index = selected[0]
            if index < len(self.colors[self.current_color].ranges):
                range_values = self.colors[self.current_color].ranges[index]
                
                # Update sliders
                self.min_h_var.set(range_values['min'][0])
                self.min_s_var.set(range_values['min'][1])
                self.min_v_var.set(range_values['min'][2])
                self.max_h_var.set(range_values['max'][0])
                self.max_s_var.set(range_values['max'][1])
                self.max_v_var.set(range_values['max'][2])
                
                # Update color object's current range
                self.colors[self.current_color].min_hsv = range_values['min']
                self.colors[self.current_color].max_hsv = range_values['max']
                
                self.update_mask()
    
    def update_range_list(self):
        """Update the range listbox with current ranges"""
        self.range_listbox.delete(0, tk.END)
        for i, range_values in enumerate(self.colors[self.current_color].ranges):
            min_vals = range_values['min']
            max_vals = range_values['max']
            self.range_listbox.insert(tk.END, f"Range {i+1}: H({min_vals[0]}-{max_vals[0]}) S({min_vals[1]}-{max_vals[1]}) V({min_vals[2]}-{max_vals[2]})")
    
    def update_mask(self, *args):
        """Update the color mask based on current HSV values"""
        if self.hsv_frame is None:
            return
        
        # Update current color with values from sliders
        self.colors[self.current_color].min_hsv = [
            self.min_h_var.get(),
            self.min_s_var.get(),
            self.min_v_var.get()
        ]
        self.colors[self.current_color].max_hsv = [
            self.max_h_var.get(),
            self.max_s_var.get(),
            self.max_v_var.get()
        ]
        
        # Create mask for current range
        current_mask = cv2.inRange(
            self.hsv_frame,
            np.array(self.colors[self.current_color].min_hsv),
            np.array(self.colors[self.current_color].max_hsv)
        )
        
        # Create mask for all saved ranges
        all_ranges_mask = np.zeros_like(current_mask)
        for range_values in self.colors[self.current_color].ranges:
            min_hsv = np.array(range_values['min'])
            max_hsv = np.array(range_values['max'])
            range_mask = cv2.inRange(self.hsv_frame, min_hsv, max_hsv)
            all_ranges_mask = cv2.bitwise_or(all_ranges_mask, range_mask)
        
        # Apply mask to original frame for visualization
        masked_frame = cv2.bitwise_and(self.original_frame, self.original_frame, mask=current_mask)
        all_ranges_frame = cv2.bitwise_and(self.original_frame, self.original_frame, mask=all_ranges_mask)
        
        # Combine the two visualizations side by side
        h, w = masked_frame.shape[:2]
        combined_mask = np.zeros((h, w*2, 3), dtype=np.uint8)
        combined_mask[:, :w] = masked_frame
        combined_mask[:, w:] = all_ranges_frame
        
        # Add labels
        cv2.putText(combined_mask, "Current Range", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(combined_mask, "All Saved Ranges", (w+10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Update mask display
        combined_mask_rgb = cv2.cvtColor(combined_mask, cv2.COLOR_BGR2RGB)
        self.mask_display = Image.fromarray(combined_mask_rgb)
        
        # Resize for display while maintaining aspect ratio
        mask_width = self.mask_canvas.winfo_width()
        mask_height = self.mask_canvas.winfo_height()
        
        if mask_width > 1 and mask_height > 1:  # Ensure canvas is initialized
            mask_aspect = w*2 / h
            canvas_aspect = mask_width / mask_height
            
            if mask_aspect > canvas_aspect:
                # Width constrained
                new_width = mask_width
                new_height = int(new_width / mask_aspect)
            else:
                # Height constrained
                new_height = mask_height
                new_width = int(new_height * mask_aspect)
            
            self.mask_display = self.mask_display.resize((new_width, new_height), Image.LANCZOS)
        
        mask_tk = ImageTk.PhotoImage(self.mask_display)
        self.mask_canvas.config(width=mask_tk.width(), height=mask_tk.height())
        self.mask_canvas.create_image(0, 0, anchor=tk.NW, image=mask_tk)
        self.mask_canvas.image = mask_tk  # Keep reference
    
    def save_configurations(self):
        """Save color configurations to YAML file"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                 "config/params.yaml")
        
        # First, try to load existing config to preserve any existing data
        existing_config = {}
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    existing_config = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Error loading existing config: {e}")
        
        # Ensure the necessary structure exists
        if '/point_to_pixel' not in existing_config:
            existing_config['/point_to_pixel'] = {}
        
        if 'ros__parameters' not in existing_config['/point_to_pixel']:
            existing_config['/point_to_pixel']['ros__parameters'] = {}
        
        # Add our color configurations to the parameters
        for color in self.colors:
            color_key = f"{color}_ranges"
            existing_config['/point_to_pixel']['ros__parameters'][color_key] = self.colors[color].to_dict()
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # Save to file
        try:
            with open(config_path, 'w') as f:
                yaml.dump(existing_config, f, default_flow_style=False)
            print(f"Color configurations saved to: {config_path}")
            messagebox.showinfo("Success", "Color configurations saved successfully!")
        except Exception as e:
            print(f"Error saving color configurations: {e}")
            messagebox.showerror("Error", f"Failed to save configurations: {str(e)}")
    
    def load_frame(self):
        """Load the frame from the specified path"""
        try:
            frame = cv2.imread(self.frame_path)
            if frame is None:
                raise ValueError(f"Could not load image from {self.frame_path}")
            
            self.original_frame = frame
            self.hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Convert for display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.display_frame = Image.fromarray(frame_rgb)
            
            # Resize to fit canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:  # Ensure canvas is initialized
                img_width, img_height = self.display_frame.size
                img_aspect = img_width / img_height
                canvas_aspect = canvas_width / canvas_height
                
                if img_aspect > canvas_aspect:
                    # Width constrained
                    new_width = canvas_width
                    new_height = int(new_width / img_aspect)
                else:
                    # Height constrained
                    new_height = canvas_height
                    new_width = int(new_height * img_aspect)
                
                self.display_frame = self.display_frame.resize((new_width, new_height), Image.LANCZOS)
            
            # Display image
            img_tk = ImageTk.PhotoImage(self.display_frame)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
            self.canvas.image = img_tk  # Keep reference
            
            # Set height and width for canvas to match the image size
            self.canvas.config(width=img_tk.width(), height=img_tk.height())
            
            # Initial mask update
            self.update_mask()
            
            print(f"Loaded frame: {self.frame_path}")
            return True
        except Exception as e:
            print(f"Error loading frame: {e}")
            messagebox.showerror("Error", f"Failed to load frame: {str(e)}")
            return False
    
    def run(self):
        """Run the UI application"""
        # Wait for the canvas to be realized so we can get its actual size
        self.root.update_idletasks()
        
        # Load the frame after the UI is fully initialized
        if not self.load_frame():
            self.root.destroy()
            return
        
        self.root.mainloop()

def main():
    # Path to the frozen frame
    frame_path = "/Users/aryalohia/Documents/CMR/lidar_camera_calibration/scripts/1080_test.jpg"
    
    # Initialize and run the UI
    ui = ColorCalibrationUI(frame_path=frame_path)
    ui.run()

if __name__ == "__main__":
    main()