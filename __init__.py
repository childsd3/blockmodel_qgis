# -*- coding: utf-8 -*-
"""
/***************************************************************************
 BlockModel
                                 A QGIS plugin
 3d block model tools
                             -------------------
        begin                : 2016-02-07
        copyright            : (C) 2016 by Daniel Childs
        email                : daniel@fatbug.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load BlockModel class from file BlockModel.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .block_model import BlockModel
    return BlockModel(iface)
