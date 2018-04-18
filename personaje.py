from direct.actor.Actor import Actor
from panda3d.bullet import *
from panda3d.core import *
import os, os.path

from sistema import Sistema
from shader import GestorShader

import logging
log=logging.getLogger(__name__)

#
#
# PERSONAJE
#
#
class Personaje:
    
    # suelo
    SueloNulo=0
    SueloGenerico=1
    SueloEscalera=2
    SueloPendienteSubida=3
    SueloPendienteBajada=4

#    # estados
    EstadoNulo=0
    EstadoQuieto=1
    EstadoClaseDerivadaBase=100

    # parametros de estados
    ParamEstadoNulo=0

    def __init__(self, clase):
        # variables internas
        self._suelo=self.SueloNulo
        self._partes_actor=list() # [] | [nombre_parte, ...]
        self._estado_capa=[self.EstadoNulo, self.EstadoNulo] # [estado,estado]
        self._params_estado=Personaje.ParamEstadoNulo
        self._altura=0.0
        self._velocidad_lineal=LVector3()
        self._velocidad_angular=LVector3() # grados
        self._ajuste_altura=0.0
        # variables externas
        self.altitud_suelo=0.0
        self.altitud_agua=0.0
        self.contactos=None # |list [BulletContact,...]
        self.objetos_estados=dict() # {Estado:NodePath,...}
        # parametros
        self.directorio_recursos="personajes"
        self.clase=clase
        self.prefijo_cuerpo_suelo="cuerpo_suelo_"
        self.prefijo_cuerpo_personaje="cuerpo_personaje_"
        self.rapidez_caminar=1.0 # multiplicador
        self.rapidez_correr=2.0 # multiplicador
        # referencias
        self.sistema=None
        self.input_mapper=None
        self.bullet_world=None
        # componentes
        self.cuerpo=None
        self.actor=None
    
    def iniciar(self, parent_node_path, bullet_world, partes=list()):
        log.info("iniciar")
        # sistema
        self.sistema=Sistema.obtener_instancia()
        # recursos
        ruta_dir=os.path.join(os.getcwd(), self.directorio_recursos, self.clase)
        if not os.path.exists(ruta_dir):
            raise Exception("no existe el directorio '%s'"%(ruta_dir))
        archivos=[archivo for archivo in os.listdir(ruta_dir) if archivo[-4:].lower()==".egg" or archivo[-4:].lower()==".bam"]
        archivo_actor=""
        dict_animaciones=dict()
        for archivo in archivos:
            if archivo[:-4]=="actor":
                archivo_actor=archivo
            else:
                dict_animaciones[archivo[:-4]]=Filename.fromOsSpecific(os.path.join(ruta_dir, archivo))
        if archivo_actor=="":
            raise Exception("no se encontró ningún archivo de actor (actor.[egg|bam]) en '%s'"%ruta_dir)
        # cuerpo
        self.bullet_world=bullet_world
        rb=self._generar_cuerpo_fisica()
        self.bullet_world.attach(rb)
        self.cuerpo=parent_node_path.attachNewNode(rb)
        self.cuerpo.setCollideMask(BitMask32.bit(2))
        # actor
        self.actor=Actor(Filename.fromOsSpecific(os.path.join(ruta_dir, archivo_actor)), dict_animaciones)
        self.actor.reparentTo(self.cuerpo)
        self.actor.setZ(-self._ajuste_altura)
        # partes
        for parte in partes:
            self.actor.makeSubpart(parte[0], parte[1], parte[2])
            self._partes_actor.append(parte[0])
        # shader
        GestorShader.aplicar(self.actor, GestorShader.ClasePersonaje, 2)
    
    def terminar(self):
        log.info("terminar")
        self.sistema=None
        self.actor.delete()
        self.bullet_world.remove(self.cuerpo.node())
        self.actor=None
        self.cuerpo=None
        self.input_mapper=None
        self.bullet_world=None
    
    def setPos(self, posicion):
        _posicion=Vec3(posicion[0], posicion[1], posicion[2]+self._ajuste_altura)
        self.cuerpo.setPos(_posicion)

    def chequear_estado(self, estado, idx_capa):
        if idx_capa==1: # capa 1
            return (self._estado_capa[1]&estado)==estado
        elif idx_capa==0: # capa 0
            return estado==self._estado_capa[0]
    
    def update(self, dt):
        if self._estado_capa[0]!=Personaje.EstadoQuieto:
            # altitud suelo
            self.altitud_suelo=self.sistema.obtener_altitud_suelo(self.cuerpo.getPos())
            # definir ambiente y suelo
            self._definir_suelo()
            # altura desde el suelo (se encuentra al final para ser evaluada en forma porterior)
            self._altura=self.cuerpo.getZ()-self.altitud_suelo-self._ajuste_altura#|0.5
        # definir estados
        for idx_capa in range(len(self._estado_capa)):
            estado_nuevo=self._definir_estado(idx_capa)
            if self._estado_capa[idx_capa]!=estado_nuevo:
                # procesar cambio de estado
                self._cambio_estado(idx_capa, self._estado_capa[idx_capa], estado_nuevo)
                self._estado_capa[idx_capa]=estado_nuevo
        # verificar cambio de parametros
        param_estado_nuevo=self.input_mapper.parametros
        if self._params_estado!=param_estado_nuevo:
            # procesar cambio en parametros
            self._cambio_params(self._params_estado, param_estado_nuevo)
            self._params_estado=param_estado_nuevo
        # procesar estados
        self._procesar_estados(dt)
        # contactos
        self._procesar_contactos()

    def obtener_info(self):
        info="Personaje:BulletRigidBodyNode vl=%s va=%s\n"%(str(self.cuerpo.node().getLinearVelocity()), str(self.cuerpo.node().getAngularVelocity()))
        info+="velocidad_lineal=%s velocidad_angular=%s\n"%(str(self._velocidad_lineal), str(self._velocidad_angular))
        info+="posicion=%s altitud_suelo=%s altura=%s\n"%(str(self.cuerpo.getPos()), str(self.altitud_suelo), str(self._altura))
        info+="ambiente=? suelo=%s\n"%(str(self._suelo))
        info+="estado=%s params=%s\n"%(str(self._estado_capa), str(self._params_estado))
        if self.contactos:
            info+="contactos=%s\n"%(str([c.getNode1().getName() for c in self.contactos]))
        if len(self.objetos_estados)>0:
            info+="objetos_estados=%s\n"%("; ".join(["%i %s"%(e, np.getName()) for e, np in self.objetos_estados.items()]))
        return info

    def _definir_suelo(self):
        if self._suelo!=Personaje.SueloNulo and self._altura>0.5:
            self._suelo=Personaje.SueloNulo
        elif self._suelo==Personaje.SueloNulo and self._altura<0.05:
            self._suelo=Personaje.SueloGenerico

    def _generar_cuerpo_fisica(self):
        log.warning("_generar_cuerpo_fisica no implementado (%s)"%self.clase)
        return None

    def _definir_estado(self, idx_capa):
        log.warning("_definir_estado no implementado (%s)"%self.clase)
        pass
    
    def _cambio_estado(self, idx_capa, estado_previo, estado_nuevo):
        log.warning("_cambio_estado no implementado (%s)"%self.clase)

    def _cambio_params(self, params_previos, params_nuevos):
        log.warning("_cambio_params no implementado (%s)"%self.clase)
        pass

    def _procesar_estados(self, dt):
        log.warning("_procesar_estados no implementado (%s)"%self.clase)
        pass

    def _procesar_contactos(self):
        log.warning("_procesar_contactos no implementado (%s)"%self.clase)
        pass

    def _contacto_iniciado(self, contacto):
        log.debug("_contacto_iniciado %s %s"%(self.clase, contacto.getNode1().getName()))
        log.warning("_contacto_iniciado no implementado (%s)"%self.clase)
        pass
    
    def _contacto_finalizado(self, contacto):
        log.debug("_contacto_finalizado %s %s"%(self.clase, contacto.getNode1().getName()))
        log.warning("_contacto_finalizado no implementado (%s)"%self.clase)
        pass

    def _agarrar(self):
        log.warning("_agarrar no implementado (%s)"%self.clase)
        return False
    
    def _soltar(self):
        log.warning("_soltar no implementado (%s)"%self.clase)
        return False

    def _usar(self, nodo_objeto):
        log.warning("_usar no implementado (%s)"%self.clase)
        return False
