from panda3d.bullet import *
from panda3d.core import *

from shader import GeneradorShader
from objetos import *
import sistema, config

import math

import logging
log=logging.getLogger(__name__)

#
# TERRENO
#
class Terreno:
    
    # tamano de la parcela
    TamanoParcela=32

    # radio de expansion
    RadioExpansion=1 #4

    def __init__(self, base, bullet_world):
        # referencias:
        self.base=base
        self.bullet_world=bullet_world
        self.sistema=None
        # componentes:
        self.nodo=self.base.render.attachNewNode("terreno")
        self.nodo_parcelas=self.nodo.attachNewNode("parcelas")
        self.nodo_naturaleza=self.nodo.attachNewNode("naturaleza")
        #self.nodo.setRenderModeWireframe()
        self.parcelas={} # {idx_pos:parcela_node_path,...}
        self.naturaleza={} # {idx_pos:naturaleza_node_path,...}
        # variables externas:
        self.idx_pos_parcela_actual=None # (x,y)
        self.switch_lod_naturaleza=(6.0*Terreno.TamanoParcela, 0.0)
        # debug
        self.dibujar_normales=False # cada update

    def iniciar(self):
        log.info("iniciar")
        #
        self.sistema=sistema.obtener_instancia()
        #
        self._establecer_shader()
        #
        Terreno.RadioExpansion=int(config.val("terreno.radio_expansion"))
        self.dibujar_normales=config.valbool("terreno.dibujar_normales")
        #
        log.info("altitud (%s)=%.3f"%(str((0, 0)), self.sistema.obtener_altitud_suelo((0, 0))))
    
    def terminar(self):
        log.info("terminar")
        terminar_objetos()
        self.sistema=None
    
    def obtener_indice_parcela(self, pos):
        x=pos[0]/Terreno.TamanoParcela
        y=pos[1]/Terreno.TamanoParcela
        if x<0.0: x=math.floor(x)
        if y<0.0: y=math.floor(y)
        return (int(x), int(y))
    
    def obtener_pos_parcela(self, idx_pos):
        x=idx_pos[0]*Terreno.TamanoParcela
        y=idx_pos[1]*Terreno.TamanoParcela
        return (x, y, 0.0)

    def obtener_info(self):
        pos_parcela_actual=None
        temp=None
        if len(self.parcelas)>0:
            parcela_actual=self.parcelas[self.idx_pos_parcela_actual]
            pos_parcela_actual=parcela_actual.getPos() 
            temp=self.sistema.obtener_temperatura_anual_media_norm(pos_parcela_actual.getXy())
        #
        info="Terreno\n"
        info+="idx_pos_parcela_actual=%s pos=%s\n"%(str(self.idx_pos_parcela_actual), str(pos_parcela_actual))
        info+="RadioExpansion=%i altitud=%.2f temp_base=%s\n"%(Terreno.RadioExpansion, self.sistema.obtener_altitud_suelo_cursor(), str(temp))
        return info

    def update(self, forzar=False):
        #
        idx_pos=self.obtener_indice_parcela(self.sistema.posicion_cursor)
        #log.debug("idx_pos=%s"%(str(idx_pos)))
        if forzar or idx_pos!=self.idx_pos_parcela_actual:
            self.idx_pos_parcela_actual=idx_pos
            #
            idxs_pos_parcelas_obj=[]
            idxs_pos_parcelas_cargar=[]
            idxs_pos_parcelas_descargar=[]
            # determinar parcelas que deben estar cargadas
            for idx_pos_x in range(idx_pos[0]-Terreno.RadioExpansion, idx_pos[0]+Terreno.RadioExpansion+1):
                for idx_pos_y in range(idx_pos[1]-Terreno.RadioExpansion, idx_pos[1]+Terreno.RadioExpansion+1):
                    idxs_pos_parcelas_obj.append((idx_pos_x, idx_pos_y))
            # crear listas de parcelas a descargar y a cargar
            for idx_pos in self.parcelas.keys():
                if idx_pos not in idxs_pos_parcelas_obj:
                    idxs_pos_parcelas_descargar.append(idx_pos)
            for idx_pos in idxs_pos_parcelas_obj:
                if idx_pos not in self.parcelas:
                    idxs_pos_parcelas_cargar.append(idx_pos)
            # descarga y carga de parcelas
            for idx_pos in idxs_pos_parcelas_descargar:
                self._descargar_parcela(idx_pos)
            for idx_pos in idxs_pos_parcelas_cargar:
                self._generar_parcela(idx_pos)

    def _generar_parcela(self, idx_pos):
        # posición y nombre
        pos=self.obtener_pos_parcela(idx_pos)
        nombre="parcela_%i_%i"%(int(idx_pos[0]), int(idx_pos[1]))
        log.info("_generar_parcela idx_pos=%s pos=%s nombre=%s"%(str(idx_pos), str(pos), nombre))
        # nodo
        parcela_node_path=self.nodo_parcelas.attachNewNode(nombre)
        parcela_node_path.setPos(pos[0], pos[1], 0.0)
        # datos de parcela
        datos_parcela=self._generar_datos_parcela(pos, idx_pos)
        # geometria
        geom_node=self._generar_nodo_parcela(nombre, idx_pos, pos, datos_parcela, config.valbool("terreno.color_debug"))
        parcela_node_path.attachNewNode(geom_node)
        # generar textura guia de terreno
        ts2=TextureStage("ts_parcela") # para metodo de interpolacion de texturas
        textura_parcela=self._obtener_textura_parcela(nombre, datos_parcela, pos)
        parcela_node_path.setTexture(ts2, textura_parcela, priority=3)
        # debug: normales
        if self.dibujar_normales:
            geom_node_normales=self._generar_lineas_normales("normales_%i_%i"%(int(pos[0]), int(pos[1])), geom_node)
            geom_node_normales.reparentTo(parcela_node_path)
        # agregar a parcelas
        self.parcelas[idx_pos]=parcela_node_path
        # naturaleza
        naturaleza_node_path=self._generar_nodo_naturaleza(pos, idx_pos, datos_parcela) # datos_parcela es obsoleto
        naturaleza_node_path.setPos(pos[0], pos[1], 0.0)
        naturaleza_node_path.reparentTo(self.nodo_naturaleza)
        self.naturaleza[idx_pos]=naturaleza_node_path
        #
        if idx_pos==(0, 0):
            parcela_node_path.writeBamFile("parcela.bam")
            log.info("se escribio parcela.bam")

    def _descargar_parcela(self, idx_pos):
        log.info("_descargar_parcela %s"%str(idx_pos))
        #
        naturaleza=self.naturaleza[idx_pos]
        naturaleza.removeNode()
        del self.naturaleza[idx_pos]
        #
        parcela=self.parcelas[idx_pos]
        parcela.removeNode()
        del self.parcelas[idx_pos]
    
    def _obtener_textura_parcela(self, nombre, datos_parcela, pos):
        #
        if not os.path.exists("texturas/terreno"): # esto deberia ir en inicio!!!
            os.mkdir("texturas/terreno")
        #
        ruta_archivo_textura=os.path.join("texturas/terreno", "%s.png"%nombre)
        if not os.path.exists(ruta_archivo_textura):
            log.info("_obtener_textura_parcela se genera archivo de textura de parcela '%s'"%ruta_archivo_textura)
            tamano_imagen=int(Terreno.TamanoParcela/4)
            imagen=PNMImage(tamano_imagen, tamano_imagen)
            tamano_area=Terreno.TamanoParcela
            for x in range(tamano_imagen):
                for y in range(tamano_imagen):
                    d=datos_parcela[1+int(x*tamano_area/tamano_imagen)][1+int(y*tamano_area/tamano_imagen)]
                    imagen.setXelA(x, y, d.tipo[0]/10.0, d.tipo[1]/10.0, d.tipo[2], d.precipitacion_frecuencia)
            imagen.write(ruta_archivo_textura)
#            for x in range(tamano_area):
#                for y in range(tamano_area):
#                    print("x,y=%s %s"%(str((x, y)), str(imagen.getXel(x, y))))
        #
        tex0=self.base.loader.loadTexture(ruta_archivo_textura)
        return tex0
    
    def _calcular_tangente_binormal(self, v0, v1, v2, tc0, tc1, tc2, n0):
        """
        Lengyel, Eric. “Computing Tangent Space Basis Vectors for an Arbitrary Mesh”. Terathon Software, 2001. http://terathon.com/code/tangent.html
        //
        struct Triangle
        {
            unsigned short  index[3];
        };
        void CalculateTangentArray(long vertexCount, const Point3D *vertex, const Vector3D *normal,
                const Point2D *texcoord, long triangleCount, const Triangle *triangle, Vector4D *tangent)
        {
            Vector3D *tan1 = new Vector3D[vertexCount * 2];
            Vector3D *tan2 = tan1 + vertexCount;
            ZeroMemory(tan1, vertexCount * sizeof(Vector3D) * 2);
            
            for (long a = 0; a < triangleCount; a++)
            {
                long i1 = triangle->index[0];
                long i2 = triangle->index[1];
                long i3 = triangle->index[2];
                
                const Point3D& v1 = vertex[i1];
                const Point3D& v2 = vertex[i2];
                const Point3D& v3 = vertex[i3];
                
                const Point2D& w1 = texcoord[i1];
                const Point2D& w2 = texcoord[i2];
                const Point2D& w3 = texcoord[i3];
                
                float x1 = v2.x - v1.x;
                float x2 = v3.x - v1.x;
                float y1 = v2.y - v1.y;
                float y2 = v3.y - v1.y;
                float z1 = v2.z - v1.z;
                float z2 = v3.z - v1.z;
                
                float s1 = w2.x - w1.x;
                float s2 = w3.x - w1.x;
                float t1 = w2.y - w1.y;
                float t2 = w3.y - w1.y;
                
                float r = 1.0F / (s1 * t2 - s2 * t1);
                Vector3D sdir((t2 * x1 - t1 * x2) * r, (t2 * y1 - t1 * y2) * r,
                        (t2 * z1 - t1 * z2) * r);
                Vector3D tdir((s1 * x2 - s2 * x1) * r, (s1 * y2 - s2 * y1) * r,
                        (s1 * z2 - s2 * z1) * r);
                
                tan1[i1] += sdir;
                tan1[i2] += sdir;
                tan1[i3] += sdir;
                
                tan2[i1] += tdir;
                tan2[i2] += tdir;
                tan2[i3] += tdir;
                
                triangle++;
            }
            
            for (long a = 0; a < vertexCount; a++)
            {
                const Vector3D& n = normal[a];
                const Vector3D& t = tan1[a];
                
                // Gram-Schmidt orthogonalize
                tangent[a] = (t - n * Dot(n, t)).Normalize();
                
                // Calculate handedness
                tangent[a].w = (Dot(Cross(n, t), tan2[a]) < 0.0F) ? -1.0F : 1.0F;
            }
            
            delete[] tan1;
        }
        """
        #
        x1=v1[0]-v0[0]
        x2=v2[0]-v0[0]
        y1=v1[1]-v0[1]
        y2=v2[1]-v0[1]
        z1=v1[2]-v0[2]
        z2=v2[2]-v0[2]
        #
        s1=tc1[0]-tc0[0]
        s2=tc2[0]-tc0[0]
        t1=tc1[1]-tc0[1]
        t2=tc2[1]-tc0[1]
        #
        r_div=(s1*t2-s2*t1)
        r=1.0/r_div if r_div>0.0 else 0.0
        sdir=Vec3((t2 * x1 - t1 * x2) * r, (t2 * y1 - t1 * y2) * r, (t2 * z1 - t1 * z2) * r);
        tdir=Vec3((s1 * x2 - s2 * x1) * r, (s1 * y2 - s2 * y1) * r, (s1 * z2 - s2 * z1) * r);
        tan1=sdir
        tan2=tdir
        #
        t=(tan1-n0*Vec3.dot(n0, tan1)).normalized()
        th=-1.0 if (Vec3.dot(Vec3.cross(n0, tan1), tan2)<0.0) else 1.0
        #bn=Vec3.cross(n0, t)*th
        return Vec4(t[0], t[1], t[2], th) #bn.normalized()
    
    def _generar_datos_parcela(self, pos, idx_pos):
        # matriz de DatosLocalesTerreno; x,y->TamanoParcela +/- 1
        data=list() # x,y: [[n, ...], ...]
        _pos=(0, 0)
        tc_x, tc_y=0.0, 0.0
        for x in range(Terreno.TamanoParcela+3):
            if x==1: # 1, en vez de 0
                tc_x=0.0
            else:
                tc_x=x/(Terreno.TamanoParcela+1)
            data.append(list())
            for y in range(Terreno.TamanoParcela+3):
                if y==1: # 1, en vez de 0
                    tc_y=0.0
                else:
                    tc_y=y/(Terreno.TamanoParcela+1)
                d=DatosLocalesTerreno()
                #data.index=None # no establecer en esta instancia
                _pos=(pos[0]+x-1, pos[1]+y-1)
                precipitacion_frecuencia=self.sistema.obtener_precipitacion_frecuencia_anual(_pos)
                d.pos=Vec3(x-1, y-1, self.sistema.obtener_altitud_suelo(_pos))
                d.tc=Vec2(tc_x, tc_y)
                #d.tipo=Vec3(self.sistema.obtener_tipo_terreno(_pos)) # FS_FUNC_TEX_TERRENO_1
                d.tipo=Vec3(self.sistema.obtener_temperatura_anual_media_norm(_pos), self.sistema.obtener_precipitacion_frecuencia_anual(_pos), 0.0) # FS_FUNC_TEX_TERRENO_2
                d.precipitacion_frecuencia=precipitacion_frecuencia
                d.temperatura_base=0.0 # eliminar!!! esta por objetos.py
                data[x].append(d)
        # calcular normales
        for x in range(Terreno.TamanoParcela+1):
            for y in range(Terreno.TamanoParcela+1):
                v0=data[x+1][y+1].pos
                v1=data[x+2][y+1].pos
                v2=data[x+1][y+2].pos
                v3=data[x+2][y].pos
                v4=data[x][y+2].pos
                v5=data[x][y+1].pos
                v6=data[x+1][y].pos
                n0=self._calcular_normal(v0, v1, v2)
                n1=self._calcular_normal(v0, v3, v1)
                n2=self._calcular_normal(v0, v2, v4)
                n3=self._calcular_normal(v0, v5, v6)
                n_avg=(n0+n1+n2+n3)/4.0
                data[x+1][y+1].normal=n_avg
        # calcular tangent & binormal
        for x in range(Terreno.TamanoParcela+1):
            for y in range(Terreno.TamanoParcela+1):
                v0, tc0, n0=data[x+1][y+1].pos, data[x+1][y+1].tc, data[x+1][y+1].normal
                v1, tc1=data[x+2][y+1].pos, data[x+2][y+1].tc
                v2, tc2=data[x+1][y+2].pos, data[x+1][y+2].tc
                v3, tc3=data[x+2][y].pos, data[x+2][y].tc
                v4, tc4=data[x][y+2].pos, data[x][y+2].tc
                v5, tc5=data[x][y+1].pos, data[x][y+1].tc
                v6, tc6=data[x+1][y].pos, data[x+1][y].tc
                t0=self._calcular_tangente_binormal(v0, v1, v2, tc0, tc1, tc2, n0)
                t1=self._calcular_tangente_binormal(v0, v3, v1, tc0, tc3, tc1, n0)
                t2=self._calcular_tangente_binormal(v0, v2, v4, tc0, tc2, tc4, n0)
                t3=self._calcular_tangente_binormal(v0, v5, v6, tc0, tc5, tc6, n0)
                t_avg=(t0+t1+t2+t3)/4.0
                data[x+1][y+1].tangent=t_avg
        #
        return data

    def _generar_nodo_parcela(self, nombre, idx_pos, posicion, datos_parcela, con_color=False):
        # formato
        co_info_tipo_terreno=InternalName.make("info_tipo_terreno")
        if con_color: co_color=InternalName.make("Color") # debug
        format_array=GeomVertexArrayFormat()
        format_array.addColumn(InternalName.getVertex(), 3, Geom.NT_stdfloat, Geom.C_point)
        format_array.addColumn(InternalName.getNormal(), 3, Geom.NT_stdfloat, Geom.C_normal)
        format_array.addColumn(InternalName.getTexcoord(), 2, Geom.NT_stdfloat, Geom.C_texcoord)
        if con_color: format_array.addColumn(co_color, 4, Geom.NT_stdfloat, Geom.C_other) # debug
        format_array.addColumn(InternalName.getTangent(), 4, Geom.NT_stdfloat, Geom.C_vector)
        format_array.addColumn(co_info_tipo_terreno, 3, Geom.NT_stdfloat, Geom.C_other) # caro?! volver a float?
        formato=GeomVertexFormat()
        formato.addArray(format_array)
        # iniciar vértices y primitivas
        vdata=GeomVertexData("vertex_data", GeomVertexFormat.registerFormat(formato), Geom.UHStatic)
        vdata.setNumRows((Terreno.TamanoParcela+1)*(Terreno.TamanoParcela+1)) # +1 ?
        prim=GeomTriangles(Geom.UHStatic)
        # vertex writers
        wrt_v=GeomVertexWriter(vdata, InternalName.getVertex())
        wrt_n=GeomVertexWriter(vdata, InternalName.getNormal())
        wrt_t=GeomVertexWriter(vdata, InternalName.getTexcoord())
        wrt_i=GeomVertexWriter(vdata, co_info_tipo_terreno)
        wrt_tng=GeomVertexWriter(vdata, InternalName.getTangent())
        if con_color: wrt_c=GeomVertexWriter(vdata, co_color) # debug
        # llenar datos de vertices
        i_vertice=0
        for x in range(Terreno.TamanoParcela+1):
            for y in range(Terreno.TamanoParcela+1):
                # data
                d=datos_parcela[x+1][y+1]
                #print("x,y=%s %s"%(str((x, y)), str(d)))
                d.index=i_vertice # aqui se define el indice
                # llenar vertex data
                wrt_v.addData3(d.pos)
                wrt_n.addData3(d.normal)
                wrt_t.addData2(d.tc)
                wrt_i.addData3(d.tipo)
                wrt_tng.addData4(d.tangent)
                if con_color: # debug
                    if config.val("terreno.debug_info")=="bioma":
                        color=self.sistema.calcular_color_bioma_debug((posicion[0]+x, posicion[1]+y, 0.0))
                    elif config.val("terreno.debug_info")=="terreno":
                        color=self.sistema.calcular_color_terreno_debug((posicion[0]+x, posicion[1]+y, 0.0))
                    else:
                        log.error("valor erroneo de configuracion en terreno.debug_info: "+config.val("terreno.debug_info"))
                    wrt_c.addData4(color)
                i_vertice+=1
        # debug data
        #for fila in data:
        #    for _d in fila:
        #        log.debug(str(_d))
        # llenar datos de primitivas
        for x in range(Terreno.TamanoParcela):
            for y in range(Terreno.TamanoParcela):
                # vertices
                i0=datos_parcela[x+1][y+1].index
                i1=datos_parcela[x+2][y+1].index
                i2=datos_parcela[x+1][y+2].index
                i3=datos_parcela[x+2][y+2].index
                # primitivas
                prim.addVertex(i0)
                prim.addVertex(i1)
                prim.addVertex(i2)
                prim.closePrimitive()
                prim.addVertex(i2)
                prim.addVertex(i1)
                prim.addVertex(i3)
                prim.closePrimitive()
        # geom
        geom=Geom(vdata)
        geom.addPrimitive(prim)
        geom.setBoundsType(BoundingVolume.BT_box)
        # nodo
        geom_node=GeomNode(nombre)
        geom_node.addGeom(geom)
        geom_node.setBoundsType(BoundingVolume.BT_box)
        return geom_node
    
    def _generar_nodo_naturaleza(self, pos, idx_pos, datos_parcela):
        #
        tamano=Terreno.TamanoParcela+1
        naturaleza=Naturaleza(self.base, pos, tamano)
        naturaleza.iniciar()
        for x in range(tamano):
            for y in range(tamano):
                _d=datos_parcela[x+1][y+1]
                #log.debug(str(_d))
                naturaleza.cargar_datos(_d.pos, _d.temperatura_base)
        #
        nombre="nodo_naturaleza_%i_%i"%(idx_pos[0], idx_pos[1])
        #
        nodo=naturaleza.generar("%s_objetos"%nombre)
        #
        naturaleza.terminar()
        #
        lod0=NodePath(LODNode("%s_lod"%nombre))
        lod0.node().addSwitch(*self.switch_lod_naturaleza)
        nodo.reparentTo(lod0)
        #
        return lod0

    def _establecer_shader(self):
        #
        ruta_tex_ruido="texturas/white_noise.png"
        tamano=512
        if not os.path.exists(ruta_tex_ruido):
            imagen_ruido=PNMImage(tamano+1, tamano+1)
            for x in range(tamano+1):
                for y in range(tamano+1):
                    a=random.random()
                    imagen_ruido.setXel(x, y, a, a, a)
            imagen_ruido.write(ruta_tex_ruido)
        #
        ts0=TextureStage("ts_terreno")
        textura_terreno=self.base.loader.loadTexture("texturas/terreno2.png")
        self.nodo_parcelas.setTexture(ts0, textura_terreno, priority=2)
        #
        ts1=TextureStage("ts_ruido")
        textura_ruido=self.base.loader.loadTexture(ruta_tex_ruido)
        self.nodo_parcelas.setTexture(ts1, textura_ruido, priority=2)
        #
        GeneradorShader.aplicar(self.nodo_parcelas, GeneradorShader.ClaseTerreno, 2)
        GeneradorShader.aplicar(self.nodo_naturaleza, GeneradorShader.ClaseGenerico, 2)

    def _calcular_normal(self, v0, v1, v2):
        U=v1-v0
        V=v2-v0
        return U.cross(V)
    
    def _generar_lineas_normales(self, nombre, geom_node_parcela):
        #
        nodo=self.base.render.attachNewNode(nombre)
        #
        geom_normales=LineSegs("%s_normales"%nombre)
        geom_normales.setColor((0, 0, 1, 1))
        geom_tangent=LineSegs("%s_tangent"%nombre)
        geom_tangent.setColor((1, 0, 1, 1))
        #
        geom_parcela=geom_node_parcela.getGeom(0)
        vdata=geom_parcela.getVertexData()
        v_reader=GeomVertexReader(vdata, InternalName.getVertex())
        n_reader=GeomVertexReader(vdata, InternalName.getNormal())
        t_reader=GeomVertexReader(vdata, InternalName.getTangent())
        #
        while(not v_reader.isAtEnd()):
            vertex=v_reader.getData3f()
            normal1=n_reader.getData3f()
            tangent=t_reader.getData4f()
            geom_normales.moveTo(vertex)
            geom_normales.drawTo(vertex+normal1)
            geom_tangent.moveTo(vertex+normal1)
            geom_tangent.drawTo(vertex+Vec3(tangent[0], tangent[1], tangent[2]))
        #
        nodo.attachNewNode(geom_normales.create())
        nodo.attachNewNode(geom_tangent.create())
        return nodo

#
# DATOS LOCALES TERRENO
#
class DatosLocalesTerreno:
    
    def __init__(self):
        #
        self.index=None # vertex array index
        self.pos=None
        self.tc=None
        self.normal=None
        self.tangent=None
        self.binormal=None
        self.tipo=Vec3(0.0, 0.0, 0.0) # Vec3(tipo_terreno_0,tipo_terreno_1,factor_transicion)
        self.precipitacion_frecuencia=0.0 # 
    
    def __str__(self):
        return "DatosLocalesTerreno: i=%s; pos=%s; tc=%s; normal=%s; tan=%s; bn=%s; tipo=%s; prec_f=%.3f"%(str(self.index), str(self.pos), str(self.tc), str(self.normal), str(self.tangent), str(self.binormal), self.tipo, self.precipitacion_frecuencia)

#
# TESTER
#
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
import random
import os, os.path
class Tester(ShowBase):

    TipoImagenNulo=0
    TipoImagenTopo=1
    TipoImagenRuido=2
    TipoImagenRuidoContinuo=3
    TipoImagenBlendTerrenosBase=4
    TipoImagenBlendTerreno=5

    def __init__(self):
        #
        super(Tester, self).__init__()
        self.disableMouse()
        self.win.setClearColor(Vec4(0.95, 1.0, 1.0, 1.0))
        #
        bullet_world=BulletWorld()
        #
        self.cam_pitch=30.0
        self.escribir_archivo=False # cada update
        #
        config.iniciar()
        self.sistema=sistema.Sistema()
        self.sistema.iniciar()
        sistema.establecer_instancia(self.sistema)
        #
        GeneradorShader.iniciar(self, sistema.Sistema.TopoAltitudOceano, Vec4(0, 0, 1, sistema.Sistema.TopoAltitudOceano))
        GeneradorShader.aplicar(self.render, GeneradorShader.ClaseGenerico, 1)
        self.render.setShaderInput("distancia_fog_maxima", 3000.0, 0, 0, 0, priority=3)
        #
        self.terreno=Terreno(self, bullet_world)
        self.terreno.iniciar()
        #self.terreno.nodo.setRenderModeWireframe()
        #
        plano=CardMaker("plano_agua")
        r=Terreno.TamanoParcela*6
        plano.setFrame(-r, r, -r, r)
        plano.setColor((0, 0, 1, 1))
        self.plano_agua=self.render.attachNewNode(plano.generate())
        self.plano_agua=self.loader.loadModel("objetos/plano_agua")
        self.plano_agua.reparentTo(self.render)
        self.plano_agua.setScale(0.5)
        #self.plano_agua.setP(-90.0)
        #self.plano_agua.hide()
        #
        self.cam_driver=self.render.attachNewNode("cam_driver")
        self.camera.reparentTo(self.cam_driver)
        self.camera.setPos(Terreno.TamanoParcela/2, 500, 100)
        self.camera.lookAt(self.cam_driver)
        self.cam_driver.setP(self.cam_pitch)
        #
        self.luz_ambiental=self.render.attachNewNode(AmbientLight("luz_ambiental"))
        self.luz_ambiental.node().setColor(Vec4(0, 1, 1, 1))
        #
        self.sun=self.render.attachNewNode(DirectionalLight("sun"))
        self.sun.node().setColor(Vec4(1, 1, 1, 1))
        self.sun.setPos(self.terreno.nodo, 100, 100, 100)
        self.sun.lookAt(self.terreno.nodo)
        #
        self.render.setLight(self.luz_ambiental)
        #self.render.setLight(self.sun)
        #
        self.texturaImagen=None
        self.imagen=None
        self.zoom_imagen=1
        #
        self.tipo_imagen=Tester.TipoImagenBlendTerrenosBase
        #
        self.taskMgr.add(self.update, "update")
        self.accept("wheel_up", self.zoom, [1])
        self.accept("wheel_down", self.zoom, [-1])
        #
        self._cargar_ui()
        #self._actualizar_terreno()
        self._generar_imagen()
        
    def update(self, task):
        nueva_pos_foco=Vec3(self.sistema.posicion_cursor)
        #
        mwn=self.mouseWatcherNode
        if mwn.isButtonDown(KeyboardButton.up()):
            nueva_pos_foco[1]-=32
        elif mwn.isButtonDown(KeyboardButton.down()):
            nueva_pos_foco[1]+=32
        elif mwn.isButtonDown(KeyboardButton.left()):
            nueva_pos_foco[0]+=32
        elif mwn.isButtonDown(KeyboardButton.right()):
            nueva_pos_foco[0]-=32
        #
        if nueva_pos_foco!=self.sistema.posicion_cursor:
            log.info("update pos_foco=%s"%str(nueva_pos_foco))
            self.sistema.posicion_cursor=nueva_pos_foco
            self._actualizar_terreno()
        return task.cont
    
    def zoom(self, dir):
        dy=25*dir
        self.camera.setY(self.camera, dy)

    def analizar_altitudes(self, pos_foco, tamano=1024):
        log.info("analizar_altitudes en %ix%i"%(tamano, tamano))
        i=0
        media=0
        vals=list()
        min=999999
        max=-999999
        for x in range(tamano):
            for y in range(tamano):
                a=self.terreno.sistema.obtener_altitud_suelo((pos_foco[0]+x, pos_foco[1]+y))
                vals.append(a)
                if a>max:
                    max=a
                if a<min:
                    min=a
                media=((media*i)+a)/(i+1)
                i+=1
        sd=0
        for val in vals:  sd+=((val-media)*(val-media))
        sd/=(tamano*tamano)
        sd=math.sqrt(sd)
        log.info("analizar_altitudes rango:[%.3f/%.3f] media=%.3f sd=%.3f"%(min, max, media, sd))

    def _actualizar_terreno(self):
        log.info("_actualizar_terreno pos=%s"%(str(self.sistema.posicion_cursor)))
        #
        self.terreno.update()
        if self.escribir_archivo:
            log.info("escribir_archivo")
            self.terreno.nodo.writeBamFile("terreno.bam")
        self.plano_agua.setPos(Vec3(self.sistema.posicion_cursor[0], self.sistema.posicion_cursor[1], Sistema.TopoAltitudOceano))
        #
        self.cam_driver.setPos(Vec3(self.sistema.posicion_cursor[0]+Terreno.TamanoParcela/2, self.sistema.posicion_cursor[1]-Terreno.TamanoParcela, Sistema.TopoAltitudOceano))
        #
        self.lblInfo["text"]=self.terreno.obtener_info()
        #
        self._generar_imagen()

    def _ruido(self, position, imagen_ruido, tamano_imagen_ruido):
        octaves=8
        persistance=0.55
        value=0.0
        amplitude=1.0
        total_amplitude=0.0
        for i_octave in range(octaves):
            amplitude*=persistance
            total_amplitude+=amplitude
            period=1<<(octaves-i_octave)
            offset_periodo_x, cant_periodos_x=math.modf(position[0]/period)
            offset_periodo_y, cant_periodos_y=math.modf(position[1]/period)
            periodo_x0=(cant_periodos_x*period)%tamano_imagen_ruido
            periodo_y0=(cant_periodos_y*period)%tamano_imagen_ruido
            periodo_x1=(periodo_x0+period)%tamano_imagen_ruido
            periodo_y1=(periodo_y0+period)%tamano_imagen_ruido
            c00=imagen_ruido.getGray(int(periodo_x0), int(periodo_y0))
            c10=imagen_ruido.getGray(int(periodo_x1), int(periodo_y0))
            c01=imagen_ruido.getGray(int(periodo_x0), int(periodo_y1))
            c11=imagen_ruido.getGray(int(periodo_x1), int(periodo_y1))
            interp_x0=(c00*(1.0-offset_periodo_x))+(c10*offset_periodo_x)
            interp_x1=(c01*(1.0-offset_periodo_x))+(c11*offset_periodo_x)
            interp_y=(interp_x0*(1.0-offset_periodo_y))+(interp_x1*offset_periodo_y)
            value+=interp_y*amplitude
            #info="_ruido\tposition=%s tamano_imagen_ruido=%i i_octave=%i periodo=%i offset_periodo=%s\n"%(str(position), tamano_imagen_ruido, i_octave, period, str((offset_periodo_x, offset_periodo_y)))
            #info+="\tpx0=%.1f px1=%.1f offset_x=%.2f py0=%.1f py1=%.1f offset_y=%.2f interp_y=%.3f"%(periodo_x0, periodo_x1, offset_x, periodo_y0, periodo_y1, offset_y, interp_y)
            #print(info)
            #print("cxx=%s a=%.4f p=%i v=%.4f"%(str((c00, c10, c01, c11)), amplitude, period, value))
        if total_amplitude>1.0:
            value/=total_amplitude
        return value

    def _limpiar_imagen(self):
        if self.imagen:
            self.texturaImagen.releaseAll()
            self.texturaImagen.clear()
            self.texturaImagen=None
            self.imagen.clear()
            self.imagen=None

    def _generar_imagen(self):
        log.info("_generar_imagen")
        self._limpiar_imagen()
        if self.tipo_imagen==Tester.TipoImagenTopo:
            self._generar_imagen_topo()
        elif self.tipo_imagen==Tester.TipoImagenRuido:
            self._generar_imagen_ruido()
        elif self.tipo_imagen==Tester.TipoImagenRuidoContinuo:
            self._generar_imagen_ruido_continuo()
        elif self.tipo_imagen==Tester.TipoImagenBlendTerrenosBase:
            self._generar_imagen_blend_terreno_base()
        elif self.tipo_imagen==Tester.TipoImagenBlendTerreno:
            self._generar_imagen_blend_terreno()

    def _generar_imagen_blend_terreno_base(self):
        log.info("_generar_imagen_blend_terreno_base")
        #
        idx_pos=self.terreno.obtener_indice_parcela(self.sistema.posicion_cursor)
        log.info("idx_pos=%s"%str(idx_pos))
        ruta_archivo_textura="texturas/terreno/tester_%i_%i.png"%(idx_pos[0], idx_pos[1])
        log.info("ruta_archivo_textura=%s"%ruta_archivo_textura)
        if os.path.exists(ruta_archivo_textura):
            log.warning("se elimina archivo previo")
            os.remove(ruta_archivo_textura)
        #
        tamano=int(Terreno.TamanoParcela/4)
        #
        if not self.imagen:
            type=PNMFileTypeRegistry.getGlobalPtr().getTypeFromExtension("png")
            self.imagen=PNMImage(tamano, tamano, 4, 255, type, CS_linear)
            self.texturaImagen=Texture()
            self.frmImagen["image"]=self.texturaImagen
            self.frmImagen["image_scale"]=0.4
        #
        x0=math.floor(self.sistema.posicion_cursor[0]/tamano)*tamano
        y0=math.floor(self.sistema.posicion_cursor[1]/tamano)*tamano
        for x in range(tamano):
            for y in range(tamano):
                posicion=(x0+(x*Terreno.TamanoParcela/tamano), y0+(y*Terreno.TamanoParcela/tamano), 0.0)
                tipo_terreno_0, tipo_terreno_1, factor_transicion=self.sistema.obtener_tipo_terreno(posicion)
                tipo=tipo_terreno_0 if factor_transicion<0.5 else tipo_terreno_1
                tipo/=10.0
                self.imagen.setXelA(x, y, tipo, tipo, tipo, 1.0)
        #
        self.imagen.write(ruta_archivo_textura)
        log.info("archivo de imagen escrito")
        #
        self.texturaImagen.load(self.imagen)

    def _generar_imagen_blend_terreno(self):
        log.info("_generar_imagen_blend_terreno")
        #
        idx_pos=self.terreno.obtener_indice_parcela(self.sistema.posicion_cursor)
        log.info("idx_pos=%s"%str(idx_pos))
        ruta_archivo_textura="texturas/terreno/tester_%i_%i.png"%(idx_pos[0], idx_pos[1])
        log.info("ruta_archivo_textura=%s"%ruta_archivo_textura)
        if not os.path.exists(ruta_archivo_textura):
            log.warning("el archivo no existe, se lo creara...")
            self._generar_imagen_blend_terreno_base()
            self._limpiar_imagen()
            log.info("...continua")
        #
        imagen_ruido=PNMImage(ruta_archivo_textura)
        tamano_imagen_ruido=imagen_ruido.getReadXSize()
        #
        tamano=Terreno.TamanoParcela*4
        #
        if not self.imagen:
            type=PNMFileTypeRegistry.getGlobalPtr().getTypeFromExtension("*.png")
            self.imagen=PNMImage(tamano, tamano, 4, 255, type, CS_linear)
            self.texturaImagen=Texture()
            self.frmImagen["image"]=self.texturaImagen
            self.frmImagen["image_scale"]=0.4
        #
        cant_total, cant_calc_ext, cant_mezcla=0, 0, 0
        for x in range(tamano):
            for y in range(tamano):
                pos_parcela_x=x*(tamano_imagen_ruido-1)/tamano
                pos_parcela_y=y*(tamano_imagen_ruido-1)/tamano
                fract_x, entero_x=math.modf(pos_parcela_x)
                fract_y, entero_y=math.modf(pos_parcela_y)
                fract_x_rnd=round(fract_x)
                fract_y_rnd=round(fract_y)
                proximo_x=int(entero_x+fract_x_rnd)
                proximo_y=int(entero_y+fract_y_rnd)
                dist_proximo=math.sqrt((fract_x_rnd-fract_x)**2+(fract_y_rnd-fract_y)**2)
                texel_a=math.floor(imagen_ruido.getXelA(proximo_x, proximo_y)[0]*10.0)
                color=Sistema.ColoresTipoTerreno[texel_a]/255
                print("posp=%s e/f=%s prox=%s distp=%.2f tx=%s (%s)"%(str((pos_parcela_x, pos_parcela_y)), 
                                                                      str(((entero_x, fract_x), (entero_y, fract_y))), 
                                                                      str((proximo_x, proximo_y)), 
                                                                      dist_proximo, 
                                                                      str(texel_a), str(color)
                                                               ))
                if dist_proximo>0.25:
                    fract_x_rnd_op, fract_y_rnd_op=(fract_x_rnd+1)%2, (fract_y_rnd+1)%2
                    siguiente_x, siguiente_y, dist_siguiente=0, 0, 0.0
                    # b
                    dist_siguiente=math.sqrt((fract_x_rnd_op-fract_x)**2+(fract_y_rnd-fract_y)**2)
                    siguiente_x, siguiente_y=int(entero_x+fract_x_rnd_op), int(entero_y+fract_y_rnd)
                    info=" sgte=%s dists=%.2f "%(str((siguiente_x, siguiente_y)), dist_siguiente)
                    # c
                    dist_c=math.sqrt((fract_x_rnd-fract_x)**2+(fract_y_rnd_op-fract_y)**2)
                    if dist_c<dist_siguiente:
                        dist_siguiente=dist_c
                        siguiente_x, siguiente_y=int(entero_x+fract_x_rnd), int(entero_y+fract_y_rnd_op)
                    info+="sgte=%s dist_c=%.2f "%(str((siguiente_x, siguiente_y)), dist_c)
                    # d
                    dist_d=math.sqrt((fract_x_rnd_op-fract_x)**2+(fract_y_rnd_op-fract_y)**2)
                    if dist_d<dist_siguiente:
                        dist_siguiente=dist_d
                        siguiente_x, siguiente_y=int(entero_x+fract_x_rnd_op), int(entero_y+fract_y_rnd_op)
                    info+="sgte=%s dist_d=%.2f "%(str((siguiente_x, siguiente_y)), dist_d)
                    #
                    texel_2=math.floor(imagen_ruido.getXelA(siguiente_x, siguiente_y)[0]*10.0)
                    cant_calc_ext+=1
                    if texel_a!=texel_2:
                        factor_transicion=(dist_siguiente/(dist_proximo+dist_siguiente))
                        color=(color*(factor_transicion))+((Sistema.ColoresTipoTerreno[texel_2]/255)*(1.0-factor_transicion))
                        cant_mezcla+=1
                        info+="texel_2(%s)=%s factor_transicion=%.3f c=%s"%(str((siguiente_x, siguiente_y)), str(texel_2), factor_transicion, str(color))
                    print(info)
                cant_total+=1
                self.imagen.setXelA(x, y, color)
        print("cant_total=%i; cant_calc_ext=%i(%.2fpct); cant_mezcla=%i(%.2fpct)"%(cant_total, cant_calc_ext, cant_calc_ext*100/cant_total, cant_mezcla, cant_mezcla*100/cant_total))
        #
        imagen_ruido.clear()
        #
        if os.path.exists("tipo_terreno.png"):
            os.remove("tipo_terreno.png")
        self.imagen.write("tipo_terreno.png")
        log.info("archivo de imagen escrito")
        #
        self.texturaImagen.load(self.imagen)
        
    def _generar_imagen_ruido_continuo(self):
        log.info("_generar_imagen_ruido_continuo")
        #
        tamano=512
        #
        perlin_noise_scale=64
        perlin=StackedPerlinNoise2(perlin_noise_scale, perlin_noise_scale, 8, 2.0, 0.50, 256, 1069)
        #
        if not self.imagen:
            type=PNMFileTypeRegistry.getGlobalPtr().getTypeFromExtension("*.png")
            self.imagen=PNMImage(tamano, tamano, 4, 255, type, CS_linear)
            self.texturaImagen=Texture()
            self.frmImagen["image"]=self.texturaImagen
            self.frmImagen["image_scale"]=0.4
        #
        zoom=self.zoom_imagen
        log.info("zoom: %.2f"%(zoom))
        range_x, range_y=tamano, tamano
        factor_x, factor_y=range_x/tamano, range_y/tamano
        for x in range(tamano):
            for y in range(tamano):
                _x=x*factor_x
                _y=y*factor_y
                c00=perlin(_x,                  _y                  )
                c10=perlin((_x+range_x)        ,_y                  )
                c01=perlin(_x,                  (_y+range_y)        )
                c11=perlin((_x+range_x)        ,(_y+range_y)        )
                mix_x, mix_y=1.0-_x/range_x, 1.0-_y/range_y
                if mix_x<0.0 or mix_y<0.0 or mix_x>1.0 or mix_y>1.0:
                    print("error mix_x,mix_y")
                interp_x0=(c00*(1.0-mix_x))+(c10*mix_x)
                interp_x1=(c01*(1.0-mix_x))+(c11*mix_x)
                interp_y=(interp_x0*(1.0-mix_y))+(interp_x1*mix_y)
                interp_y=interp_y*0.5+0.5
                interp_y=interp_y if interp_y<1.0 else 1.0
                interp_y=interp_y if interp_y>0.0 else 0.0
                c=interp_y
                if c<0.0 or c>1.0:
                    print("error c")
                self.imagen.setXelA(x, y, c, c, c, 1.0)
        #
        self.imagen.write("texturas/white_noise.png")
        image_tiled=PNMImage(2*tamano, 2*tamano)
        image_tiled.copySubImage(self.imagen, 0,      0,      0, 0, tamano, tamano)
        image_tiled.copySubImage(self.imagen, tamano, 0,      0, 0, tamano, tamano)
        image_tiled.copySubImage(self.imagen, 0,      tamano, 0, 0, tamano, tamano)
        image_tiled.copySubImage(self.imagen, tamano, tamano, 0, 0, tamano, tamano)
        self.imagen.clear()
        self.imagen=None
        self.imagen=image_tiled
        self.texturaImagen.load(self.imagen)

    def _generar_imagen_ruido(self):
        # http://devmag.org.za/2009/04/25/perlin-noise/
        log.info("_generar_imagen_ruido")
        return
        #
        tamano=128
        #
        if not self.imagen:
            self.imagen=PNMImage(tamano+1, tamano+1)
            self.texturaImagen=Texture()
            self.frmImagen["image"]=self.texturaImagen
            self.frmImagen["image_scale"]=0.4
        #
        zoom=self.zoom_imagen
        log.info("zoom: %.2f"%(zoom))        
        imagen_ruido=PNMImage("texturas/white_noise.png")
        n=0
        vals=list()
        tamano_imagen_ruido=imagen_ruido.getReadXSize()
        for x in range(tamano_imagen_ruido):
            vals.append(list())
            for y in range(tamano_imagen_ruido):
                _x=self.sistema.posicion_cursor[0]+zoom*(tamano/2.0)-zoom*x
                _y=self.sistema.posicion_cursor[1]-zoom*(tamano/2.0)+zoom*y
                a=self._ruido((_x, _y), imagen_ruido, tamano_imagen_ruido)
                vals[x].append(a)
                n+=1
        media=0.0
        sd=0.0
        for fila in vals:
            for val in fila:
                media+=val
        media/=n
        for fila in vals:
            for val in fila:
                sd+=(val-media)**2
        sd=math.sqrt(sd/(n-1))
        vals2=list()
        k=7
        for x in range(tamano_imagen_ruido):
            vals2.append(list())
            for y in range(tamano_imagen_ruido):
                val=vals[x][y]
                val-=(media-0.5)
                val+=(0.5-val)*(-(1.0+(2**k)*sd))
                val2=min(1.0, max(0.0, val))
                vals2[x].append(val2)
        for x in range(tamano_imagen_ruido):
            for y in range(tamano_imagen_ruido):
                self.imagen.setXel(x, y, vals2[x][y])
        print("_generar_imagen_ruido media=%.4f sd=%.4f"%(media, sd))
        #
        self.texturaImagen.load(self.imagen)

    def _generar_imagen_topo(self):
        log.info("_generar_imagen_topo")
        #
        tamano=128
        if not self.imagen:
            self.imagen=PNMImage(tamano+1, tamano+1)
            self.texturaImagen=Texture()
            self.frmImagen["image"]=self.texturaImagen
            self.frmImagen["image_scale"]=0.4
        #
        zoom=self.zoom_imagen
        log.info("zoom: %.2f"%(zoom))
        for x in range(tamano+1):
            for y in range(tamano+1):
                _x=self.sistema.posicion_cursor[0]+zoom*(tamano/2.0)-zoom*x
                _y=self.sistema.posicion_cursor[1]-zoom*(tamano/2.0)+zoom*y
                a=self.terreno.sistema.obtener_altitud_suelo((_x, _y))/Sistema.TopoAltura
                if x==tamano/2 or y==tamano/2:
                    self.imagen.setXel(x, y, 1.0)
                else:
                    if a>(Sistema.TopoAltitudOceano/Sistema.TopoAltura):
                        self.imagen.setXel(x, y, a, a, 0.0)
                    else:
                        self.imagen.setXel(x, y, 0.0, 0.0, a)
        #
        self.texturaImagen.load(self.imagen)

    def _ir_a_idx_pos(self):
        log.info("_ir_a_idx_pos")
        try:
            idx_x=int(self.entry_x.get())
            idx_y=int(self.entry_y.get())
            pos=self.terreno.obtener_pos_parcela((idx_x, idx_y))
            log.info("idx_pos:(%i,%i); pos:%s"%(idx_x, idx_y, str(pos)))
            self.sistema.posicion_cursor=Vec3(pos[0], pos[1], 0.0)
            self._actualizar_terreno()
        except Exception as e:
            log.exception(str(e))

    def _cargar_ui(self):
        # frame
        self.frame=DirectFrame(parent=self.aspect2d, pos=(0, 0, -0.85), frameSize=(-1, 1, -0.15, 0.25), frameColor=(1, 1, 1, 0.5))
        # info
        self.lblInfo=DirectLabel(parent=self.frame, pos=(-1, 0, 0.15), scale=0.05, text="info terreno?", frameColor=(1, 1, 1, 0.2), frameSize=(0, 40, -2, 2), text_align=TextNode.ALeft, text_pos=(0, 1, 1))
        # idx_pos
        DirectLabel(parent=self.frame, pos=(-1, 0, 0), scale=0.05, text="idx_pos_x", frameColor=(1, 1, 1, 0), frameSize=(0, 2, -1, 1), text_align=TextNode.ALeft)
        DirectLabel(parent=self.frame, pos=(-1, 0, -0.1), scale=0.05, text="idx_pos_y", frameColor=(1, 1, 1, 0), frameSize=(0, 2, -1, 1), text_align=TextNode.ALeft)
        self.entry_x=DirectEntry(parent=self.frame, pos=(-0.7, 0, 0), scale=0.05, initialText="0")
        self.entry_y=DirectEntry(parent=self.frame, pos=(-0.7, 0, -0.1), scale=0.05, initialText="0")
        DirectButton(parent=self.frame, pos=(0, 0, -0.1), scale=0.075, text="actualizar", command=self._ir_a_idx_pos)
        #
        self.frmImagen=DirectFrame(parent=self.frame, pos=(0.8, 0, 0.2), state=DGG.NORMAL, frameSize=(-0.4, 0.4, -0.4, 0.4))
        self.frmImagen.bind(DGG.B1PRESS, self._click_imagen)
        DirectButton(parent=self.frame, pos=(0.500, 0, 0.65), scale=0.1, text="acercar", command=self._acercar_zoom_imagen, frameSize=(-1, 1, -0.4, 0.4), text_scale=0.5)
        DirectButton(parent=self.frame, pos=(0.725, 0, 0.65), scale=0.1, text="alejar", command=self._alejar_zoom_imagen, frameSize=(-1, 1, -0.4, 0.4), text_scale=0.5)
        DirectButton(parent=self.frame, pos=(0.950, 0, 0.65), scale=0.1, text="cambiar", command=self._cambiar_tipo_imagen, frameSize=(-1, 1, -0.4, 0.4), text_scale=0.5)

    def _cambiar_tipo_imagen(self):
        log.info("_cambiar_tipo_imagen a:")
        if self.tipo_imagen==Tester.TipoImagenTopo:
            log.info("TipoImagenRuido")
            self.tipo_imagen=Tester.TipoImagenRuido
        elif self.tipo_imagen==Tester.TipoImagenRuido:
            log.info("TipoImagenRuidoContinuo")
            self.tipo_imagen=Tester.TipoImagenRuidoContinuo
        elif self.tipo_imagen==Tester.TipoImagenRuidoContinuo:
            log.info("TipoImagenBlendTerrenosBase")
            self.tipo_imagen=Tester.TipoImagenBlendTerrenosBase
        elif self.tipo_imagen==Tester.TipoImagenBlendTerrenosBase:
            log.info("TipoImagenBlendTerreno")
            self.tipo_imagen=Tester.TipoImagenBlendTerreno
        elif self.tipo_imagen==Tester.TipoImagenBlendTerreno:
            log.info("TipoImagenTopo")
            self.tipo_imagen=Tester.TipoImagenTopo
        self._generar_imagen()

    def _click_imagen(self, *args):
        log.info("_click_imagen %s"%str(args))

    def _acercar_zoom_imagen(self):
        log.info("_acercar_zoom_imagen")
        self.zoom_imagen-=4
        if self.zoom_imagen<1:
            self.zoom_imagen=1
        self._generar_imagen()

    def _alejar_zoom_imagen(self):
        log.info("_alejar_zoom_imagen")
        self.zoom_imagen+=4
        if self.zoom_imagen>4096:
            self.zoom_imagen=4096
        self._generar_imagen()

if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG)
    PStatClient.connect()
    Terreno.RadioExpansion=0
    tester=Tester()
    tester.terreno.dibujar_normales=False
    tester.escribir_archivo=False
    tester.run()
