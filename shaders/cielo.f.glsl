#version 120

varying vec4 vpos;

void main()
{
    vec4 color_base=vec4(0.7,0.9,1,1);
    vec4 color_sol=vec4(1,1,0,1);
    vec4 color_noche=vec4(0.025,0.025,0.4,1.0);
    
    float distancia_centro_sol=1.0;
    if(vpos.x>0.0) distancia_centro_sol=clamp(length(vpos.yz),0.0,1.0);
    
    vec4 color_final=mix(color_sol,color_base,distancia_centro_sol);
    color_final*=mix(color_noche,color_base,(vpos.x+1.0)/2.0);
    
    color_final.a=1.0;
    gl_FragColor=color_final;
}
