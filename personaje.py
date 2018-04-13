from direct.actor.Actor import Actor
from panda3d.bullet import *
from panda3d.core import *
import os, os.path

#from input import InputMapper # pasa a Hombre
from shader import GestorShader

import logging
log=logging.getLogger(__name__)

#
#
# PERSONAJE
#
#
class Personaje:
    
##    ELIMINAR
#    # ambiente
#    AmbienteNulo=0
#    AmbienteAire=1
#    AmbienteAgua=2
    
    # suelo
    SueloNulo=0
    SueloGenerico=1
    SueloEscalera=2
    SueloPendienteSubida=3
    SueloPendienteBajada=4

#    # estados
    EstadoNulo=0
    EstadoClaseDerivadaBase=100

    # parametros de estados
    ParamEstadoNulo=0

##    pasa a Hombre
#    # capa 0; un solo estado
#    EstadoQuieto=1
#    EstadoCaminando=2
#    EstadoCorriendo=3
#    EstadoSaltando=4
#    EstadoFlotando=5
#    EstadoDescendiendo=6
#    EstadoCayendo=7
#    EstadoConduciendo=8
#    # capa 1; estado0|estado1|...
#    EstadoAgachado=1
#    EstadoAgarrando=2
#    EstadoUsando=4
#    
#    # parametros de estados
#    ParamEstadoNulo=0
#    ParamEstadoAdelante=1
#    ParamEstadoAtras=2
#    ParamEstadoIzquierda=4
#    ParamEstadoDerecha=8
#    ParamEstadoArriba=16
#    ParamEstadoAbajo=32
#    ParamEstadoGirando=64

    def __init__(self, clase):
        # variables internas
#        self._ambiente=self.AmbienteNulo ELIMINAR
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
        self.input_mapper=None
        self.bullet_world=None
        # componentes
        self.cuerpo=None
        self.actor=None
    
    def iniciar(self, parent_node_path, bullet_world, partes=list()):
        log.info("iniciar")
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
            #log.debug("chequear_estado e1=%s e2=%s"%(str(self._estado_capa[1]), str(estado)))
            return (self._estado_capa[1]&estado)==estado
        elif idx_capa==0: # capa 0
            return estado==self._estado_capa[0]
    
    def update(self, dt):
        # definir ambiente y suelo
        #self._definir_ambiente() ELIMINAR
        self._definir_suelo()
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
        # altura desde el suelo (se encuentra al final para ser evaluada en forma porterior)
        self._altura=self.cuerpo.getZ()-self.altitud_suelo-self._ajuste_altura#|0.5
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

##    ELIMINAR
#    def _definir_ambiente(self):
#        if self._ambiente != Personaje.AmbienteAire:
#            self._ambiente=Personaje.AmbienteAire
    
    def _generar_cuerpo_fisica(self):
        log.warning("_generar_cuerpo_fisica no implementado (%s)"%self.clase)
        return None
##        pasa a Hombre
#        shp=BulletCapsuleShape(0.25, 0.5, ZUp)
#        rb=BulletRigidBodyNode(self.prefijo_cuerpo_personaje+self.clase)
#        rb.setMass(70.0)
#        rb.addShape(shp)
#        rb.setKinematic(True)
#        self.bullet_world.attach(rb)
#        self._ajuste_altura=rb.getShapeBounds().getRadius()
#        return rb

    def _definir_estado(self, idx_capa):
        log.warning("_definir_estado no implementado (%s)"%self.clase)
        pass
##        pasa a Hombre
#        #
#        estado_actual=self._estado_capa[idx_capa]
#        estado_nuevo=estado_actual
#        # capa 0
#        if idx_capa==0:
#            # quieto
#            if estado_actual==Personaje.EstadoQuieto:
#                #->caminar
#                if self.input_mapper.accion==InputMapper.AccionAvanzar:
#                    estado_nuevo=Personaje.EstadoCaminando
#                    #->correr
#                    if self.input_mapper.parametro(InputMapper.ParametroRapido):
#                        estado_nuevo=Personaje.EstadoCorriendo
#                #->saltar
#                elif self.input_mapper.accion==InputMapper.AccionAscender:
#                    estado_nuevo=Personaje.EstadoSaltando
#            # caminando,corriendo
#            elif estado_actual==Personaje.EstadoCaminando or estado_actual==Personaje.EstadoCorriendo:
#                #caminar<->correr
#                estado_nuevo=Personaje.EstadoCorriendo if self.input_mapper.parametro(InputMapper.ParametroRapido) else Personaje.EstadoCaminando
#                #->quieto
#                if self.input_mapper.accion!=InputMapper.AccionAvanzar:
#                    estado_nuevo=Personaje.EstadoQuieto
#                #->saltar
#                if self.input_mapper.accion==InputMapper.AccionAscender:
#                    estado_nuevo=Personaje.EstadoSaltando
#            # cayendo
#            elif estado_actual==Personaje.EstadoCayendo:
#                if self._suelo!=Personaje.SueloNulo:
#                    estado_nuevo=Personaje.EstadoQuieto
#            #
#            # sin suelo
#            if self._suelo==Personaje.SueloNulo:
#                estado_nuevo=Personaje.EstadoCayendo
#        # capa 1
#        elif idx_capa==1:
#            # (cualquiera, con contactos)
#            if self.contactos:
#                #->agarrar
#                if self.input_mapper.accion==InputMapper.AccionAgarrar:
#                    if self._agarrar():
#                        estado_nuevo|=Personaje.EstadoAgarrando
#            # agarrando
#            if self.chequear_estado(Personaje.EstadoAgarrando, 1):
#                #->soltar
#                if self.input_mapper.accion==InputMapper.AccionSoltar or Personaje.EstadoAgarrando not in self.objetos_estados:
#                    if self._soltar():
#                        estado_nuevo-=Personaje.EstadoAgarrando
#        return estado_nuevo
    
    def _cambio_estado(self, idx_capa, estado_previo, estado_nuevo):
        log.warning("_cambio_estado no implementado (%s)"%self.clase)
##        pasa a Hombre
#        log.info("%s: cambio de estado en capa %i, de %s a %s"%(self.clase, idx_capa, str(estado_previo), str(estado_nuevo)))
#        self.actor.stop() # ???
#        # capa 0
#        if idx_capa==0:
#            if estado_nuevo==Personaje.EstadoQuieto:
#                self._velocidad_lineal=LVector3(0.0, 0.0, 0.0)
#                self._velocidad_angular=LVector3(0.0, 0.0, 0.0)
#        # capa 1
#        elif idx_capa==1:
#            pass
#        #

    def _cambio_params(self, params_previos, params_nuevos):
        log.warning("_cambio_params no implementado (%s)"%self.clase)
        pass
##        pasa a Hombre
#        log.info("%s: cambio de parámetros de estados de %s a %s"%(self.clase, str(bin(params_previos)), str(bin(params_nuevos))))
#        # detener giro
#        if params_previos & Personaje.ParamEstadoGirando and not params_nuevos & Personaje.ParamEstadoGirando:
#            self._velocidad_angular=LVector3(0.0, 0.0, 0.0)

    def _procesar_estados(self, dt):
        log.warning("_procesar_estados no implementado (%s)"%self.clase)
        pass
##        pasa a Hombre
#        # capa 0
#        # caminando,corriendo
#        if self._estado_capa[0]==Personaje.EstadoCaminando or self._estado_capa[0]==Personaje.EstadoCorriendo:
#            param=self._params_estado
#            rapidez=self.rapidez_caminar if self._estado_capa[0]==Personaje.EstadoCaminando else self.rapidez_correr
#            signo_x=-1.0 if param & Personaje.ParamEstadoDerecha else 1.0
#            signo_y=-1.0 if param & Personaje.ParamEstadoAdelante else 1.0
#            self._velocidad_lineal=LVector3()
#            if param & Personaje.ParamEstadoIzquierda or param & Personaje.ParamEstadoDerecha:
#                self._velocidad_lineal.setX(rapidez * signo_x)
#            if param & Personaje.ParamEstadoAdelante or param & Personaje.ParamEstadoAtras:
#                self._velocidad_lineal.setY(rapidez * signo_y)
#            if param & Personaje.ParamEstadoGirando:
#                self._velocidad_angular=LVector3(0.0, 0.0, 60.0 * rapidez * signo_x)
#            self.cuerpo.setZ(self.altitud_suelo+self._ajuste_altura)
#        # saltando
#        elif self._estado_capa[0]==Personaje.EstadoSaltando:
#            self._velocidad_lineal.setZ(5.0)
#            self._velocidad_angular=LVector3(0.0, 0.0, 0.0)
#        # cayendo
#        elif self._estado_capa[0]==Personaje.EstadoCayendo:
#            delta_velocidad_lineal=LVector3(0.0, 0.0, -9.81) * dt
#            self._velocidad_lineal+=delta_velocidad_lineal
#            prox_delta_h=abs(delta_velocidad_lineal.getZ()*dt)
#            if delta_velocidad_lineal.getZ()<0.0 and self._altura<=prox_delta_h: # si cayendo y cerca del suelo
#                self.cuerpo.setZ(self.altitud_suelo+self._ajuste_altura)
#                self._velocidad_lineal.setZ(0.0)            
#        #
#        # mover, si no está quieto
#        if self._estado_capa[0]!=Personaje.EstadoQuieto:
#            self.cuerpo.setPos(self.cuerpo, self._velocidad_lineal * dt)
#            self.cuerpo.setH(self.cuerpo, self._velocidad_angular.getZ() * dt)
#        #

    def _procesar_contactos(self):
        log.warning("_procesar_contactos no implementado (%s)"%self.clase)
        pass
##        pasa a Hombre
#        # evaluar contactos actuales
#        test_contactos=self.bullet_world.contactTest(self.cuerpo.node())
#        # si no hay, vaciar lista y ejecutar eventos pertinentes
#        if test_contactos.getNumContacts()==0:
#            if self.contactos:
#                for contacto in self.contactos:
#                    self._contacto_finalizado(contacto)
#                self.contactos=None
#            return
#        # obtener contactos
#        contactos_actuales=test_contactos.getContacts()
#        # crear lista interna de contactos
#        if not self.contactos:
#            self.contactos=list()
#        # recopilar contactos nuevos (ineficiente?)
#        contactos_nuevos=list()
#        for contacto_actual in contactos_actuales:
#            encontrado=False
#            for contacto in self.contactos:
#                if contacto.getNode1()==contacto_actual.getNode1():
#                    encontrado=True
#                    break
#            if not encontrado:
#                contactos_nuevos.append(contacto_actual)
#        # listar contactos perdidos
#        contactos_perdidos=list()
#        for contacto in self.contactos:
#            encontrado=False
#            for contacto_actual in contactos_actuales:
#                if contacto_actual.getNode1()==contacto.getNode1():
#                    encontrado=True
#                    break
#            if not encontrado:
#                contactos_perdidos.append(contacto)
#        # actualizar lista interna de contactos
#        self.contactos=contactos_actuales
#        # ejecutar eventos
#        for contacto in contactos_nuevos:
#            self._contacto_iniciado(contacto)
#        for contacto in contactos_perdidos:
#            self._contacto_finalizado(contacto)
#        # garantizar inter-impenetrabilidad
#        for contacto in contactos_actuales:
#            nodo=contacto.getNode1()
#            if not nodo.isStatic():
#                continue
#            punto=contacto.getManifoldPoint()
#            normal=punto.getPositionWorldOnB()-punto.getPositionWorldOnA()
#            colisiones=Vec3()
#            dist=punto.getDistance()
#            if dist<0:
#                colisiones-=normal*dist
#            colisiones.setZ(0)
#            self.cuerpo.setPos(self.cuerpo.getPos()+colisiones)            

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
##        pasa a Hombre
#        if Personaje.EstadoAgarrando in self.objetos_estados:
#            del self.objetos_estados[Personaje.EstadoAgarrando]
        return False

    def _usar(self, nodo_objeto):
        log.warning("_usar no implementado (%s)"%self.clase)
##        pasa a Hombre
        return False
