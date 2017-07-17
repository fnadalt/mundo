#version 120

uniform sampler2D p3d_Texture0;
uniform sampler2D p3d_Texture1;

varying vec4 vpos;

void main()
{
    vec2 xy_pos=vpos.xy;
    vec2 ndc= (xy_pos/vpos.w)/2.0+0.5;
    vec2 tc=vec2(ndc.x,1.0-ndc.y);
    vec4 color_reflection=texture2D(p3d_Texture0, tc);
    vec4 color_refraction=texture2D(p3d_Texture1, ndc);
    vec4 color=mix(color_reflection,color_refraction,0.8);
    color+=vec4(0.0,0.1,0.3,0.0);
    //color.a=0.7;
    gl_FragColor=color;
}
