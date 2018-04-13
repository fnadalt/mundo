from panda3d.core import *
from panda3d.bullet import *

from input import InputMapper
from personaje import Personaje

import logging
log=logging.getLogger(__name__)

class Hombre(Personaje):

    # partes
    Partes=[("torso", ["spine"], ["shoulder.R", "thigh.L", "thigh.R"]), 
            ("pelvis", ["main", "hips", "thigh.L", "thigh.R"], ["spine"]), 
            ("brazo.R", ["shoulder.R"], [])
            ]

    # estados
    # capa 0; un solo estado
    EstadoQuieto=1
    EstadoCaminando=2
    EstadoCorriendo=3
    EstadoSaltando=4
    EstadoFlotando=5
    EstadoDescendiendo=6
    EstadoCayendo=7
    EstadoConduciendo=8
    # capa 1; estado0|estado1|...
    EstadoAgachado=1
    EstadoAgarrando=2
    EstadoUsando=4
    
    # parametros de estados
    ParamEstadoAdelante=1
    ParamEstadoAtras=2
    ParamEstadoIzquierda=4
    ParamEstadoDerecha=8
    ParamEstadoArriba=16
    ParamEstadoAbajo=32
    ParamEstadoGirando=64

    def __init__(self):
        Personaje.__init__(self, "male")
    
    def iniciar(self, parent_node_path, bullet_world):
        Personaje.iniciar(self, parent_node_path, bullet_world, Hombre.Partes)
        # joints
        self.manoD=self.actor.exposeJoint(None, "modelRoot", "hand.R")
        self.manoI=self.actor.exposeJoint(None, "modelRoot", "hand.L")
        # actor
        self.actor.setScale(0.06)
        # establecer estado inicial Quieto
        self._estado_capa[0]=Hombre.EstadoQuieto
        self._cambio_estado(0, Personaje.EstadoNulo, Hombre.EstadoQuieto)

    def _generar_cuerpo_fisica(self):
        shp=BulletCapsuleShape(0.25, 0.5, ZUp)
        rb=BulletRigidBodyNode(self.prefijo_cuerpo_personaje+self.clase)
        rb.setMass(70.0)
        rb.addShape(shp)
        rb.setKinematic(True)
        self._ajuste_altura=rb.getShapeBounds().getRadius()
        return rb

    def _definir_estado(self, idx_capa):
        #
        estado_actual=self._estado_capa[idx_capa]
        estado_nuevo=estado_actual
        # capa 0
        if idx_capa==0:
            # quieto
            if estado_actual==Hombre.EstadoQuieto:
                #->caminar
                if self.input_mapper.accion==InputMapper.AccionAvanzar:
                    estado_nuevo=Hombre.EstadoCaminando
                    #->correr
                    if self.input_mapper.parametro(InputMapper.ParametroRapido):
                        estado_nuevo=Hombre.EstadoCorriendo
                #->saltar
                elif self.input_mapper.accion==InputMapper.AccionAscender:
                    estado_nuevo=Hombre.EstadoSaltando
                if Hombre.EstadoAgarrando in self.objetos_estados:
                    #-> conduciendo
                    nodo_objeto=self.objetos_estados[Hombre.EstadoAgarrando]
                    if nodo_objeto.getName().endswith("_nave"):
                        estado_nuevo=Hombre.EstadoConduciendo
            # caminando,corriendo
            elif estado_actual==Hombre.EstadoCaminando or estado_actual==Hombre.EstadoCorriendo:
                #caminar<->correr
                estado_nuevo=Hombre.EstadoCorriendo if self.input_mapper.parametro(InputMapper.ParametroRapido) else Hombre.EstadoCaminando
                #->quieto
                if self.input_mapper.accion!=InputMapper.AccionAvanzar:
                    estado_nuevo=Hombre.EstadoQuieto
                #->saltar
                if self.input_mapper.accion==InputMapper.AccionAscender:
                    estado_nuevo=Hombre.EstadoSaltando
            # cayendo
            elif estado_actual==Hombre.EstadoCayendo:
                if self._suelo!=Personaje.SueloNulo:
                    estado_nuevo=Hombre.EstadoQuieto
            # conduciendo
            elif estado_actual==Hombre.EstadoConduciendo:
                if not Hombre.EstadoAgarrando in self.objetos_estados:
                    #-> quieto
                    estado_nuevo=Hombre.EstadoQuieto
            #
            # sin suelo
            if self._suelo==Personaje.SueloNulo:
                estado_nuevo=Hombre.EstadoCayendo
        # capa 1
        elif idx_capa==1:
            # (cualquiera, con contactos)
            if self.contactos:
                #->agarrar
                if self.input_mapper.accion==InputMapper.AccionAgarrar:
                    if self._agarrar():
                        estado_nuevo|=Hombre.EstadoAgarrando
            # agarrando
            if self.chequear_estado(Hombre.EstadoAgarrando, 1):
                #->soltar
                if self.input_mapper.accion==InputMapper.AccionSoltar or Hombre.EstadoAgarrando not in self.objetos_estados:
                    if self._soltar():
                        estado_nuevo-=Hombre.EstadoAgarrando
        return estado_nuevo

    def _cambio_estado(self, idx_capa, estado_previo, estado_nuevo):
        #
        self.actor.stop() # ???
        # capa 0
        if idx_capa==0:
            if estado_nuevo==Hombre.EstadoQuieto:
                self._velocidad_lineal=LVector3(0.0, 0.0, 0.0)
                self._velocidad_angular=LVector3(0.0, 0.0, 0.0)
                self.actor.loop("quieto", partName="brazo.R")
                self.actor.loop("quieto", partName="torso")
                self.actor.loop("quieto", partName="pelvis")
            elif estado_nuevo==Hombre.EstadoCaminando:
                self.actor.loop("caminar", partName="brazo.R")
                self.actor.loop("caminar", partName="torso")
                self.actor.loop("caminar", partName="pelvis")
            elif estado_nuevo==Hombre.EstadoCorriendo:
                self.actor.setPlayRate(1.5, "correr")
                self.actor.loop("correr", partName="brazo.R")
                self.actor.loop("correr", partName="torso")
                self.actor.loop("correr", partName="pelvis")
            elif estado_nuevo==Hombre.EstadoConduciendo:
                self.actor.pose("ride", 0)
        # capa 1
        elif idx_capa==1:
            pass    
        #

    def _cambio_params(self, params_previos, params_nuevos):
#        log.info("%s: cambio de parámetros de estados de %s a %s"%(self.clase, str(bin(params_previos)), str(bin(params_nuevos))))
        # detener giro
        if params_previos & Hombre.ParamEstadoGirando and not params_nuevos & Hombre.ParamEstadoGirando:
            self._velocidad_angular=LVector3(0.0, 0.0, 0.0)

    def _procesar_estados(self, dt):
        # capa 0
        # caminando,corriendo
        if self._estado_capa[0]==Hombre.EstadoCaminando or self._estado_capa[0]==Hombre.EstadoCorriendo:
            param=self._params_estado
            rapidez=self.rapidez_caminar if self._estado_capa[0]==Hombre.EstadoCaminando else self.rapidez_correr
            signo_x=-1.0 if param & Hombre.ParamEstadoDerecha else 1.0
            signo_y=-1.0 if param & Hombre.ParamEstadoAdelante else 1.0
            self._velocidad_lineal=LVector3()
            if param & Hombre.ParamEstadoIzquierda or param & Hombre.ParamEstadoDerecha:
                self._velocidad_lineal.setX(rapidez * signo_x)
            if param & Hombre.ParamEstadoAdelante or param & Hombre.ParamEstadoAtras:
                self._velocidad_lineal.setY(rapidez * signo_y)
            if param & Hombre.ParamEstadoGirando:
                self._velocidad_angular=LVector3(0.0, 0.0, 60.0 * rapidez * signo_x)
            self.cuerpo.setZ(self.altitud_suelo+self._ajuste_altura)
        # saltando
        elif self._estado_capa[0]==Hombre.EstadoSaltando:
            self._velocidad_lineal.setZ(5.0)
            self._velocidad_angular=LVector3(0.0, 0.0, 0.0)
        # cayendo
        elif self._estado_capa[0]==Hombre.EstadoCayendo:
            delta_velocidad_lineal=LVector3(0.0, 0.0, -9.81) * dt
            self._velocidad_lineal+=delta_velocidad_lineal
            prox_delta_h=abs(delta_velocidad_lineal.getZ()*dt)
            if delta_velocidad_lineal.getZ()<0.0 and self._altura<=prox_delta_h: # si cayendo y cerca del suelo
                self.cuerpo.setZ(self.altitud_suelo+self._ajuste_altura)
                self._velocidad_lineal.setZ(0.0)            
        #
        # mover, si no está quieto
        if self._estado_capa[0]!=Hombre.EstadoQuieto:
            self.cuerpo.setPos(self.cuerpo, self._velocidad_lineal * dt)
            self.cuerpo.setH(self.cuerpo, self._velocidad_angular.getZ() * dt)
        #

    def _procesar_contactos(self):
        # evaluar contactos actuales
        test_contactos=self.bullet_world.contactTest(self.cuerpo.node())
        # si no hay, vaciar lista y ejecutar eventos pertinentes
        if test_contactos.getNumContacts()==0:
            if self.contactos:
                for contacto in self.contactos:
                    self._contacto_finalizado(contacto)
                self.contactos=None
            return
        # obtener contactos
        contactos_actuales=test_contactos.getContacts()
        # crear lista interna de contactos
        if not self.contactos:
            self.contactos=list()
        # recopilar contactos nuevos (ineficiente?)
        contactos_nuevos=list()
        for contacto_actual in contactos_actuales:
            encontrado=False
            for contacto in self.contactos:
                if contacto.getNode1()==contacto_actual.getNode1():
                    encontrado=True
                    break
            if not encontrado:
                contactos_nuevos.append(contacto_actual)
        # listar contactos perdidos
        contactos_perdidos=list()
        for contacto in self.contactos:
            encontrado=False
            for contacto_actual in contactos_actuales:
                if contacto_actual.getNode1()==contacto.getNode1():
                    encontrado=True
                    break
            if not encontrado:
                contactos_perdidos.append(contacto)
        # actualizar lista interna de contactos
        self.contactos=contactos_actuales
        # ejecutar eventos
        for contacto in contactos_nuevos:
            self._contacto_iniciado(contacto)
        for contacto in contactos_perdidos:
            self._contacto_finalizado(contacto)
        # garantizar inter-impenetrabilidad
        for contacto in contactos_actuales:
            nodo=contacto.getNode1()
            if not nodo.isStatic():
                continue
            punto=contacto.getManifoldPoint()
            normal=punto.getPositionWorldOnB()-punto.getPositionWorldOnA()
            colisiones=Vec3()
            dist=punto.getDistance()
            if dist<0:
                colisiones-=normal*dist
            colisiones.setZ(0)
            self.cuerpo.setPos(self.cuerpo.getPos()+colisiones)            

    def _contacto_iniciado(self, contacto):
        log.debug("_contacto_iniciado %s %s"%(self.clase, contacto.getNode1().getName()))
    
    def _contacto_finalizado(self, contacto):
        log.debug("_contacto_finalizado %s %s"%(self.clase, contacto.getNode1().getName()))

    def _agarrar(self):
        if not Hombre.EstadoAgarrando in self.objetos_estados:
            nodo_objeto=NodePath(self.contactos[0].getNode1())
            if nodo_objeto.getName().endswith("_nave"):
                log.debug("_agarrar %s"%(nodo_objeto.getName()))
                self.objetos_estados[Hombre.EstadoAgarrando]=nodo_objeto
                return True
        return False
    
    def _soltar(self):
        if Hombre.EstadoAgarrando in self.objetos_estados:
            nodo_objeto=self.objetos_estados[Hombre.EstadoAgarrando]
            if nodo_objeto.getName().endswith("_nave"):
                log.debug("_soltar %s"%(nodo_objeto.getName()))
                del self.objetos_estados[Hombre.EstadoAgarrando]
                self.cuerpo.reparentTo(nodo_objeto.getParent())
                self.cuerpo.setPos(nodo_objeto.getX(), nodo_objeto.getY(), self.altitud_suelo)
                self.cuerpo.setHpr(nodo_objeto.getHpr())
                return True
        return False
