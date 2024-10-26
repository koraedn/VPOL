import sys
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import re
import os

class VPOLEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("VPOL Editor")
        self.root.geometry("800x600")

        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vpol.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

        self.textArea = ScrolledText(self.root, wrap=tk.WORD, bg="#282c34", fg="#abb2bf", insertbackground="white", font=("Consolas", 12))
        self.textArea.pack(expand=True, fill='both')

        self.menuBar = tk.Menu(self.root)
        self.root.config(menu=self.menuBar)

        self.fileMenu = tk.Menu(self.menuBar, tearoff=0)
        self.menuBar.add_cascade(label="File", menu=self.fileMenu)
        self.fileMenu.add_command(label="New", command=self.newFile)
        self.fileMenu.add_command(label="Open", command=self.openFile)
        self.fileMenu.add_command(label="Save", command=self.saveFile)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Exit", command=self.exitApplication)

        self.currentFile = None
        self.createTags()
        self.textArea.bind("<KeyRelease>", self.highlightSyntax)
        self.textArea.bind("<Return>", self.autoIndent)

        self.root.bind('<Control-n>', lambda event: self.newFile())
        self.root.bind('<Control-s>', lambda event: self.saveFile())

        self.textArea.bind("<<Modified>>", self.on_modified)

    def on_modified(self, event):
        self.textArea.edit_modified(False)

    def createTags(self):
        defaultFont = tkfont.Font(font=self.textArea['font'])
        italicFont = tkfont.Font(font=self.textArea['font'])
        italicFont.configure(slant="italic")

        self.textArea.tag_configure("keyword", foreground="#c678dd")
        self.textArea.tag_configure("variable", foreground="#e06c75")
        self.textArea.tag_configure("string", foreground="#98c379")
        self.textArea.tag_configure("bracket", foreground="#d19a66")
        self.textArea.tag_configure("comment", foreground="#5c6370", font=italicFont)
        self.textArea.tag_configure("ifstmt", foreground="#61afef")
        self.textArea.tag_configure("function", foreground="#56b6c2")
        self.textArea.tag_configure("dollar", foreground="#61afef")
        self.textArea.tag_configure("tilde", foreground="#88c0d0")

        self.is_modified = False

    def newFile(self):
        if self.checkUnsavedChanges():
            self.textArea.delete(1.0, tk.END)
            self.currentFile = None

    def openFile(self):
        if self.checkUnsavedChanges():
            filePath = filedialog.askopenfilename(filetypes=[("VPOL files", "*.vpol")])
            if filePath:
                with open(filePath, 'r') as file:
                    content = file.read()
                    self.textArea.delete(1.0, tk.END)
                    self.textArea.insert(tk.END, content)
                self.currentFile = filePath
                self.highlightSyntax()

    def saveFile(self):
        if self.currentFile:
            content = self.textArea.get(1.0, tk.END)
            with open(self.currentFile, 'w') as file:
                file.write(content)
                self.is_modified = False
        else:
            self.saveFileAs()

    def saveFileAs(self):
        filePath = filedialog.asksaveasfilename(defaultextension=".vpol", filetypes=[("VPOL files", "*.vpol")])
        if filePath:
            content = self.textArea.get(1.0, tk.END)
            with open(filePath, 'w') as file:
                file.write(content)
                self.currentFile = filePath
                self.is_modified = False

    def autoIndent(self, event=None):
        currentLine = int(self.textArea.index("insert").split('.')[0])
        previousLineContent = self.textArea.get(f"{currentLine - 1}.0", f"{currentLine}.0").strip()

        self.textArea.insert(tk.INSERT, "\n")

        if previousLineContent.endswith(":"):
            self.textArea.insert(tk.INSERT, "    ")

        return "break"

    def highlightSyntax(self, event=None):
        self.textArea.tag_remove("keyword", "1.0", tk.END)
        self.textArea.tag_remove("variable", "1.0", tk.END)
        self.textArea.tag_remove("string", "1.0", tk.END)
        self.textArea.tag_remove("bracket", "1.0", tk.END)
        self.textArea.tag_remove("comment", "1.0", tk.END)
        self.textArea.tag_remove("ifstmt", "1.0", tk.END)
        self.textArea.tag_remove("function", "1.0", tk.END)
        self.textArea.tag_remove("dollar", "1.0", tk.END)
        self.textArea.tag_remove("tilde", "1.0", tk.END)

        content = self.textArea.get("1.0", tk.END)

        keywords = ["terminal.print", "cls", "network.ping", "network.http_check", "network.send_packet", "json.parse"]
        for keyword in keywords:
            startIndex = "1.0"
            while True:
                startIndex = self.textArea.search(keyword, startIndex, stopindex=tk.END)
                if not startIndex:
                    break
                endIndex = f"{startIndex}+{len(keyword)}c"
                self.textArea.tag_add("keyword", startIndex, endIndex)
                startIndex = endIndex

        functionPattern = r'def\s+(\w+)\s*:'  
        for match in re.finditer(functionPattern, content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.textArea.tag_add("function", start, end)

        for match in re.finditer(r'@\w+', content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.textArea.tag_add("variable", start, end)

        for match in re.finditer(r'("[^"]*")', content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.textArea.tag_add("string", start, end)

        for match in re.finditer(r'[\(\)\[\]\{\}]', content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.textArea.tag_add("bracket", start, end)

        for match in re.finditer(r'#.*$', content, re.MULTILINE):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.textArea.tag_add("comment", start, end)

        multilineCommentPattern = r'#\[\[(.*?)\]\]'
        for match in re.finditer(multilineCommentPattern, content, re.DOTALL):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.textArea.tag_add("comment", start, end)

        ifStatementPattern = r'if\s+@\w+\s*=\s*".*?":'
        for match in re.finditer(ifStatementPattern, content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.textArea.tag_add("ifstmt", start, end)

        for match in re.finditer(r'\$', content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.textArea.tag_add("dollar", start, end)

        for match in re.finditer(r'~', content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.textArea.tag_add("tilde", start, end)

    def checkUnsavedChanges(self):
        if self.is_modified:
            response = messagebox.askyesnocancel("Unsaved Changes", "You have unsaved changes. Do you want to save before proceeding?")
            if response is None:
                return False
            elif response:
                self.saveFile()
        return True

    def exitApplication(self):
        if self.checkUnsavedChanges():
            self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    editor = VPOLEditor(root)
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as file:
            content = file.read()
            editor.textArea.insert(tk.END, content)
        editor.currentFile = sys.argv[1]
        editor.highlightSyntax()
    root.mainloop()
