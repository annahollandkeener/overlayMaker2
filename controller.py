import tkinter as tk
from tkinter import messagebox, filedialog

class OMController:
    def __init__(self, model, view, app):
        self.app = app
        self.model = model
        self.view = view

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

    def onPressSelectFile(self, entryBox, currentInput):
        print(f"\nSelected Input: '{currentInput.getInfo()['name']}'")
        print(f"Associated Field: {entryBox}")

        # Open the file dialog and get the selected file path
        file_path = filedialog.askopenfilename(
            title="Select a file",
            initialdir="/", # Optional: sets the initial directory (e.g., home or C:/)
            filetypes=(
                ("SHP files", "*.shp"),
                ("All files", "*.*")
            ) # Optional: filters file types in the dialog
        )
        
        if file_path:
            entryBox.delete(0, tk.END)
            entryBox.insert(0, file_path)

            currentInput.editInfo('associatedPath', file_path)
            currentInput.updateApp()
            print(f"Selected Input '{currentInput.getInfo()['name']}' associated path changed to '{currentInput.getInfo()['associatedPath']}'")



