import tkinter as tk
from tkinter import messagebox, filedialog
import os

class OMController:
    def __init__(self, model, view, app):
        self.app = app
        self.model = model
        self.view = view

        self.lastDir = os.path.expanduser('~') 

    def on_submit(self, app):
        #runs desired operation

        if app.mode == 'AO':
            
            blocksPath = app.getInputs()['Blocks']['associatedPath']
            demPath = app.getInputs()['DEM']['associatedPath']
            outputFolder = app.getInputs()['Output Folder']['associatedPath']

            print("\n-------------MODE AutoOverlay-------------")
            print("\nInputs:\n")
            print(f"    Blocks: '{blocksPath}'")
            print(f"    DEM: '{demPath}'")
            print(f"    Output Folder: '{outputFolder}'")

            print("\nRunning...")
            self.model.overlayMaker(blocksPath, demPath, outputFolder, [0])

    def onSelectModeSO(self):
        "Changes screen according to selected mode"
        self.app.mode = "SO"
        self.view.pressButton()
        
    def onSelectModeAO(self):
        "Changes screen according to selected mode:"
        self.app.mode = "AO"
        self.view.pressButton()
            
    def onSelectModeHist(self):
        "Changes screen according to selected mode:"
        self.app.mode = "HIST"
        self.view.pressButton()

    def onPressSelectDirectory(self, entryBox, currentInput):
        print(f"\nSelected Input: '{currentInput.getInfo()['name']}'")
        print(f"Associated Field: {entryBox}")

        # Open the file dialog and get the selected file path
        directory = filedialog.askdirectory(title="Select an output folder")

        if directory:
            entryBox.delete(0, tk.END)
            entryBox.insert(0, directory)

            currentInput.editInfo('associatedPath', directory)
            currentInput.updateApp()
            print(f"Selected Input '{currentInput.getInfo()['name']}' associated path changed to '{currentInput.getInfo()['associatedPath']}'")


    def onPressSelectFile(self, entryBox, currentInput):
        print(f"\nSelected Input: '{currentInput.getInfo()['name']}'")
        print(f"Associated Field: {entryBox}")

        if currentInput.getInfo()['name'] == 'DEM':
            ft = ("TIF files", "*.tif")
        elif currentInput.getInfo()['name'] == 'Blocks':
            ft = ("SHP files", "*.shp")

        # Open the file dialog and get the selected file path
        file_path = filedialog.askopenfilename(
            title=f"Select a file for '{currentInput.getInfo()['name'].lower()}'",
            initialdir=self.lastDir, # Optional: sets the initial directory (e.g., home or C:/)
            
            filetypes=(
                ft,
                ("All files", "*.*")
            ) # Optional: filters file types in the dialog
        )
        
        if file_path:
            entryBox.delete(0, tk.END)
            entryBox.insert(0, file_path)

            currentInput.editInfo('associatedPath', file_path)
            currentInput.updateApp()
            print(f"Selected Input '{currentInput.getInfo()['name']}' associated path changed to '{currentInput.getInfo()['associatedPath']}'")



