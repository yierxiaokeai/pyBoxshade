import sys
from itertools import chain
from platform import system

import numpy as np
from PyQt5.QtCore import QFileInfo, QPoint, QSize, Qt, QDir
from PyQt5.QtGui import QIcon, QKeySequence, QFont, QColor, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow, QMessageBox, QTextEdit,
                             QStyleFactory, QWidget)

import BS_config as BS
from OutDevs import RTFdev, PSdev, ASCIIdev, Paintdev, ImageDisp
from mydialog import prefsDialog
from pyboxshade.alignment import read_alignment
from pyboxshade.resources import resource_path
from pyboxshade.settings import new_settings as QSettings

# some global varibles and strings

file_filter = ("All files (*);;FASTA files (*.fas*);;Clustal files (*.aln);;Phylip files (*.phy);;GCG/MSF files (*.msf)\
                                                      ;;Nexus files (*.nexus);;Stockholm files (*.st*)")
aaset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
lenaa = len(aaset)
aasetlow = 'abcdefghijklmnopqrstuvwxyz'
chars = aaset+aasetlow
gapchars = '-.~'

aa_dict = dict(zip(list(aaset), range(lenaa)))
aalow_dict = dict(zip(list(aasetlow), range(len(aasetlow))))

simtable = np.full((lenaa,lenaa), False, dtype=bool)
for i in range(lenaa):
    simtable[i,i]= True
grptable = np.copy(simtable)

def sim(a, b):
    p1 = aa_dict.get(a)
    p2 = aa_dict.get(b)
    if p1 is not None and p2 is not None:
        return simtable[p1, p2]
    else:
        return False

def grp(a, b):
    p1 = aa_dict.get(a)
    p2 = aa_dict.get(b)
    if p1 is not None and p2 is not None:
        return grptable[p1, p2]
    else:
        return False

def readsims():
    global simtable
    global grptable
    settings = QSettings("Boxshade", "Boxshade")
    if settings.value("pepseqsflag", type=bool):
        simsline = settings.value("simsline", 'SIMS:F YW:Y FW:W FY:I LM:L IM:M IL:R KH:K RH:H KR:A G:S T:D EN:E DQ:N EQ:P G:V M:END')
        grpsline = settings.value("grpsline", 'GRPS:FYW:ILVM:DE:GA:ST:NQ:RKH:END')
    else:
        simsline = settings.value("DNAsimsline")
        grpsline = settings.value("DNAgrpsline")
    simsline = simsline.split(":")
    grpsline = grpsline.split(":")
    simtable = np.full((lenaa, lenaa), False, dtype=bool)
    for i in range(lenaa):
        simtable[i, i] = True
    grptable = np.copy(simtable)
    for i in range(1,len(simsline)-1):
        p1 = aa_dict.get(simsline[i][0])
        if p1 is not None:
            for j in range (2,len(simsline[i])):
                p2 = aa_dict.get(simsline[i][j])
                if p2 is not None:
                    simtable[p1,p2] = True
                    simtable[p2,p1] = True

    for k in range(1,len(grpsline)-1):
        for j in range(0, len(grpsline[k])-1):
            p1 = aa_dict.get(grpsline[k][j])
            if p1 is not None:
                for i in range (j+1, len(grpsline[k])):
                    p2 = aa_dict.get(grpsline[k][i])
                    if p2 is not None:
                        grptable[p1, p2] = True
                        grptable[p2, p1] = True
    return

def set_defaults():# To be called the first time the program is run, if there are no Preferences

    settings = QSettings("Boxshade", "Boxshade")
    settings.setFallbacksEnabled(False)
#    if settings.contains("ASCIIchars"):
#        return
    keys = settings.allKeys()
    if not "simsline" in keys:
        settings.setValue("simsline", 'SIMS:F YW:Y FW:W FY:I LM:L IM:M IL:R KH:K RH:H KR:A G:S T:D EN:E DQ:N EQ:P G:V M:END')
    if not "grpsline" in keys:
        settings.setValue("grpsline", 'GRPS:FYW:ILVM:DE:GA:ST:NQ:RKH:END')
    if not "DNAsimsline" in keys:
        settings.setValue("DNAsimsline", 'SIMS:A GR:G AR:C TY:T CY:R AG:Y CT:END')
    if not "DNAgrpsline" in keys:
        settings.setValue("DNAgrpsline", 'GRPS:AGR:CTY:END')
    if not "thrfrac" in keys:
        settings.setValue("thrfrac", 0.7)
    if not "scflag" in keys:
        settings.setValue("scflag", False)
    if not "countGaps" in keys:
        settings.setValue("countGaps", True)
    if not "snameflag" in keys:
        settings.setValue("snameflag", True)
    if not "RHsnumsflag" in keys:
        settings.setValue("RHsnumsflag", False)
    if not "LHsnumsflag" in keys:
        settings.setValue("LHsnumsflag", False)
    if not "defnumsflag" in keys:
        settings.setValue("defnumsflag", False)
    if not "simflag" in keys:
        settings.setValue("simflag", True)
    if not "globalflag" in keys:
        settings.setValue("globalflag", True)
    if not "consflag" in keys:
        settings.setValue("consflag", False)
    if not "outlen" in keys:
        settings.setValue("outlen", 60)
    if not "interlines" in keys:
        settings.setValue("interlines", 1)
    if not "symbcons" in keys:
        settings.setValue("symbcons", ' LU')
    if not "consline" in keys:
        settings.setValue("consline", 1)
    if not "rulerflag" in keys:
        settings.setValue("rulerflag", False)
    if not "pepseqsflag" in keys:
        settings.setValue("pepseqsflag", True)
    if not "PSfgds" in keys:
        settings.setValue("PSfgds", [QColor(0, 0, 0), QColor(255, 255, 255), QColor(0, 0, 0), QColor(255, 255, 255)])
    if not "PSbgds" in keys:
        settings.setValue("PSbgds", [QColor(255, 255, 255), QColor(0, 0, 0), QColor(180, 180, 180), QColor(0, 0, 0)])
    if not "PSFsize" in keys:
        settings.setValue("PSFsize", 12)
    if not "PSLCs" in keys:
        settings.setValue("PSLCs", [False, False, False, False])
    if not "PSlandscapeflag" in keys:
        settings.setValue("PSlandscapeflag", False)
    if not "ASCIIchars" in keys:
        settings.setValue("ASCIIchars", ['L', '.', 'l', '*'])
    if not "pos" in keys:
        settings.setValue("pos", QPoint(200, 200))
    if not "size" in keys:
        settings.setValue("size", QSize(400, 400))
    settings.sync()
    return


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        QApplication.setStyle(QStyleFactory.create("Fusion"))
        QApplication.setPalette(QApplication.style().standardPalette())

        BS.ssfont = QFont("")
        BS.ssfont.setStyleHint(QFont.SansSerif)
        BS.ssfont.setStyleStrategy(QFont.PreferOutline)
        BS.ssfont.setFamily("Arial")
        BS.ssfont.setPointSize(32)
        self.setAcceptDrops(True)
        self.textEdit = QTextEdit()
        self.textEdit.setPlaceholderText("Open a sequence file or drop one here")
        self.textEdit.setFont(BS.ssfont)
        self.textEdit.setReadOnly(True)
        self.setCentralWidget(self.textEdit)

        BS.monofont = QFont("")
        BS.monofont.setStyleHint(QFont.Monospace)
        BS.monofont.setStyleStrategy(QFont.PreferOutline)
        if system() == "Darwin":
            BS.monofont.setFamily("Courier")
        else:
            BS.monofont.setFamily("Courier New")

        self.curFile = ''
        self.al = []
        self.seqs = np.array([[' ', ' '], [' ', ' ']], dtype=str)
        self.cons = np.array([' ',' ',' '], dtype=str)
        self.conschar = np.copy(self.cons)
        self.cols = np.copy(self.seqs)
        self.seqlens = np.array([0,0,0])
        self.startnums = np.copy(self.seqlens)
        self.no_seqs = 0
        self.maxseqlen = 0
        self.consenslen = 0
        self.consensnum = 1 # the sequence that acts as consensus if scflag=True
        self.seqnames =[] # will become a list of sequence names

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.readSettings()

        self.setCurrentFile('')
        BS.lastdir = QDir.homePath()
        self.viewList = []
        readsims()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            self.textEdit.setStyleSheet("background-color : #b3e2ff ;")
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            fileName = urls[0].toLocalFile() # only take the first file dropped if more than one file
            self.loadFile(fileName)
            BS.lastdir = QFileInfo(fileName).absolutePath()
            self.textEdit.setStyleSheet("background-color : #ffffff ;")
            event.accept()
        else:
            event.ignore()


    def dragLeaveEvent(self, event):
            self.textEdit.setStyleSheet("background-color : #ffffff ;")
            event.accept()

    def closeEvent(self, event):
        self.writeSettings()
        vL=self.viewList.copy()
        for id in vL: # close any remaining PNG windows
            id.close()
        event.accept()

    def do_prefs(self):
        Preferences = prefsDialog(self.no_seqs, self.consensnum, parent=self)
        Preferences.GenTab.startnums = self.startnums
        Preferences.GenTab.filltable() # I have made the preferences startnums array a view onto the one here
                                        # and use it to fill the table
        if 1 == Preferences.exec():
            self.consensnum = Preferences.GenTab.consensnum
            readsims()
            if Preferences.proc_flag:
                self.process_seqs()

    def about(self):
        ab = QMessageBox(self)
#        super(QMessageBox, ab).setWindowTitle("About this program")
        ab.setTextFormat(Qt.RichText)
        ab.setText("<p style='font-size: 18pt'>About pyBoxshade</p>"
                   "<p style='font-size: 14pt; font-weight: normal'> <b>pyBoxshade</b> allows the creation of nice pictures of "
                "protein or DNA alignments with residues coloured and shaded "
                "according to the level of sequence conservation </p>")

        ab.setIconPixmap(QPixmap(resource_path('image2.png')).scaled(80,80))

        ab.exec()

    def createActions(self):
        self.openAct = QAction(QIcon(resource_path('open.png')), "&Open...",
                        self, shortcut=QKeySequence.Open, statusTip="Open an existing file", triggered=self.open)
        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                statusTip="Exit the application", triggered=self.close)
        self.doPrefsAct = QAction(QIcon(resource_path('prefs.png')), "Settings", self,
                statusTip="Open dialog to allow control of program settings",
                triggered=self.do_prefs)
        self.RTFAct = QAction(QIcon(resource_path('rtf.png')), "Make RTF", self,
                statusTip="Make RTF file", triggered=self.RTF_out)
        self.PSAct = QAction(QIcon(resource_path('ps-file.png')), "Make PS", self,
                              statusTip="Make PS file", triggered=self.PS_out)
        self.AscAct = QAction(QIcon(resource_path('txt.png')), "Make Text", self,
                             statusTip="Make text file", triggered=self.ASCII_out)
        self.PaintAct = QAction(QIcon(resource_path('image.png')), "Show image", self,
                              statusTip="Show image in window", triggered=self.image_out)
        self.aboutAct = QAction("&About", self,
                statusTip="Show the application's About box", triggered=self.about)


    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)
        self.actionsMenu = self.menuBar().addMenu("&Actions")
        self.actionsMenu.addAction(self.RTFAct)
        self.actionsMenu.addAction(self.PSAct)
        self.actionsMenu.addAction(self.AscAct)
        self.actionsMenu.addAction(self.PaintAct)
        self.actionsMenu.addAction(self.doPrefsAct)

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)


    def createToolBars(self):
        self.ToolBar = self.addToolBar("Actions")
        self.ToolBar.addAction(self.openAct)
        p1 = QWidget()
        p2 = QWidget()
        p3 = QWidget()
        self.ToolBar.insertWidget(QAction(), p1)
        p1.setFixedWidth(20)
        self.ToolBar.addAction(self.RTFAct)
        self.ToolBar.addAction(self.PSAct)
        self.ToolBar.addAction(self.AscAct)
        self.ToolBar.insertWidget(QAction(), p2)
        p2.setFixedWidth(20)
        self.ToolBar.addAction(self.PaintAct)
        self.ToolBar.insertWidget(QAction(), p3)
        p3.setFixedWidth(30)
        self.ToolBar = self.addToolBar("Settings")
        self.ToolBar.addAction(self.doPrefsAct)

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def readSettings(self):
        settings = QSettings("Boxshade", "Boxshade")
        settings.setFallbacksEnabled(False)
        pos = settings.value("pos", QPoint(200, 200))
        size = settings.value("size", QSize(1100, 760))
        self.resize(size)
        self.move(pos)

    def writeSettings(self):
        settings = QSettings("Boxshade", "Boxshade")
        settings.setValue("pos", self.pos())
        settings.setValue("size", self.size())

    def open(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        title = self.interface.text("Open alignment file") if hasattr(self, "interface") else "Open alignment file"
        fileName, _ = QFileDialog.getOpenFileName(self, title, BS.lastdir, file_filter, options=options)
        if fileName:
            self.loadFile(fileName)
            BS.lastdir = QFileInfo(fileName).absolutePath()

    def loadFile(self, fileName):
        try:
            data = read_alignment(fileName)
        except (OSError, UnicodeError, ValueError) as error:
            if hasattr(self, "interface"):
                self.interface.show_error("Unable to open alignment", error)
            else:
                QMessageBox.warning(self, "Unable to open alignment", str(error))
            return False
        self.seqs = np.array([list(seq) for seq in data.sequences], str, order="F")
        self.seqnames = list(data.names)
        self.consensnum = 1
# release the memory used by the BioPython construct, not needed now.
# now that I know how big an alignment I have, I redefine the space taken up by the various arrays
        self.no_seqs = self.seqs.shape[0]
        self.maxseqlen = self.seqs.shape[1]
        if system() == "Darwin":
            BS.monofont.setPointSize(14)
        else:
            BS.monofont.setPointSize(12)
        BS.monofont.setWeight(QFont.Normal)
        self.textEdit.setFont(BS.monofont)
        self.textEdit.setPlainText(data.text)
        self.cols = np.full(self.seqs.shape, 0, dtype=np.int32)
        self.cons = np.full(self.maxseqlen, ' ', dtype=str)
        self.conschar = np.copy(self.cons)
        self.seqlens = np.full(self.no_seqs, self.maxseqlen, dtype=np.int32)
        self.startnums = np.full(self.no_seqs, 1, dtype=np.int64) # a newly loaded file has all startnums set to 1 by default
#
#set consensus length = length of longest sequence (not counting dots,
#spaces, etc. at the "far" end. May be a problem here for some strange cases
        self.consenslen = 0
        for i in range(0,self.no_seqs):
            while self.seqlens[i] and (self.seqs[i, self.seqlens[i] - 1] in gapchars):
                self.seqlens[i] -= 1
            if self.seqlens[i] > self.consenslen:
                self.consenslen = self.seqlens[i]
        self.setCurrentFile(fileName)
        self.process_seqs()
        self.statusBar().showMessage("File loaded", 2000)
        return True

    def make_consensus(self):
        settings = QSettings("Boxshade", "Boxshade")
        thrfrac = settings.value("thrfrac", type=float)
        scflag = settings.value("scflag", type=bool)
        countGaps = settings.value("countGaps", type=bool)
        self.pepseqsflag = settings.value("pepseqsflag", type=bool)
        readsims() # (re)-read the sims/grps and remake the simtable and grptable, in case settings have changed
# procedure to make a consensus which forms the basis of the shading
        thr = round(thrfrac*self.no_seqs)
        if not scflag:
            uf=np.frompyfunc(grp,2,1)
            for i in range(0, self.consenslen):
                x = self.seqs[:, i]
                xx=np.char.isalpha(x)
                self.cons[i] = ' '
                if not np.any(xx):
                    continue
                if not countGaps:
                    thr = round(thrfrac*np.sum(xx))
                idcount = np.sum(x == x[xx,None], 0)
                grpcount = np.sum(uf(x, x[xx,None]).astype(bool), 0)
                self.cons[i] = ' '
                maxidcount = np.amax(idcount)
                maxgrpcount = np.amax(grpcount)
                idindex = list(chain.from_iterable(np.where(idcount == maxidcount)))
                grpindex = list(chain.from_iterable(np.where(grpcount == maxgrpcount)))
# if there is a single maxid, and it is greater than the threshold, that is the consensus
                if maxidcount >= thr :
                    if len(idindex) == 1 :
                       self.cons[i] = x[idindex[0]]
# there is not a single maxidcount, but they may all be the same residue
# Have to check to see if all the residues with maxidcount are the same
                    else:
                        if np.all(x[idindex[0]]==x[idindex]):
                            self.cons[i] = x[idindex[0]]
#if there is an equally high idcount for a different residue then there can't be a
# single residue consensus, so look for a group consensus
                elif maxgrpcount >= thr:
                    if len(grpindex) == 1:
                        self.cons[i] = x[grpindex[0]]
                    elif np.all(uf(x[grpindex[0]], x[grpindex]).astype(bool)):
                        (vv,cc) = np.unique(x[grpindex], return_counts=True)
                        self.cons[i] = vv[np.argmax(cc)].lower()
# if maxsimcount is not unique and the other residue is NOT in the same
# similarity group then there is so consensus based on similarity. If
# the two residues with the same similarity score are in the same
# similarity group, flag that consensus position by making the
# residue lowercase

        else:
# this 'else' means that the scflag (make specific sequence the consensus) is true, so copy the sequence at row self.consensnum-1 into cons[]
            np.copyto(self.cons[0:self.consenslen], self.seqs[self.consensnum-1, 0:self.consenslen])

        return # from make_consensus

    def make_colours(self):
# The array of "colours" defines the shading that will be applied to each array
        settings = QSettings("Boxshade", "Boxshade")
        thrfrac = settings.value("thrfrac", type=float)
        scflag = settings.value("scflag", type=bool)
        consflag = settings.value("consflag", type=bool)
        symbcons = settings.value("symbcons")
        countGaps = settings.value("countGaps", type=bool)
        thr = round(thrfrac * self.no_seqs)
        self.cols.fill(0)
        seqcount = self.no_seqs
        for i in range(0, self.consenslen):
            idcount = 0
            simcount = 0
            if not np.any(np.char.isalpha(self.seqs[:, i])):
                self.conschar[i] = ' '
                continue
            aasetflag = self.cons[i] in aaset
            if not countGaps:
                seqcount=np.sum(np.char.isalpha(self.seqs[:, i]))
                thr = round(thrfrac * seqcount)

# count similar residues for the case of a group consensus;
# note that in this case there cannot be any residues marked as
# 'identical', by definition
            if self.cons[i] in aasetlow : # the np test here is 100x slower
                for j in range(0, self.no_seqs) :
                    if grp(self.seqs[j,i], self.cons[i].upper()):
                        self.cols[j,i] = 2
                        simcount += 1
            else:
                for j in range(0, self.no_seqs):
                    if self.seqs[j,i] == self.cons[i]:
                        idcount += 1
                    elif sim(self.seqs[j,i], self.cons[i]):
                        simcount += 1
                if (idcount == seqcount) and aasetflag:
                    if countGaps:
                        self.cols[:,i] = 3 # if all sequences same colour them identical idcount+
                    else:
                        for j in range(0, self.no_seqs):
                            if self.seqs[j, i] in gapchars:
                                self.cols[j, i] = 0  # a gap, always uncoloured
                            else:
                                self.cols[j, i] = 3
                elif ((idcount+simcount) >= thr) and aasetflag:
                    for j in range(0, self.no_seqs):
                        if self.seqs[j,i] == self.cons[i]:
                            self.cols[j,i] = 1 # a consensus residue
                        elif sim(self.seqs[j,i], self.cons[i]):
                            self.cols[j,i] = 2 # similar to the consensus

            if consflag: # should generate a consensus line
                        # in Python, there is no way to do this except with multiple nested if/elif/elses
                if idcount == seqcount:
                    symbchar=symbcons[2].upper()
                    if symbchar == 'U':
                        self.conschar[i] = self.cons[i].upper()
                    elif symbchar == "L":
                        self.conschar[i] = self.cons[i].lower()
                    elif symbchar == "B" or symbchar == " ":
                        self.conschar[i] = " "
                    else: self.conschar[i] =symbcons[2]
                elif (idcount+simcount)>=thr :
                    symbchar = symbcons[1].upper()
                    if symbchar == 'U':
                        self.conschar[i] = self.cons[i].upper()
                    elif symbchar == "L":
                        self.conschar[i] = self.cons[i].lower()
                    elif symbchar == "B" or symbchar == " ":
                        self.conschar[i] = " "
                    else: self.conschar[i] = symbcons[1]
                else:
                    symbchar = symbcons[0].upper()
                    if symbchar == 'U':
                        self.conschar[i] = self.cons[i].upper()
                    elif symbchar == "L":
                        self.conschar[i] = self.cons[i].lower()
                    elif symbchar == "B" or symbchar == " ":
                        self.conschar[i] = " "
                    else: self.conschar[i] = symbcons[0]
        return # end of the function make_colours

    def process_seqs(self):
        if self.no_seqs < 2:
            return
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self.make_consensus()
            self.make_colours()
        finally:
            QApplication.restoreOverrideCursor()

    def prep_out(self, gr_out):
        settings = QSettings("Boxshade", "Boxshade")
        self.LHsnumsflag = settings.value("LHsnumsflag", type=bool)
        self.RHsnumsflag = settings.value("RHsnumsflag", type=bool)
        self.defnumsflag = settings.value("defnumsflag", type=bool)

        self.scflag = settings.value("scflag", type=bool)
        self.consflag = settings.value("consflag", type=bool)
        self.snameflag = settings.value("snameflag", type=bool)
        self.globalflag = settings.value("globalflag", type=bool)
        self.outlen = settings.value("outlen", type=int)
        self.interlines = settings.value("interlines", type=int)
        self.rulerflag = settings.value("rulerflag", type=bool)

        QApplication.setOverrideCursor(Qt.WaitCursor)
        sname_just = max((self.consflag*9), max(map(len, self.seqnames)))
        nseqs = self.no_seqs
        if self.consflag:
            nseqs += 1
        if self.rulerflag:
            nseqs += 1
            gr_out.seqnames.append(" ".ljust(sname_just))
        gr_out.seqs = np.full((nseqs, self.seqs.shape[1]), ' ', dtype=str)
        gr_out.cols = np.full((nseqs, self.seqs.shape[1]), 0, dtype=np.int32)
        gr_out.seqlens = np.full(nseqs, 0, dtype=np.int64)
        gr_out.seqnames.extend([name.ljust(sname_just) for name in self.seqnames])
        if self.consflag:
            gr_out.seqnames.append("consensus".ljust(sname_just))
        if self.rulerflag: #code here to create ruler and put it in first line of gr_out.seqs
            gr_out.seqlens[0] = self.consenslen
            np.copyto(gr_out.seqs[0], np.array(['.']))
            gr_out.seqs[0,list(range(4,self.consenslen,10))] = ':'
            np.copyto(gr_out.cols[0], np.array([4]))
            gr_out.seqs[1,0] = '1'
            for i in range(10, self.consenslen+1, 10):
                inum = list(str(i))
                li = len(inum)
                for j in range(li):
                    gr_out.seqs[0,(j+i-li)]=inum[j]
        np.copyto(gr_out.seqs[self.rulerflag:self.rulerflag+self.no_seqs, :], self.seqs)
        np.copyto(gr_out.cols[self.rulerflag:self.rulerflag+self.no_seqs, :], self.cols)
        np.copyto(gr_out.seqlens[self.rulerflag:self.rulerflag+self.no_seqs], self.seqlens)
        if self.scflag and (self.consensnum >0):
            np.copyto(gr_out.cols[self.consensnum-1+self.rulerflag], np.array([4]))
        if self.consflag:
            np.copyto(gr_out.seqs[nseqs-1,:], self.conschar)
            np.copyto(gr_out.cols[nseqs-1,:], np.array([4]))
            gr_out.seqlens[nseqs-1] = self.consenslen

        gr_out.no_seqs = self.no_seqs
        gr_out.make_lowercase(self.rulerflag)
        gr_out.no_seqs = nseqs
        if self.LHsnumsflag or self.RHsnumsflag:
            gr_out.startnums = np.full(nseqs, 0, dtype=np.int64)
            if self.rulerflag:
                gr_out.startnums[0] = 1
            np.copyto(gr_out.startnums[self.rulerflag:self.rulerflag + self.no_seqs],
                      np.ones_like(self.startnums) if self.defnumsflag else self.startnums)
            if self.consflag:
                gr_out.startnums[nseqs - 1] = 1
            nblocks = (self.consenslen + self.outlen - 1)//self.outlen
            gr_out.LHprenums = [['' for i in range(nblocks)] for j in range(nseqs)]
            gr_out.RHprenums = [['' for i in range(nblocks)] for j in range(nseqs)]
            numlen = max(len(str(int(number)+offset)) for number in gr_out.startnums
                         for offset in (0, self.consenslen+1))
            if self.rulerflag:
                gr_out.LHprenums[0] = [' ' * numlen for x in gr_out.LHprenums[0]]
                gr_out.RHprenums[0] = [' ' * numlen for x in gr_out.RHprenums[0]]
            for i in range(self.rulerflag, nseqs-self.consflag):
                totcount = int(gr_out.startnums[i])
                if totcount == 0:
                    totcount = 1
                bn = 0
                thisline = 0
                for j in range(0, self.consenslen):
                    if gr_out.seqs[i,j] in chars:
                        thisline +=1
                    if ((j+1) % self.outlen == 0) or j == self.consenslen-1:
                        if (totcount == gr_out.startnums[i]) and (thisline == 0): # no chars yet
                            gr_out.LHprenums[i][bn] = ' ' * numlen
                            gr_out.RHprenums[i][bn] = ' ' * numlen
                        elif (j > gr_out.seqlens[i]) and (thisline == 0): # empty stuff at the end
                            gr_out.LHprenums[i][bn] = ' ' * numlen
                            gr_out.RHprenums[i][bn] = ' ' * numlen
                        else:
                            gr_out.LHprenums[i][bn] = str(totcount).rjust(numlen)
                            last = totcount + thisline - 1
                            if totcount < 0 and last >= 0:
                                last += 1
                            gr_out.RHprenums[i][bn] = str(last).rjust(numlen)
                            totcount = last + 1
                            if totcount == 0:
                                totcount = 1
                        bn += 1
                        thisline = 0
            if self.consflag:
                consl = nseqs - 1
                gr_out.LHprenums[consl] = [' ' * numlen for x in gr_out.LHprenums[consl]]
                gr_out.RHprenums[consl] = [' ' * numlen for x in gr_out.RHprenums[consl]]
        if not gr_out.graphics_init():
            QApplication.restoreOverrideCursor()
            return False
        else:
            return True
# at the end out prep_out, the formatted set of seqs/ruler, consensus, etc are stored in the output object

    def do_out(self,gr_out):
        nblocks = ((self.consenslen -1)// self.outlen)+1
        ll = (nblocks*(gr_out.no_seqs+self.interlines))-self.interlines
        lcount = 0
        for i in range(0, nblocks):
            for j in range(0, gr_out.no_seqs):
                if self.snameflag:
                    gr_out.set_colour(4)
                    gr_out.string_out(gr_out.seqnames[j]+' ')
                if self.LHsnumsflag:
                    gr_out.set_colour(4)
                    gr_out.string_out(gr_out.LHprenums[j][i]+' ')
                io=i*self.outlen
                for k in range(self.outlen):
                    m = io+k
                    if m <= self.consenslen-1:
                        gr_out.set_colour(gr_out.cols[j,m])
                        gr_out.char_out(gr_out.seqs[j,m])
                if self.RHsnumsflag:
                    gr_out.set_colour(4)
                    gr_out.string_out(' '+gr_out.RHprenums[j][i])
                lcount +=1
                if lcount >= gr_out.lines_per_page and ll > lcount:
                    ll -= lcount
                    lcount = 0
                    gr_out.newpage()
                else:
                    gr_out.newline()
            if i == nblocks - 1:
                break
            if (lcount + gr_out.no_seqs + self.interlines) <= gr_out.lines_per_page:
                for j in range(self.interlines):
                    gr_out.newline()
                    lcount +=1
            else:
                ll -= lcount
                lcount = 0
                gr_out.newpage()
        gr_out.exit()
        QApplication.restoreOverrideCursor()

    def RTF_out(self):
        if self.no_seqs < 2:
            return
        gr_out = RTFdev(self.strippedName(self.curFile))
        if not self.prep_out(gr_out):
            return
        self.do_out(gr_out)

    def PS_out(self):
        if self.no_seqs < 2:
            return
        gr_out = PSdev(self.strippedName(self.curFile))
        if not self.prep_out(gr_out):
            return
        self.do_out(gr_out)

    def image_out(self):
        if self.no_seqs < 2:
            return
# NB QPainter can only access co-ordinates at +/- 2^15, i.e. +/- 32768, so I limit the size of the canvas
# Carry out a check here and abort if height would be out of range
# Width cannot be > 32768 given a max font size of 48 and linelength of 250
        settings = QSettings("Boxshade", "Boxshade")
        self.outlen = settings.value("outlen", type=int)
        self.rulerflag = settings.value("rulerflag", type=bool)
        self.consflag = settings.value("consflag", type=bool)
        self.interlines = settings.value("interlines", type=int)

        gr_out = Paintdev(self)
        blocks = (self.consenslen + self.outlen - 1)//self.outlen
        nlines = self.no_seqs+self.consflag +self.rulerflag+self.interlines
        height = int(gr_out.top_mar + (gr_out.dev_ysize*((blocks*nlines)-self.interlines))+gr_out.top_mar+0.5)
        if height > 32768:
            mb = QMessageBox(self)
            mb.setTextFormat(Qt.RichText)
            mb.setText("<p style='font-size: 18pt'>Picture too large!</p>"
                       "<p style='font-size: 14pt; font-weight: normal'> Sorry, this picture would be too high.<br>"
                       "The drawing system used by pyBoxshade is limited to 32768 pixels in width or height.<br>"
                       "Your output would have a height of {:n} pixels.</p>".format(height))
            mb.setIcon(QMessageBox.Information)
            mb.exec()
            return
        if not self.prep_out(gr_out):
            return
        self.do_out(gr_out)
        self.view = ImageDisp(self)
        self.viewList.append(self.view)
        self.view.setWindowTitle(self.strippedName(self.curFile))
        self.view.imageLabel.setPixmap(gr_out.canvas)
        self.view.imageLabel.resize(self.view.imageLabel.pixmap().size())
        self.view.updateActions()
        self.view.show()


    def ASCII_out(self):
        if self.no_seqs < 2:
            return
        settings = QSettings("Boxshade", "Boxshade")
        scflag = settings.value("scflag", type=bool)
        if not scflag:
            mb = QMessageBox(self)
            mb.setTextFormat(Qt.RichText)
            mb.setText("<p style='font-size: 18pt'>Output options error</p>"
                "<p style='font-size: 14pt; font-weight: normal'> Text (ASCII) output requires you to select a specific sequence to which the others will be compared</p>")
            mb.setIcon(QMessageBox.Warning)
            mb.exec()
            return
        gr_out = ASCIIdev(self.strippedName(self.curFile))
        if not self.prep_out(gr_out):
            return
        self.do_out(gr_out)

    def setCurrentFile(self, fileName):
        self.curFile = fileName
        self.textEdit.document().setModified(False)
        self.setWindowModified(False)

        if self.curFile:
            shownName = self.strippedName(self.curFile)
        else:
            shownName = 'Boxshade window'

        self.setWindowTitle("{:s} ".format(shownName))

    def strippedName(self, fullFileName):
        return QFileInfo(fullFileName).fileName()


if __name__ == '__main__':

    from pyboxshade.cli import main
    sys.exit(main())
