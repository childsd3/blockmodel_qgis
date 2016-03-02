# Block Model

Block Model is a QGIS plugin that generates the surface exposure of three dimensional block models.

### What's a block model?
A block model is a uniformly gridded data file that has values assigned to specific spatial coordinates (x,y,z). For example lets assume a 50ft x 50ft x 50ft block that begins at 0 ft, 0 ft, 0 ft fills a cube to 500 ft, 500 ft, 500 ft. Values, such as geology lithologic codes, in the block model are assigned to each of the x,y,z coordinates.

### Great, what does that mean?
In essence, this means we can show what the surface exposure of a geologic model would be on an excavation in the earth (like an open pit mine). **NOTE, if you don't have the means to create a block model, this plugin will likely be useless to you in it's current state.**

### Required Inputs
 - Block Model (.csv file with at least an x, y, z, and value)
 - Surface DTM
