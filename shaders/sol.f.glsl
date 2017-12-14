#version 120

uniform sampler2D p3d_Texture0;

varying vec4 wpos;
varying vec4 vpos;

void main()
{
    if(vpos.z<200.0){
        gl_FragColor=vec4(0,0,0,1);
    } else {
        vec4 color=texture2D(p3d_Texture0, gl_TexCoord[0].st);
        gl_FragColor=color;//*2*(color.a - 0.5);
    }
}
