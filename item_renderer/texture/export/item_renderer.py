import os
import bpy
from manager import Manager
from util.blender_extra.material import createMaterialFromTemplate, setImage


_textureDir = "texture"
_materialTemplateFilename = "building_material_templates.blend"
_materialTemplateName = "export"


class ItemRendererMixin:
    """
    A mixin class
    """
    
    def getCladdingMaterialId(self, item, claddingTextureInfo):
        color = self.getCladdingColorHex(item)
        return "%s_%s%s" % (color, claddingTextureInfo["material"], os.path.splitext(claddingTextureInfo["name"])[1])\
            if claddingTextureInfo and color\
            else claddingTextureInfo["name"]
    
    def createCladdingMaterial(self, materialName, claddingTextureInfo):
        if not materialName in bpy.data.materials:
            # check if have texture in the data directory
            textureFileName, textureDir, textureFilepath = self.getTextureFilepath(materialName)
            if not os.path.isfile(textureFilepath):
                self.makeCladdingTexture(
                    textureFileName,
                    textureDir,
                    textureFilepath,
                    claddingTextureInfo
                )
            
            self.createMaterialFromTemplate(materialName, textureFilepath)
        return True
    
    def makeCladdingTexture(self, textureFilename, textureDir, textureFilepath, claddingTextureInfo):
        textureExporter = self.r.textureExporter
        scene = textureExporter.getTemplateScene("compositing_cladding_color")
        nodes = textureExporter.makeCommonPreparations(
            scene,
            textureFilename,
            textureDir
        )
        # cladding texture
        textureExporter.setImage(
            claddingTextureInfo["name"],
            claddingTextureInfo["path"],
            nodes,
            "cladding_texture"
        )
        # cladding color
        textureExporter.setColor(self.claddingColor, nodes, "cladding_color")
        # render the resulting texture
        textureExporter.renderTexture(scene, textureFilepath)
    
    def getCladdingColorHex(self, item):
        color = item.getStyleBlockAttrDeep("claddingColor")
        # remember the color for a future use in the next funtion call
        self.claddingColor = color
        # return a hex string
        return "{:02x}{:02x}{:02x}".format(round(255*color[0]), round(255*color[1]), round(255*color[2]))
    
    def getTextureFilepath(self, materialName):
        textureFilename = "baked_%s" % materialName
        textureDir = os.path.join(self.r.app.dataDir, _textureDir)
        return textureFilename, textureDir, os.path.join(textureDir, textureFilename)
    
    def createMaterialFromTemplate(self, materialName, textureFilepath):
        materialTemplate = self.getMaterialTemplate(
            _materialTemplateFilename,
            _materialTemplateName
        )
        nodes = createMaterialFromTemplate(materialTemplate, materialName)
        # the overlay texture
        setImage(
            textureFilepath,
            None,
            nodes,
            "Image Texture"
        )