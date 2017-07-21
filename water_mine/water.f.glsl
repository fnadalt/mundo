#version 120

uniform sampler2D p3d_Texture0;
uniform sampler2D p3d_Texture1;
uniform sampler2D p3d_Texture2;

varying vec4 vpos;
varying vec2 texcoords;

void main()
{
    //
    vec2 xy_pos=vpos.xy;
    vec2 ndc= (xy_pos/vpos.w)/2.0+0.5;
    vec2 tc=vec2(ndc.x,1.0-ndc.y);

    //
    vec2 distortion1=(texture2D(p3d_Texture2,texcoords)).rg * 2.0 - 1.0;
    distortion1*=0.02;
    ndc+=distortion1;
    ndc=clamp(ndc,0.001,0.999);
    tc+=distortion1;
    tc.x=clamp(tc.x,0.001,0.999);
    tc.y=clamp(tc.y,-0.999,-0.001);

    //
    vec4 color_reflection=texture2D(p3d_Texture0, tc);
    vec4 color_refraction=texture2D(p3d_Texture1, ndc);
    
    //
    vec4 color=mix(color_reflection,color_refraction,0.7);
    //color+=vec4(0.0,0.1,0.3,0.0);
    
    //
    gl_FragColor=color;
    //gl_FragColor=color_dudv;
}
