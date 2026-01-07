import tkinter as tk
from tkinter import messagebox, filedialog

class Handler:
    def __init__(self, boxToFill = tk.Entry, result = ''):
        self.boxToFill = boxToFill
        self.result = result

    
    def select_file(self):
        # Create a hidden root window
        root = tk.Tk()
        root.withdraw()

        # Open the file dialog and get the selected file path
        file_path = filedialog.askopenfilename(
            title="Select a file",
            initialdir="/", # Optional: sets the initial directory (e.g., home or C:/)
            filetypes=(
                ("SHP files", "*.shp"),
                ("All files", "*.*")
            ) # Optional: filters file types in the dialog
        )
        
        # Destroy the hidden root window after selection
        root.destroy()

        if file_path:

            self.result = file_path
            print(f"self.result: {self.result}")

            self.boxToFill.insert(0, self.result)

            return self.result
        else:
            print("No file selected.")


    
    def makeFileHolderButton(self, position, text):
        button = tk.Button(position, text=text, command=self.select_file)
        button.pack(padx=0, anchor='nw', expand=True, fill=tk.X)

        







#----------INTERFACE FUNCTIONS-------------

def on_submit():
    #runs desired operation
    print("Running...")
    

def onSelectModeSO():
    "Changes screen according to selected mode"
    for button in modeButtons:
        button.config(relief=tk.RAISED)

    SOButton.config(relief=tk.SUNKEN)
    inputDisplay(SOInputs)

def onSelectModeAO():
    "Changes screen according to selected mode:"
    for button in modeButtons:
        button.config(relief=tk.RAISED)
        
    AOButton.config(relief=tk.SUNKEN)
    inputDisplay(AOInputs)

def onSelectModeHist():
    "Changes screen according to selected mode:"
    for button in modeButtons:
        button.config(relief=tk.RAISED)
        
    HButton.config(relief=tk.SUNKEN)
    inputDisplay(histInputs)



#---------------LAYOUT--------------------------------
SOInputs = ['Blocks', 'DEM', 'Output Folder']
AOInputs = ['Blocks', 'DEM', 'Another Option','Output Folder']
histInputs = ['Blocks', 'Overlay','Output Folder']

modeButtons = []

# Main Window
window = tk.Tk()
window.title("KBE autoOverlay Tool")
window.geometry("500x350") # Set the window size

#Making Buttons-----------------------
modeButtonFrame = tk.Frame(window)
modeButtonFrame.pack(anchor='n',expand=True, pady=10)

SOButton = tk.Button(modeButtonFrame, text = "Simple Overlay", command=onSelectModeSO)
SOButton.pack(padx=10, side=tk.LEFT) 
modeButtons.append(SOButton)

AOButton = tk.Button(modeButtonFrame, text = "autoOverlay", command=onSelectModeAO)
AOButton.pack(padx=10, side=tk.LEFT) 
modeButtons.append(AOButton)

HButton = tk.Button(modeButtonFrame, text = "Histogram Generation", command=onSelectModeAO)
HButton.pack(padx=10, side=tk.LEFT) 
modeButtons.append(HButton)



#Making frame for interface--------------------------
main=tk.Frame(window)
main.pack(anchor='nw', expand=True, fill=tk.BOTH)


def inputDisplay(titles = []):

    for widget in main.winfo_children():
        widget.destroy()

    for input in titles:
        #making a frame
        topLeftFrame = tk.Frame(main)
        topLeftFrame.pack(anchor='nw', padx=20, expand=True, fill=tk.X)

        # Boundary Input Box Title
        label = tk.Label(topLeftFrame, text=input + ":")
        label.pack(padx=0, anchor='nw') 

        # Boundary Input Box
        entry_box = tk.Entry(topLeftFrame)
        entry_box.pack(padx=0, anchor='nw', expand=True, fill=tk.X)

        # Choose File Button

        fileSelector = Handler(entry_box)
        fileSelector.makeFileHolderButton(topLeftFrame, "Choose a file")


    # Run Button
    submit_button = tk.Button(main, text="Run", command=on_submit)
    submit_button.pack(pady=10)

    #Resizing window to fit everything
    window.geometry("")


#--------------EXECUTING----------------------------

# 5. Run the main event loop
window.mainloop()

