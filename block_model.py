# -*- coding: utf-8 -*-
"""
/***************************************************************************
 BlockModel
                                 A QGIS plugin
 3d block model tools
                              -------------------
        begin                : 2016-02-07
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Daniel Childs
        email                : daniel@fatbug.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
#from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
#from PyQt4.QtGui import QAction, QIcon, QFileDialog

from PyQt4.QtCore import *
from PyQt4.QtGui import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from block_model_dialog import BlockModelDialog
import os.path
from qgis.core import *
from qgis.gui import *
import qgis.utils
import cni as cni

class BlockModel:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'BlockModel_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = BlockModelDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Block Model')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'BlockModel')
        self.toolbar.setObjectName(u'BlockModel')
        
        ## Initialize select block model button
        self.dlg.lineEdit.clear()
        self.dlg.pushButton.clicked.connect(self.select_blockmodel_file)
        self.dlg.outputFilePath.clear()
        self.dlg.outputFileButton.clicked.connect(self.select_output_path)
        self.dlg.buildExposedSurfaceButton.clicked.connect(self.buildExposedSurface)
        

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('BlockModel', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/BlockModel/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Block Model'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Block Model'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
        
    def select_output_path(self):
        fileEnding = '.asc'
        filename = QFileDialog.getSaveFileName(self.dlg, "Select output file ","", '*'+fileEnding)
        if filename == '':
        	return
        if filename[-4:] != '.asc':
            filename = filename+'.asc'
        self.dlg.outputFilePath.setText(filename)
    
    def select_blockmodel_file(self):
        filename = QFileDialog.getOpenFileName(self.dlg, "Select block model file ","", '*.csv')
        if filename == '':
        	return
        self.dlg.lineEdit.setText(filename)
        f=open(filename)
        lines = list()
        numCols = 0
        for i in range(11):
            line = f.next().strip().split(',')
            if len(line) > numCols:
                numCols = len(line)
            lines.append(line)
        self.dlg.tableWidget.setColumnCount(numCols)
        self.dlg.tableWidget.setRowCount(len(lines)-1)
        self.dlg.tableWidget.setHorizontalHeaderLabels(lines[0])
        for i in range(1,len(lines)):
            for j in range(len(lines[i])):
                item = QTableWidgetItem(lines[i][j])
                self.dlg.tableWidget.setItem(i-1,j,item)
        self.dlg.tableWidget.resizeColumnsToContents()
        self.dlg.tableWidget.resizeRowsToContents()
        
        self.dlg.eastingColumnSelection.clear()
        self.dlg.northingColumnSelection.clear()
        self.dlg.elevationColumnSelection.clear()
        self.dlg.valueColumnSelection.clear()

        self.dlg.eastingColumnSelection.addItems(lines[0])
        self.dlg.northingColumnSelection.addItems(lines[0])
        self.dlg.elevationColumnSelection.addItems(lines[0])
        self.dlg.valueColumnSelection.addItems(lines[0])
        
        self.dlg.eastingColumnSelection.setCurrentIndex(cni.guessEasting(lines[0]))
        self.dlg.northingColumnSelection.setCurrentIndex(cni.guessNorthing(lines[0]))
        self.dlg.elevationColumnSelection.setCurrentIndex(cni.guessElevation(lines[0]))
        self.dlg.valueColumnSelection.setCurrentIndex(3)
        
    def buildExposedSurface(self):
        self.dlg.statusBlockModelExtents.setValue(0)
        self.dlg.statusBlockModelLoading.setValue(0)
        self.dlg.statusIntersections.setValue(0)
        self.dlg.statusOutput.setValue(0)
        xCol = self.dlg.eastingColumnSelection.currentIndex()
        yCol = self.dlg.northingColumnSelection.currentIndex()
        zCol = self.dlg.elevationColumnSelection.currentIndex()
        valueCol = self.dlg.valueColumnSelection.currentIndex()
        blockModelFile = self.dlg.lineEdit.text()
        outputFile = self.dlg.outputFilePath.text()
        layers = self.iface.legendInterface().layers()
        for layer in layers:
            if str(layer.name()) == str(self.dlg.comboBox.currentText()):
				selectedLayer = layer
        sNODATA_value = -1
        print('Loading ASC surface.')
        sncols,snrows,sxllcorner,syllcorner,scellsize = cni.dtmProperties(layer)
        print('Finding block model limits.')
        bminX,bminY,bminZ,bnCols,bnRows,bnLvls,bcolSize,browSize,blvlSize = cni.blockModelLimits(blockModelFile,self.dlg.statusBlockModelExtents)
        print('Initializing 3d block model.')
        blockModel = cni.make3dList(bnCols,bnRows,bnLvls)
        print('Populating block model.')
        blockModelFileLength = cni.file_len(blockModelFile)
        with open(blockModelFile, 'r') as f:
            counter = 0
            status = 0
            for line in f:
                counter += 1
                if counter == 1:
                    continue
                incStatus = cni.percentStatus(counter,blockModelFileLength)
                if incStatus > status:
                    status = incStatus
                    self.dlg.statusBlockModelLoading.setValue(status)
                lineArray = line.split(",")
                xValue = float(lineArray[xCol])
                yValue = float(lineArray[yCol])
                zValue = float(lineArray[zCol])
                icol,irow,ilvl = cni.xyz2index(xValue,yValue,zValue,bminX,bminY,bminZ,bcolSize,browSize,blvlSize)
                try:
                    blockModel[icol][irow][ilvl] = float(lineArray[valueCol])
                except:
                    print(icol,irow,ilvl,float(lineArray[valueCol]))
        print('Building ASC')
        blankASC = cni.make2dList(sncols,snrows)
        ascCounter = 0
        ascArrayLength = len(blankASC)*len(blankASC[0])
        for i in range(len(blankASC)):
            for j in range(len(blankASC[0])):
                ascCounter += 1
                status = 0
                incStatus = cni.percentStatus(ascCounter,ascArrayLength)
                if incStatus > status:
                    status = incStatus
                    self.dlg.statusIntersections.setValue(status)
                x,y = cni.index2xy(i,j,sxllcorner,syllcorner,scellsize)
                value = selectedLayer.dataProvider().identify(QgsPoint(x,y),QgsRaster.IdentifyFormatValue).results()[1]
                try:
                    bi_row,bi_col,bi_lvl = cni.xyz2index(x,y,value,bminX,bminY,bminZ,bcolSize,browSize,blvlSize)
                    blockValue = blockModel[bi_row][bi_col][bi_lvl]
                    blankASC[i][j] = blockValue
                except:
                    blankASC[i][j] = sNODATA_value
        script = cni.generateASC(blankASC,sncols,snrows,sxllcorner,syllcorner,scellsize,sNODATA_value)
        f = open(outputFile, 'w')
        f.write(script)
        f.close()
        self.dlg.statusOutput.setValue(100)

    def run(self):
        self.dlg.comboBox.clear()
        self.dlg.lineEdit.clear()
        self.dlg.outputFilePath.clear()
        self.dlg.tableWidget.setRowCount(0)
        self.dlg.tableWidget.setColumnCount(0)
        self.dlg.eastingColumnSelection.clear()
        self.dlg.northingColumnSelection.clear()
        self.dlg.elevationColumnSelection.clear()
        self.dlg.valueColumnSelection.clear()
        self.dlg.statusBlockModelExtents.setValue(0)
        self.dlg.statusBlockModelLoading.setValue(0)
        self.dlg.statusIntersections.setValue(0)
        self.dlg.statusOutput.setValue(0)
        layers = self.iface.legendInterface().layers()
        layer_list = []
        if len(layers) == 0:
			return
        for layer in layers:
            if layer.type() == layer.RasterLayer:
                layer_list.append(layer.name())
        self.dlg.comboBox.addItems(layer_list)
        for layer in layers:
            if layer.name() == self.dlg.comboBox.currentText():
                selectedLayer = layer
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
