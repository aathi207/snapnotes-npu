import sys
import threading
import numpy as np
import sounddevice as sd
import customtkinter as ctk

# Set dark theme styling for the application window
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SnapNotesApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("SnapNotes - On-Device AI Meeting Assistant")
        self.geometry("900x650")
        
        self.is_recording = False
        self.audio_data = []
        self.sample_rate = 16000 # Standard processing frequency for AI audio models
        
        self.setup_ui()
        
    def setup_ui(self):
        # Application Header Banner
        self.header_label = ctk.CTkLabel(
            self, 
            text="SnapNotes AI Assistant", 
            font=ctk.CTkFont(size=26, weight="bold")
        )
        self.header_label.pack(pady=15)
        
        self.subtitle_label = ctk.CTkLabel(
            self, 
            text="Hardware Accelerated via Snapdragon Hexagon NPU", 
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="#888888"
        )
        self.subtitle_label.pack(pady=2)

        # Control Panel Button Area
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.pack(fill="x", padx=30, pady=15)
        
        self.record_btn = ctk.CTkButton(
            self.control_frame, 
            text="Start Recording Meeting", 
            fg_color="#228B22", 
            hover_color="#006400",
            command=self.toggle_recording,
            font=ctk.CTkFont(weight="bold")
        )
        self.record_btn.pack(side="left", padx=15, pady=15, expand=True, fill="x")
        
        # Split Data Visualizer Workspace Layout
        self.workspace_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.workspace_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Left Side Pane: Real-time Transcript Window
        self.left_frame = ctk.CTkFrame(self.workspace_frame)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(self.left_frame, text="Live Raw Transcript", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.transcript_box = ctk.CTkTextbox(self.left_frame, activate_scrollbars=True)
        self.transcript_box.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Right Side Pane: Extracted Action Items Window
        self.right_frame = ctk.CTkFrame(self.workspace_frame)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        ctk.CTkLabel(self.right_frame, text="AI Summaries & Action Items", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.summary_box = ctk.CTkTextbox(self.right_frame, activate_scrollbars=True)
        self.summary_box.pack(fill="both", expand=True, padx=10, pady=10)

    def toggle_recording(self):
        if not self.is_recording:
            # Transition application state to active recording mode
            self.is_recording = True
            self.audio_data = []
            self.record_btn.configure(text="Stop & Process Summary", fg_color="#B22222", hover_color="#8B0000")
            self.transcript_box.delete("1.0", "end")
            self.summary_box.delete("1.0", "end")
            self.transcript_box.insert("end", "[Listening... Microphones active and recording locally.]\n")
            
            # Start background safe recording thread loop
            self.record_thread = threading.Thread(target=self.audio_stream_loop)
            self.record_thread.start()
        else:
            # Terminate audio record capturing state
            self.is_recording = False
            self.record_btn.configure(text="Processing NPU Inference...", state="disabled", fg_color="#D2691E")
            
    def audio_stream_loop(self):
        def callback(indata, frames, time, status):
            if self.is_recording:
                self.audio_data.append(indata.copy())
                
        with sd.InputStream(samplerate=self.sample_rate, channels=1, callbac
