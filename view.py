import tkinter as tk 

class OMView():

    def __init__(self, controller, root, app):
        self.app = app
        self.controller = controller
        self.root = root

        self.modeButtonFrame = None
        self.modeButtons = {}

        self.SOInputs = ['Blocks', 'DEM', 'Output Folder']
        self.AOInputs = ['Blocks', 'DEM', 'Output Folder']
        self.histInputs = ['Blocks', 'Overlay','Output Folder']

        self.startPage()

    def startPage(self):
        #Making Buttons-----------------------

        modeButtonFrame = tk.Frame(self.root)
        modeButtonFrame.pack(anchor='n',expand=True, pady=10)
        self.modeButtonFrame = modeButtonFrame

        SOButton = tk.Button(modeButtonFrame, text = "Simple Overlay", command=lambda: self.controller.onSelectModeSO())
        SOButton.pack(padx=10, side=tk.LEFT) 
        self.modeButtons['Simple Overlay'] = SOButton

        AOButton = tk.Button(modeButtonFrame, text = "autoOverlay", command=lambda: self.controller.onSelectModeAO())
        AOButton.pack(padx=10, side=tk.LEFT) 
        self.modeButtons['autoOverlay'] = AOButton

        HButton = tk.Button(modeButtonFrame, text = "Histogram Generation", command=lambda: self.controller.onSelectModeHist())
        HButton.pack(padx=10, side=tk.LEFT) 
        self.modeButtons['Histogram Generation'] = HButton

    def mainWindow(self, inputs = []):

        print("MAIN WINDOW!")
        window = self.app.getRoot()

        childFrames = window.winfo_children()
        for child in childFrames:
            if child == self.modeButtonFrame:
                continue
            else:
                child.destroy()

        #Making frame for interface--------------------------
        main=tk.Frame(window)
        main.pack(anchor='nw', expand=True, fill=tk.BOTH)

        entrBoxes = []

        for widget in main.winfo_children():
            widget.destroy()

        #making a frame
        topLeftFrame = tk.Frame(main)
        topLeftFrame.pack(anchor='nw', padx=20, expand=True, fill=tk.X)

        for inputName in inputs:

            currentInput = Input(self.app, inputName)
            
            # Boundary Input Box Title
            label = tk.Label(topLeftFrame, text=inputName + ":")
            label.pack(padx=0, anchor='nw') 

            # Boundary Input Box
            entry_box = tk.Entry(topLeftFrame)
            entry_box.pack(padx=0, anchor='nw', expand=True, fill=tk.X)
            entrBoxes.append(entry_box)
            currentInput.editInfo('associatedField', entry_box)

            # Choose File Button
            chooseFileButton = tk.Button(topLeftFrame, text="Choose File" + inputName, command=lambda current_entry=entry_box, current_input= currentInput: self.controller.onPressSelectFile(current_entry, current_input))
            chooseFileButton.pack(padx=0, anchor='nw', expand=True, fill=tk.X)  
            currentInput.editInfo('associatedTrigger', chooseFileButton)
            
        # Run Button
        submit_button = tk.Button(main, text="Run", command= lambda: self.controller.on_submit(self.app))
        submit_button.pack(pady=10)

        #Resizing window to fit everything
        window.geometry("")

    def pressButton(self):
        print("PRESSED")

        for key, value in self.modeButtons.items():
            value.config(relief=tk.RAISED)

        if self.app.mode == "SO":
            self.modeButtons['Simple Overlay'].config(relief=tk.SUNKEN)
            self.mainWindow(self.SOInputs)
        elif self.app.mode == "AO":
            self.modeButtons['autoOverlay'].config(relief=tk.SUNKEN)
            self.mainWindow(self.AOInputs)
        elif self.app.mode == "HIST":
            self.modeButtons['Histogram Generation'].config(relief=tk.SUNKEN)
            self.mainWindow(self.histInputs)

        
class Input:
    def __init__(self, app = None, name = '', path = '', field = None, trigger = None):
        self.app = app
        self.info =  {'name': name,
                     'associatedPath':path,
                     'associatedField':field,
                     'associatedTrigger':trigger
                     } 
        
    def getInfo(self):
        return self.info
    
    def editInfo(self, infoToEdit, newInfo):
        self.info[infoToEdit] = newInfo
        self.app.getInputs()[self.info['name']] = self.info

    def updateApp(self):
        self.app.getInputs()[self.info['name']] = self.info
