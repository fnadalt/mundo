#version 120

uniform sampler2D p3d_Texture0;

uniform vec4 water_clipping;
uniform vec3 sun_wpos;

varying vec4 wpos;

void main()
{
    if(distance(sun_wpos,wpos.xyz)>20.0){
        gl_FragColor=vec4(0,0,0,1);
    } else {
        if((water_clipping.z>0 && wpos.z<water_clipping.w) || water_clipping.z<0){
            discard;
        } else {
            vec4 color=texture2D(p3d_Texture0, gl_TexCoord[0].st);
            gl_FragColor=color;//*2*(color.a - 0.5);
        }
    }

}
