import tkinter as tk 
from PIL import ImageTk, Image
import os

class OMView():

    def __init__(self, controller, root, app):
        self.app = app
        self.controller = controller
        self.root = root

        self.modeButtons = {}
        self.framesToPreserve = []

        self.SOInputs = ['Blocks', 'DEM', 'Output Folder']
        self.AOInputs = ['Blocks', 'DEM', 'Output Folder']
        self.histInputs = ['Blocks', 'Overlay','Output Folder']

        self.startPage()

    def startPage(self):
        #Making Start Page-----------------------

        titleFrame = tk.Frame(self.root, bg = '#39979e')
        titleFrame.pack(side=tk.TOP, anchor='center',expand=True, fill='x', pady=5)
        self.framesToPreserve.append(titleFrame)

        imageFrame = tk.Frame(titleFrame, bg='#39979e')
        imageFrame.pack(anchor='center')
        self.framesToPreserve.append(imageFrame)

        KBELogoPath = "C:/wfh/python/overlayMaker2/overlayMaker2/assets/KBE_Logo_crop.jpg"
        original_image = Image.open(KBELogoPath)
        resized_image = original_image.resize((110, 50), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(resized_image)
        image_label = tk.Label(imageFrame, image=photo)
        image_label.pack(side=tk.LEFT,padx=5, pady=15)
        image_label.image = photo
        
        title = tk.Label(imageFrame, text='Overlay Maker', font=("Helvetica", 15, "bold"), bg = '#39979e', fg = '#1f1f1f')
        title.pack(side=tk.LEFT, padx=5, pady=15)

        instruction = tk.Label(self.root, text='Select a mode:', font=("Helvetica", 12, "bold"), fg = '#707070')
        instruction.pack(anchor='center', padx=5, pady=10)

        modeButtonFrame = tk.Frame(self.root)
        modeButtonFrame.pack(anchor='n',expand=True, pady=15, padx=10)
        self.framesToPreserve.append(modeButtonFrame)

        SOButton = tk.Button(modeButtonFrame, text = "Flat Overlay", font=("bold"), bg= '#ffffff', command=lambda: self.controller.onSelectModeSO())
        SOButton.pack(padx=10, side=tk.LEFT) 
        self.modeButtons['Flat Overlay'] = SOButton

        AOButton = tk.Button(modeButtonFrame, text = "autoOverlay", font=("bold"), bg= '#ffffff', command=lambda: self.controller.onSelectModeAO())
        AOButton.pack(padx=10, side=tk.LEFT) 
        self.modeButtons['autoOverlay'] = AOButton

        HButton = tk.Button(modeButtonFrame, text = "Histogram Generation", font=("bold"), bg= '#ffffff', command=lambda: self.controller.onSelectModeHist())
        HButton.pack(padx=10, side=tk.LEFT) 
        self.modeButtons['Histogram Generation'] = HButton

        pocosinPath = "C:/wfh/python/overlayMaker2/overlayMaker2/assets/pocosin.jpg"
        original_image_pocosin = Image.open(pocosinPath)
        resized_image_pocosin = original_image_pocosin.resize((599, 181), Image.Resampling.LANCZOS)
        pocosinPhoto = ImageTk.PhotoImage(resized_image_pocosin)
        image_label_pocosin = tk.Label(self.root, image=pocosinPhoto)
        image_label_pocosin.pack(side=tk.TOP, fill='x')
        image_label_pocosin.image = pocosinPhoto

        self.root.geometry("")
        

    def mainWindow(self, inputs = []):

        window = self.app.getRoot()

        childFrames = window.winfo_children()
        for child in childFrames:
            if child in self.framesToPreserve:
                continue
            else:
                child.destroy()

        #Making frame for interface--------------------------
        '''
        if self.app.mode == 'AO':
            desc = """
            Creates several overlay options for the extent of specified
            blocks based on domed water tables created for each block. 
            Will estimate existing water level if not specified. 
            """
        descriptionFrame = tk.Label(window, text=desc, justify='left')
        descriptionFrame.pack(anchor='center', expand=True, fill=tk.BOTH, padx=50)
        '''

        main=tk.Frame(window)
        main.pack(anchor='nw', expand=True, fill=tk.BOTH)

        entrBoxes = []


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
            if inputName == 'Output Folder':
                chooseFileButton = tk.Button(topLeftFrame, text="Choose Folder", command=lambda current_entry=entry_box, current_input= currentInput: self.controller.onPressSelectDirectory(current_entry, current_input))
                chooseFileButton.pack(padx=0, anchor='nw', expand=True, fill=tk.X)  
                currentInput.editInfo('associatedTrigger', chooseFileButton)
            else:
                chooseFileButton = tk.Button(topLeftFrame, text="Choose File", command=lambda current_entry=entry_box, current_input= currentInput: self.controller.onPressSelectFile(current_entry, current_input))
                chooseFileButton.pack(padx=0, anchor='nw', expand=True, fill=tk.X)  
                currentInput.editInfo('associatedTrigger', chooseFileButton)
                
        # Run Button
        submit_button = tk.Button(main, text="Run", command= lambda: self.controller.on_submit(self.app))
        submit_button.pack(pady=10)

        #Resizing window to fit everything
        window.geometry("")

    def pressButton(self):

        for key, value in self.modeButtons.items():
            value.config(relief=tk.RAISED)

        if self.app.mode == "SO":
            self.modeButtons['Flat Overlay'].config(relief=tk.SUNKEN)
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
