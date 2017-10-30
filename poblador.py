class PobladorTerreno:

    def __init__(self, base, height_map_seed):
        # referencias:
        self.base=base
        # componentes:
        self.nodo=self.base.render.attachNewNode("poblador_terreno")
        # variables externas:
        self.cantidad_parcelas_expandir=2
        self.nivel_agua=-25
        self.altura_arena=0.44
        self.altura_tierra_baja=0.48
        self.altura_pasto=0.55
        self.altura_tierra_alta=0.63
        self.altura_nieve=0.70
        # variables internas:
        self._height_map_seed=height_map_seed
        self._idx_pos_parcela_actual=(0, 0)
        self._nodos=dict() # {idx_pos:nodo, ...}
    
    def update(self, idx_pos_parcela):
        if idx_pos_parcela!=self._idx_pos_parcela_actual:
            self._idx_pos_parcela_actual=idx_pos_parcela

    def _poblar_parcela(self, idx_pos):
        pass
